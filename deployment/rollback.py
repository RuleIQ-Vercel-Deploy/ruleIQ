"""
Automatic Rollback System for RuleIQ

Monitors key metrics and triggers automatic rollback when thresholds
are exceeded, ensuring <5 minute recovery time.
"""

from __future__ import annotations

import asyncio
import subprocess
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
import os

logger = logging.getLogger(__name__)


class DeploymentState(str, Enum):
    """Deployment state enumeration."""
    STABLE = "stable"
    DEPLOYING = "deploying"
    MONITORING = "monitoring"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class RollbackReason(str, Enum):
    """Reasons for triggering rollback."""
    HIGH_ERROR_RATE = "high_error_rate"
    SLOW_RESPONSE = "slow_response"
    DB_CONNECTION_FAILURE = "db_connection_failure"
    REDIS_FAILURE = "redis_failure"
    AUTH_SPIKE = "auth_spike"
    AI_COST_EXCEEDED = "ai_cost_exceeded"
    MANUAL_TRIGGER = "manual_trigger"
    HEALTH_CHECK_FAILED = "health_check_failed"


@dataclass
class MetricThreshold:
    """Threshold configuration for a metric."""
    name: str
    current_value: float = 0.0
    threshold_value: float = 0.0
    duration_seconds: int = 60
    exceeded_at: Optional[datetime] = None

    def check_threshold(self, value: float) -> bool:
        """Check if threshold is exceeded."""
        self.current_value = value

        if value > self.threshold_value:
            if self.exceeded_at is None:
                self.exceeded_at = datetime.now(timezone.utc)

            # Check if duration requirement is met
            duration = (datetime.now(timezone.utc) - self.exceeded_at).total_seconds()
            return duration >= self.duration_seconds
        else:
            self.exceeded_at = None
            return False


@dataclass
class DeploymentVersion:
    """Deployment version information."""
    version: str
    deployed_at: datetime
    commit_hash: str
    docker_image: str
    config_snapshot: Dict[str, Any] = field(default_factory=dict)
    metrics_baseline: Dict[str, float] = field(default_factory=dict)


class AutomaticRollbackSystem:
    """
    Monitors deployments and triggers automatic rollback when issues are detected.
    Ensures <5 minute recovery time with blue-green deployment switching.
    """

    def __init__(self):
        self.state = DeploymentState.STABLE
        self.current_version: Optional[DeploymentVersion] = None
        self.previous_version: Optional[DeploymentVersion] = None
        self.rollback_history: List[Dict[str, Any]] = []
        
        # Health check configuration
        self.healthcheck_base_url = os.environ.get('HEALTHCHECK_URL', 'http://localhost:8000')
        self.healthcheck_endpoint = os.environ.get('HEALTHCHECK_ENDPOINT', '/health')
        self.green_healthcheck_url = os.environ.get('GREEN_HEALTHCHECK_URL', 'http://localhost:8001')
        self.blue_healthcheck_url = os.environ.get('BLUE_HEALTHCHECK_URL', 'http://localhost:8000')

        # Metric thresholds
        self.thresholds = {
            "error_rate": MetricThreshold(
                name="error_rate",
                threshold_value=0.05,  # 5%
                duration_seconds=60
            ),
            "response_time": MetricThreshold(
                name="response_time",
                threshold_value=2.0,  # 2x baseline
                duration_seconds=120
            ),
            "db_connections": MetricThreshold(
                name="db_connections",
                threshold_value=0.8,  # 80% utilization
                duration_seconds=60
            ),
            "auth_failures": MetricThreshold(
                name="auth_failures",
                threshold_value=100,  # 100 failures per minute
                duration_seconds=60
            ),
            "ai_cost_rate": MetricThreshold(
                name="ai_cost_rate",
                threshold_value=10.0,  # $10 per minute
                duration_seconds=60
            )
        }

        self.monitoring_interval = 10  # seconds
        self.monitoring_task: Optional[asyncio.Task] = None
        self.rollback_in_progress = False

    async def deploy_new_version(
        self,
        version: str,
        commit_hash: str,
        docker_image: str
    ) -> bool:
        """Deploy a new version with monitoring."""
        if self.state == DeploymentState.ROLLING_BACK:
            logger.error("Cannot deploy during rollback")
            return False

        logger.info(f"Starting deployment of version {version}")
        self.state = DeploymentState.DEPLOYING

        try:
            # Save current version as previous
            if self.current_version:
                self.previous_version = self.current_version

            # Capture baseline metrics
            baseline = await self._capture_baseline_metrics()

            # Create new version
            self.current_version = DeploymentVersion(
                version=version,
                deployed_at=datetime.now(timezone.utc),
                commit_hash=commit_hash,
                docker_image=docker_image,
                config_snapshot=await self._capture_config(),
                metrics_baseline=baseline
            )

            # Backup sessions before deployment
            from services.session_manager import get_session_manager
            session_manager = await get_session_manager()
            await session_manager.backup_all_sessions()

            # Perform blue-green switch
            success = await self._blue_green_deploy(docker_image)

            if success:
                self.state = DeploymentState.MONITORING
                # Start monitoring
                if self.monitoring_task:
                    self.monitoring_task.cancel()
                self.monitoring_task = asyncio.create_task(self._monitor_deployment())

                logger.info(f"Deployment of version {version} successful, monitoring started")
                return True
            else:
                logger.error(f"Deployment of version {version} failed")
                self.state = DeploymentState.STABLE
                return False

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self.state = DeploymentState.STABLE
            return False

    async def _blue_green_deploy(self, docker_image: str) -> bool:
        """Perform blue-green deployment switch."""
        try:
            # Determine deployment mode from environment
            deployment_mode = os.environ.get('DEPLOYMENT_MODE', 'blue-green')
            
            if deployment_mode == 'single-stack':
                return await self._single_stack_deploy(docker_image)
            
            # Default blue-green deployment using existing compose files
            compose_file = "docker-compose.prod.yml"
            if not os.path.exists(compose_file):
                compose_file = "docker-compose.yml"
                if not os.path.exists(compose_file):
                    logger.error("No compose file found for deployment")
                    return False

            backup_file = "docker-compose.backup.yml"
            override_file = "docker-compose.override.yml"

            # Backup current compose file
            subprocess.run(["cp", compose_file, backup_file], check=True)

            # Create override file with new image using labeled approach
            override_content = f"""version: '3.8'
services:
  app:
    image: {docker_image}
    labels:
      - "deployment=green"
  celery_worker:
    image: {docker_image}
    labels:
      - "deployment=green"
  celery_beat:
    image: {docker_image}
    labels:
      - "deployment=green"
"""
            with open(override_file, 'w') as f:
                f.write(override_content)

            try:
                # Deploy new version using docker compose (not docker-compose)
                subprocess.run([
                    "docker", "compose",
                    "-f", compose_file,
                    "-f", override_file,
                    "up", "-d", "--no-deps",
                    "app", "celery_worker", "celery_beat"
                ], check=True)

                # Wait for health check with readiness probe
                await self._wait_for_readiness(self.green_healthcheck_url)

                # Check if green is healthy
                if await self._check_green_health():
                    # Reload nginx configuration if service exists
                    if self._service_exists_in_compose("nginx", compose_file):
                        subprocess.run([
                            "docker", "compose",
                            "-f", compose_file,
                            "exec", "-T", "nginx",
                            "nginx", "-s", "reload"
                        ], check=True)
                        logger.info("NGINX configuration reloaded")

                    logger.info("Blue-green deployment successful")
                    return True
                else:
                    # Green unhealthy, rollback to previous state
                    logger.warning("New deployment unhealthy, rolling back")
                    subprocess.run([
                        "docker", "compose",
                        "-f", backup_file,
                        "up", "-d", "--no-deps",
                        "app", "celery_worker", "celery_beat"
                    ], check=True)
                    return False
            finally:
                # Clean up override file
                if os.path.exists(override_file):
                    os.remove(override_file)

        except subprocess.CalledProcessError as e:
            logger.error(f"Blue-green deployment failed: {e}")
            # Attempt cleanup
            if 'override_file' in locals() and os.path.exists(override_file):
                os.remove(override_file)
            return False
        except Exception as e:
            logger.error(f"Unexpected error during deployment: {e}")
            return False

    def _service_exists_in_compose(self, service_name: str, compose_file: str) -> bool:
        """Check if a service exists in docker-compose file."""
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", compose_file, "config", "--services"],
                capture_output=True,
                text=True,
                check=True
            )
            services = result.stdout.strip().split('\n')
            return service_name in services
        except subprocess.CalledProcessError:
            return False

    async def _single_stack_deploy(self, docker_image: str) -> bool:
        """Perform single-stack deployment with rolling update."""
        try:
            compose_file = os.environ.get('COMPOSE_FILE', 'docker-compose.prod.yml')
            if not os.path.exists(compose_file):
                compose_file = 'docker-compose.yml'
                if not os.path.exists(compose_file):
                    logger.error("No compose file found for single-stack deployment")
                    return False

            # Create temporary override file instead of modifying original
            override_file = "docker-compose.deploy.yml"
            override_content = f"""version: '3.8'
services:
  app:
    image: {docker_image}
  celery_worker:
    image: {docker_image}
  celery_beat:
    image: {docker_image}
"""
            with open(override_file, 'w') as f:
                f.write(override_content)

            try:
                # Perform rolling update using docker compose
                subprocess.run([
                    "docker", "compose",
                    "-f", compose_file,
                    "-f", override_file,
                    "up", "-d", "--no-deps", "app"
                ], check=True)
            finally:
                # Clean up override file
                if os.path.exists(override_file):
                    os.remove(override_file)
            
            # Wait for readiness
            await self._wait_for_readiness(self.healthcheck_base_url)
            
            # Verify health
            return await self._check_health(self.healthcheck_base_url)
            
        except Exception as e:
            logger.error(f"Single-stack deployment failed: {e}")
            return False
    
    async def _wait_for_readiness(self, base_url: str, max_wait: int = 60) -> bool:
        """Wait for service to be ready with exponential backoff."""
        import aiohttp
        
        readiness_endpoint = os.environ.get('READINESS_ENDPOINT', self.healthcheck_endpoint)
        readiness_url = f"{base_url}{readiness_endpoint}"
        
        logger.info(f"Waiting for service readiness at: {readiness_url}")
        
        wait_time = 2
        total_waited = 0
        
        while total_waited < max_wait:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(readiness_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            logger.info(f"Service is ready after {total_waited} seconds")
                            return True
            except Exception as e:
                logger.debug(f"Readiness check failed: {e}")
            
            await asyncio.sleep(wait_time)
            total_waited += wait_time
            wait_time = min(wait_time * 1.5, 10)  # Exponential backoff with cap
        
        logger.error(f"Service failed to become ready after {max_wait} seconds")
        return False
    
    async def _check_health(self, base_url: str) -> bool:
        """Generic health check for any deployment."""
        import aiohttp
        
        health_url = f"{base_url}{self.healthcheck_endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed at {health_url}: {e}")
            return False

    async def _check_green_health(self) -> bool:
        """Check health of green deployment."""
        import aiohttp

        health_url = f"{self.green_healthcheck_url}{self.healthcheck_endpoint}"
        logger.info(f"Checking green deployment health at: {health_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Green health check failed: {e}")
            return False

    async def _check_nginx_upstream_health(self, upstream_name: str = "app") -> bool:
        """Check NGINX upstream health status."""
        nginx_status_url = os.environ.get('NGINX_STATUS_URL')
        
        if not nginx_status_url:
            return True  # Skip if not configured
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{nginx_status_url}/upstream/{upstream_name}") as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if majority of upstreams are healthy
                        healthy = sum(1 for u in data.get('peers', []) if u.get('state') == 'up')
                        total = len(data.get('peers', []))
                        return healthy > total / 2
            return True
        except Exception as e:
            logger.warning(f"NGINX upstream health check failed: {e}")
            return True  # Don't block on NGINX checks

    async def trigger_rollback(self, reason: RollbackReason) -> bool:
        """Trigger automatic rollback to previous version."""
        if self.rollback_in_progress:
            logger.warning("Rollback already in progress")
            return False

        if not self.previous_version:
            logger.error("No previous version available for rollback")
            return False

        logger.critical(f"TRIGGERING ROLLBACK: {reason.value}")
        self.rollback_in_progress = True
        self.state = DeploymentState.ROLLBACK_TRIGGERED

        rollback_start = datetime.now(timezone.utc)

        try:
            # Record rollback event
            self.rollback_history.append({
                "triggered_at": rollback_start,
                "reason": reason.value,
                "from_version": self.current_version.version,
                "to_version": self.previous_version.version
            })

            # Stop monitoring
            if self.monitoring_task:
                self.monitoring_task.cancel()

            self.state = DeploymentState.ROLLING_BACK

            # Perform rollback
            success = await self._perform_rollback()

            rollback_duration = (datetime.now(timezone.utc) - rollback_start).total_seconds()

            if success:
                self.state = DeploymentState.ROLLED_BACK
                logger.info(f"Rollback completed in {rollback_duration:.2f} seconds")

                # Restore sessions
                from services.session_manager import get_session_manager
                session_manager = await get_session_manager()
                await session_manager.restore_all_sessions()

                # Swap versions
                self.current_version = self.previous_version
                self.previous_version = None

                # Alert team
                await self._send_rollback_alert(reason, rollback_duration)

                return True
            else:
                logger.error(f"Rollback failed after {rollback_duration:.2f} seconds")
                return False

        finally:
            self.rollback_in_progress = False

    async def _perform_rollback(self) -> bool:
        """Perform the actual rollback."""
        try:
            backup_file = "docker-compose.backup.yml"
            compose_file = "docker-compose.prod.yml"

            # Check if backup file exists
            if not os.path.exists(backup_file):
                logger.warning("No backup file available for rollback")
                # Try to use the main compose file if no backup exists
                if not os.path.exists(compose_file):
                    compose_file = "docker-compose.yml"
                    if not os.path.exists(compose_file):
                        logger.error("No compose files available for rollback")
                        return False
                backup_file = compose_file

            # Quick switch using docker compose (not docker-compose)
            subprocess.run([
                "docker", "compose",
                "-f", backup_file,
                "up", "-d", "--force-recreate",
                "app", "celery_worker", "celery_beat"
            ], check=True, timeout=60)

            # Restore database if needed
            if await self._needs_db_rollback():
                await self._rollback_database()

            # Clear caches
            await self._clear_caches()

            # Verify rollback
            await asyncio.sleep(5)
            return await self._verify_rollback()

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    async def _needs_db_rollback(self) -> bool:
        """Check if database rollback is needed by comparing Alembic versions."""
        try:
            from database.db_setup import get_async_db
            async for db in get_async_db():
                # Get current alembic version
                result = await db.execute(
                    "SELECT version_num FROM alembic_version LIMIT 1"
                )
                current_version = result.scalar()
                
                # Compare with previous snapshot version
                previous_version = self.previous_version.config_snapshot.get("db_version")
                
                # If versions differ, we need to rollback
                if current_version and previous_version and current_version != previous_version:
                    logger.info(f"Database rollback needed: current={current_version}, target={previous_version}")
                    return True
                return False
        except Exception as e:
            logger.warning(f"Failed to check if database rollback needed: {e}")
            return False

    async def _rollback_database(self):
        """Rollback database migrations using Alembic."""
        try:
            target_version = self.previous_version.config_snapshot.get("db_version")
            
            if not target_version or target_version == "unknown":
                logger.warning("No valid target version for database rollback")
                return
            
            # Use alembic downgrade to target version
            # Note: target_version should be the Alembic revision ID
            result = subprocess.run([
                "alembic", "downgrade", target_version
            ], check=True, capture_output=True, text=True, timeout=30)
            
            logger.info(f"Database rolled back to version {target_version}")
            if result.stdout:
                logger.debug(f"Alembic output: {result.stdout}")
                
        except subprocess.TimeoutExpired:
            logger.error("Database rollback timed out after 30 seconds")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Database rollback failed: {e}")
            if e.stderr:
                logger.error(f"Alembic error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database rollback: {e}")
            raise

    async def _rollback_database_with_api(self):
        """Alternative: Rollback database using Alembic API directly."""
        try:
            from alembic import command
            from alembic.config import Config
            
            target_version = self.previous_version.config_snapshot.get("db_version")
            
            if not target_version or target_version == "unknown":
                logger.warning("No valid target version for database rollback")
                return
            
            # Load Alembic configuration
            alembic_cfg = Config("alembic.ini")
            
            # Set database URL from environment if needed
            from database.db_setup import get_database_url
            alembic_cfg.set_main_option("sqlalchemy.url", get_database_url())
            
            # Perform the downgrade using Alembic API
            command.downgrade(alembic_cfg, target_version)
            
            logger.info(f"Database rolled back to version {target_version} using Alembic API")
            
        except Exception as e:
            logger.error(f"Database rollback via API failed: {e}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Database rollback failed: {e}")
            if e.stderr:
                logger.error(f"Alembic error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database rollback: {e}")
            raise

    async def _clear_caches(self):
        """Clear all caches after rollback."""
        try:
            from config.cache import get_cache_manager
            cache = await get_cache_manager()
            
            if cache.redis_client:
                # Clear Redis cache if available
                await cache.redis_client.flushdb()
                logger.info("Redis cache cleared successfully")
            else:
                # Clear in-memory cache
                cache.memory_cache.clear()
                logger.info("In-memory cache cleared successfully")
                
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            # Continue rollback even if cache clear fails

    async def _verify_rollback(self) -> bool:
        """Verify rollback was successful."""
        try:
            # Check health endpoint
            import aiohttp
            health_url = f"{self.healthcheck_base_url}{self.healthcheck_endpoint}"
            logger.info(f"Verifying rollback health at: {health_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"Health check returned status: {response.status}")
                        return False

            # Check key metrics are back to normal
            metrics = await self._get_current_metrics()
            error_rate = metrics.get("error_rate", 1.0)

            return error_rate < 0.05  # Below 5% error rate

        except Exception as e:
            logger.error(f"Rollback verification failed: {e}")
            return False

    async def _monitor_deployment(self):
        """Monitor deployment and trigger rollback if needed."""
        monitoring_start = datetime.now(timezone.utc)
        monitoring_duration = 300  # 5 minutes of monitoring

        while self.state == DeploymentState.MONITORING:
            try:
                # Get current metrics
                metrics = await self._get_current_metrics()

                # Check thresholds
                for name, threshold in self.thresholds.items():
                    value = metrics.get(name, 0)

                    # Adjust for baseline (2x check for response time)
                    if name == "response_time" and self.current_version:
                        baseline = self.current_version.metrics_baseline.get(name, value/2)
                        value = value / baseline if baseline > 0 else 1.0

                    if threshold.check_threshold(value):
                        # Threshold exceeded, trigger rollback
                        reason_map = {
                            "error_rate": RollbackReason.HIGH_ERROR_RATE,
                            "response_time": RollbackReason.SLOW_RESPONSE,
                            "db_connections": RollbackReason.DB_CONNECTION_FAILURE,
                            "auth_failures": RollbackReason.AUTH_SPIKE,
                            "ai_cost_rate": RollbackReason.AI_COST_EXCEEDED
                        }

                        await self.trigger_rollback(reason_map.get(name, RollbackReason.HEALTH_CHECK_FAILED))
                        return

                # Check if monitoring period is over
                elapsed = (datetime.now(timezone.utc) - monitoring_start).total_seconds()
                if elapsed > monitoring_duration:
                    self.state = DeploymentState.STABLE
                    logger.info("Deployment monitoring completed successfully")
                    return

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        from monitoring.metrics import get_metrics_collector
        collector = get_metrics_collector()

        # In production, you'd parse Prometheus metrics
        # For now, return mock metrics
        return {
            "error_rate": 0.02,  # 2% error rate
            "response_time": 0.5,  # 500ms
            "db_connections": 0.6,  # 60% utilization
            "auth_failures": 10,  # 10 failures per minute
            "ai_cost_rate": 1.5  # $1.50 per minute
        }

    async def _capture_baseline_metrics(self) -> Dict[str, float]:
        """Capture baseline metrics before deployment."""
        return await self._get_current_metrics()

    async def _capture_config(self) -> Dict[str, Any]:
        """Capture current configuration."""
        return {
            "db_version": await self._get_db_version(),
            "feature_flags": await self._get_feature_flags(),
            "env_vars": self._get_safe_env_vars()
        }

    async def _get_db_version(self) -> str:
        """Get current database version from Alembic."""
        try:
            from database.db_setup import get_async_db
            async for db in get_async_db():
                # Query the alembic_version table for current migration version
                result = await db.execute(
                    "SELECT version_num FROM alembic_version LIMIT 1"
                )
                return result.scalar() or "unknown"
        except Exception as e:
            logger.warning(f"Failed to get database version: {e}")
            return "unknown"

    def _get_db_version_with_api(self) -> str:
        """Alternative: Get current database version using Alembic API."""
        try:
            from alembic import command
            from alembic.config import Config
            from alembic.script import ScriptDirectory
            from alembic.runtime.migration import MigrationContext
            from sqlalchemy import create_engine
            
            # Load Alembic configuration
            alembic_cfg = Config("alembic.ini")
            
            # Get database URL
            from database.db_setup import get_database_url
            database_url = get_database_url()
            
            # Create engine and get current revision
            engine = create_engine(database_url)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                return current_rev or "unknown"
                
        except Exception as e:
            logger.warning(f"Failed to get database version via API: {e}")
            return "unknown"

    async def _get_feature_flags(self) -> Dict[str, bool]:
        """Get current feature flag states."""
        from config.feature_flags import feature_flags
        return feature_flags.get_all_flags()

    def _get_safe_env_vars(self) -> Dict[str, str]:
        """Get safe environment variables (no secrets)."""
        safe_vars = [
            "ENVIRONMENT", "APP_VERSION", "LOG_LEVEL",
            "DATABASE_POOL_SIZE", "REDIS_MAX_CONNECTIONS"
        ]
        return {k: os.environ.get(k, "") for k in safe_vars}

    async def _send_rollback_alert(self, reason: RollbackReason, duration: float):
        """Send alert about rollback."""
        alert = {
            "type": "ROLLBACK_COMPLETED",
            "reason": reason.value,
            "duration_seconds": duration,
            "from_version": self.rollback_history[-1]["from_version"],
            "to_version": self.rollback_history[-1]["to_version"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # In production, send to PagerDuty, Slack, etc.
        logger.critical(f"ROLLBACK ALERT: {json.dumps(alert, indent=2)}")

    def get_status(self) -> Dict[str, Any]:
        """Get current rollback system status."""
        return {
            "state": self.state.value,
            "current_version": self.current_version.version if self.current_version else None,
            "previous_version": self.previous_version.version if self.previous_version else None,
            "rollback_in_progress": self.rollback_in_progress,
            "rollback_history": self.rollback_history[-5:],  # Last 5 rollbacks
            "thresholds": {
                name: {
                    "current": t.current_value,
                    "threshold": t.threshold_value,
                    "exceeded": t.exceeded_at is not None
                }
                for name, t in self.thresholds.items()
            }
        }


# Global rollback system instance
_rollback_system: Optional[AutomaticRollbackSystem] = None


def get_rollback_system() -> AutomaticRollbackSystem:
    """Get or create the global rollback system."""
    global _rollback_system
    if _rollback_system is None:
        _rollback_system = AutomaticRollbackSystem()
    return _rollback_system
