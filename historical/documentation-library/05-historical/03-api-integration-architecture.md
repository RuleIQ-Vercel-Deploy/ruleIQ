# API Integration Architecture for Enterprise Evidence Collection

## Current State Analysis

### ✅ What We Have (Solid Foundation)
- **Integration Service** (`frontend/lib/api/integrations.service.ts`) - OAuth handling, sync, webhooks
- **Base Integration** (`api/integrations/base/base_integration.py`) - Abstract class with encryption
- **OAuth Configuration** (`api/integrations/oauth_config.py`) - Google & Microsoft OAuth setup
- **Integration Models** - Database models for storing encrypted credentials
- **Integration Router** (`api/routers/integrations.py`) - REST endpoints for integration management

### ❌ What We're Missing (Critical Gaps)
- **Enterprise System APIs** - AWS, Okta, CrowdStrike, Splunk, GitHub, Jira, etc.
- **API Client Libraries** - Standardized clients for each system
- **Evidence Collection APIs** - Specific endpoints for compliance evidence gathering
- **Credential Management** - Enterprise-grade secret storage and rotation
- **Rate Limiting & Throttling** - API quota management per provider
- **Error Handling & Retry Logic** - Resilient API operations
- **Real-time Monitoring** - API health and performance tracking

## Comprehensive API Integration Architecture

### 1. Enterprise API Client Library

```python
# api/clients/base_api_client.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
import hashlib
import json

@dataclass
class APICredentials:
    provider: str
    auth_type: str  # oauth2, api_key, role_assumption, certificate
    credentials: Dict[str, Any]
    expires_at: Optional[datetime] = None
    scopes: List[str] = None

@dataclass
class APIRequest:
    method: str
    endpoint: str
    params: Dict[str, Any] = None
    headers: Dict[str, str] = None
    body: Any = None
    timeout: int = 30
    retry_attempts: int = 3

@dataclass
class APIResponse:
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    request_id: str

class BaseAPIClient(ABC):
    """Base class for all enterprise API clients"""
    
    def __init__(self, credentials: APICredentials):
        self.credentials = credentials
        self.base_url = self.get_base_url()
        self.session = None
        self.rate_limiter = None
        self.circuit_breaker = None
        
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @abstractmethod
    def get_base_url(self) -> str:
        pass
        
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
        
    @abstractmethod
    async def refresh_credentials(self) -> bool:
        pass
        
    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make authenticated API request with retry logic"""
        
        # Ensure authentication
        if not await self.ensure_authenticated():
            raise APIException(f"Authentication failed for {self.provider_name}")
            
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Execute request with circuit breaker
        return await self.circuit_breaker.call(self._execute_request, request)
        
    async def _execute_request(self, request: APIRequest) -> APIResponse:
        """Execute HTTP request with full error handling"""
        
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        start_time = time.time()
        request_id = self._generate_request_id(request)
        
        try:
            # Prepare headers
            headers = await self._prepare_headers(request.headers or {})
            
            # Execute request
            async with self.session.request(
                method=request.method,
                url=f"{self.base_url}{request.endpoint}",
                params=request.params,
                headers=headers,
                json=request.body if request.method != 'GET' else None,
                timeout=aiohttp.ClientTimeout(total=request.timeout)
            ) as response:
                
                response_time = time.time() - start_time
                response_data = await self._parse_response(response)
                
                # Log request/response for audit
                await self._log_api_call(request, response, response_time, request_id)
                
                return APIResponse(
                    status_code=response.status,
                    data=response_data,
                    headers=dict(response.headers),
                    response_time=response_time,
                    request_id=request_id
                )
                
        except asyncio.TimeoutError:
            raise APITimeoutException(f"Request to {self.provider_name} timed out")
        except aiohttp.ClientError as e:
            raise APIConnectionException(f"Connection error to {self.provider_name}: {e}")
        except Exception as e:
            raise APIException(f"Unexpected error calling {self.provider_name}: {e}")
            
    async def collect_evidence(self, evidence_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Collect specific evidence type from this API"""
        evidence_collector = self.get_evidence_collector(evidence_type)
        if not evidence_collector:
            raise UnsupportedEvidenceTypeException(
                f"{evidence_type} not supported by {self.provider_name}"
            )
            
        return await evidence_collector.collect(**kwargs)
        
    @abstractmethod
    def get_evidence_collector(self, evidence_type: str):
        """Get evidence collector for specific evidence type"""
        pass
        
    async def health_check(self) -> Dict[str, Any]:
        """Check API health and connectivity"""
        try:
            start_time = time.time()
            await self.make_request(APIRequest("GET", self.get_health_endpoint()))
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "provider": self.provider_name,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name,
                "timestamp": datetime.utcnow()
            }
            
    @abstractmethod
    def get_health_endpoint(self) -> str:
        """Get provider-specific health check endpoint"""
        pass
```

### 2. AWS API Client Implementation

```python
# api/clients/aws_client.py
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, List, Any
import json

class AWSAPIClient(BaseAPIClient):
    """AWS API client for collecting infrastructure and security evidence"""
    
    @property
    def provider_name(self) -> str:
        return "aws"
        
    def get_base_url(self) -> str:
        return "https://amazonaws.com"  # Not used for boto3
        
    async def authenticate(self) -> bool:
        """Authenticate using AWS credentials (Access Key, Role Assumption, etc.)"""
        try:
            if self.credentials.auth_type == "access_key":
                self.aws_session = boto3.Session(
                    aws_access_key_id=self.credentials.credentials["access_key_id"],
                    aws_secret_access_key=self.credentials.credentials["secret_access_key"],
                    region_name=self.credentials.credentials.get("region", "us-east-1")
                )
            elif self.credentials.auth_type == "role_assumption":
                # Implement STS role assumption
                sts_client = boto3.client('sts')
                response = sts_client.assume_role(
                    RoleArn=self.credentials.credentials["role_arn"],
                    RoleSessionName="ruleiq-evidence-collection",
                    ExternalId=self.credentials.credentials.get("external_id")
                )
                
                credentials = response['Credentials']
                self.aws_session = boto3.Session(
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken'],
                    region_name=self.credentials.credentials.get("region", "us-east-1")
                )
            
            # Test authentication
            sts = self.aws_session.client('sts')
            sts.get_caller_identity()
            return True
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"AWS authentication failed: {e}")
            return False
            
    async def refresh_credentials(self) -> bool:
        """Refresh AWS credentials if using role assumption"""
        if self.credentials.auth_type == "role_assumption":
            return await self.authenticate()
        return True
        
    def get_evidence_collector(self, evidence_type: str):
        """Get AWS evidence collector for specific evidence type"""
        collectors = {
            "iam_policies": AWSIAMEvidenceCollector(self.aws_session),
            "security_groups": AWSSecurityGroupCollector(self.aws_session),
            "vpc_configuration": AWSVPCCollector(self.aws_session),
            "cloudtrail_logs": AWSCloudTrailCollector(self.aws_session),
            "config_rules": AWSConfigCollector(self.aws_session),
            "guardduty_findings": AWSGuardDutyCollector(self.aws_session),
            "inspector_findings": AWSInspectorCollector(self.aws_session),
            "compliance_reports": AWSComplianceCollector(self.aws_session)
        }
        return collectors.get(evidence_type)
        
    def get_health_endpoint(self) -> str:
        return "/health"  # Custom health check method

class AWSIAMEvidenceCollector:
    """Collect IAM-related evidence from AWS"""
    
    def __init__(self, aws_session):
        self.iam = aws_session.client('iam')
        
    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect IAM policies, users, roles, and access patterns"""
        evidence = []
        
        try:
            # Collect IAM policies
            policies_paginator = self.iam.get_paginator('list_policies')
            for page in policies_paginator.paginate(Scope='Local'):
                for policy in page['Policies']:
                    policy_version = self.iam.get_policy_version(
                        PolicyArn=policy['Arn'],
                        VersionId=policy['DefaultVersionId']
                    )
                    
                    evidence.append({
                        "evidence_type": "iam_policy",
                        "resource_id": policy['Arn'],
                        "resource_name": policy['PolicyName'],
                        "policy_document": policy_version['PolicyVersion']['Document'],
                        "created_date": policy['CreateDate'],
                        "last_used": policy.get('LastUsedDate'),
                        "compliance_controls": ["CC6.1", "CC6.2", "CC6.3"],  # SOC 2 controls
                        "collection_timestamp": datetime.utcnow()
                    })
                    
            # Collect IAM users
            users_paginator = self.iam.get_paginator('list_users')
            for page in users_paginator.paginate():
                for user in page['Users']:
                    # Get user policies and groups
                    user_policies = self.iam.list_attached_user_policies(UserName=user['UserName'])
                    user_groups = self.iam.get_groups_for_user(UserName=user['UserName'])
                    
                    evidence.append({
                        "evidence_type": "iam_user",
                        "resource_id": user['Arn'],
                        "resource_name": user['UserName'],
                        "created_date": user['CreateDate'],
                        "last_used": user.get('PasswordLastUsed'),
                        "attached_policies": user_policies['AttachedPolicies'],
                        "groups": user_groups['Groups'],
                        "compliance_controls": ["CC6.1", "CC6.2"],
                        "collection_timestamp": datetime.utcnow()
                    })
                    
            # Collect IAM roles
            roles_paginator = self.iam.get_paginator('list_roles')
            for page in roles_paginator.paginate():
                for role in page['Roles']:
                    role_policies = self.iam.list_attached_role_policies(RoleName=role['RoleName'])
                    
                    evidence.append({
                        "evidence_type": "iam_role",
                        "resource_id": role['Arn'],
                        "resource_name": role['RoleName'],
                        "assume_role_policy": role['AssumeRolePolicyDocument'],
                        "created_date": role['CreateDate'],
                        "last_used": role.get('RoleLastUsed', {}).get('LastUsedDate'),
                        "attached_policies": role_policies['AttachedPolicies'],
                        "compliance_controls": ["CC6.1", "CC6.3"],
                        "collection_timestamp": datetime.utcnow()
                    })
                    
        except ClientError as e:
            logger.error(f"Error collecting IAM evidence: {e}")
            raise AWSAPIException(f"Failed to collect IAM evidence: {e}")
            
        return evidence

class AWSCloudTrailCollector:
    """Collect CloudTrail audit logs for compliance evidence"""
    
    def __init__(self, aws_session):
        self.cloudtrail = aws_session.client('cloudtrail')
        
    async def collect(self, start_time: datetime = None, event_types: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Collect CloudTrail events for audit evidence"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=30)
            
        evidence = []
        
        try:
            # Look up events
            response = self.cloudtrail.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'EventName',
                        'AttributeValue': event_type
                    } for event_type in (event_types or ['iam', 'security', 'access'])
                ],
                StartTime=start_time,
                EndTime=datetime.utcnow()
            )
            
            for event in response['Events']:
                evidence.append({
                    "evidence_type": "audit_log",
                    "event_id": event['EventId'],
                    "event_name": event['EventName'],
                    "event_time": event['EventTime'],
                    "username": event.get('Username'),
                    "user_identity": event.get('UserIdentity'),
                    "source_ip": event.get('SourceIPAddress'),
                    "user_agent": event.get('UserAgent'),
                    "resources": event.get('Resources', []),
                    "cloud_trail_event": event.get('CloudTrailEvent'),
                    "compliance_controls": ["CC6.1", "CC7.2", "CC7.3"],
                    "collection_timestamp": datetime.utcnow()
                })
                
        except ClientError as e:
            logger.error(f"Error collecting CloudTrail evidence: {e}")
            raise AWSAPIException(f"Failed to collect CloudTrail evidence: {e}")
            
        return evidence
```

### 3. Okta API Client Implementation

```python
# api/clients/okta_client.py
import aiohttp
from typing import Dict, List, Any
import base64

class OktaAPIClient(BaseAPIClient):
    """Okta API client for identity and access management evidence"""
    
    @property
    def provider_name(self) -> str:
        return "okta"
        
    def get_base_url(self) -> str:
        domain = self.credentials.credentials["domain"]
        return f"https://{domain}.okta.com/api/v1"
        
    async def authenticate(self) -> bool:
        """Authenticate using Okta API token"""
        try:
            # Test authentication with a simple API call
            headers = await self._prepare_headers()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/me",
                    headers=headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Okta authentication failed: {e}")
            return False
            
    async def refresh_credentials(self) -> bool:
        """Okta API tokens don't typically expire, but we can validate them"""
        return await self.authenticate()
        
    async def _prepare_headers(self, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """Prepare headers with API token"""
        headers = {
            "Authorization": f"SSWS {self.credentials.credentials['api_token']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers
        
    def get_evidence_collector(self, evidence_type: str):
        """Get Okta evidence collector for specific evidence type"""
        collectors = {
            "users": OktaUserCollector(self),
            "groups": OktaGroupCollector(self),
            "applications": OktaApplicationCollector(self),
            "policies": OktaPolicyCollector(self),
            "system_logs": OktaLogsCollector(self),
            "mfa_factors": OktaMFACollector(self)
        }
        return collectors.get(evidence_type)
        
    def get_health_endpoint(self) -> str:
        return "/users/me"

class OktaUserCollector:
    """Collect user and access evidence from Okta"""
    
    def __init__(self, okta_client: OktaAPIClient):
        self.client = okta_client
        
    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect user accounts, status, and access patterns"""
        evidence = []
        
        try:
            # Collect all users
            users_request = APIRequest("GET", "/users", params={"limit": 200})
            response = await self.client.make_request(users_request)
            
            for user in response.data:
                # Get user groups
                groups_request = APIRequest("GET", f"/users/{user['id']}/groups")
                groups_response = await self.client.make_request(groups_request)
                
                # Get user applications
                apps_request = APIRequest("GET", f"/users/{user['id']}/appLinks")
                apps_response = await self.client.make_request(apps_request)
                
                evidence.append({
                    "evidence_type": "identity_user",
                    "user_id": user['id'],
                    "username": user['profile']['login'],
                    "email": user['profile']['email'],
                    "first_name": user['profile']['firstName'],
                    "last_name": user['profile']['lastName'],
                    "status": user['status'],
                    "created": user['created'],
                    "activated": user.get('activated'),
                    "last_login": user.get('lastLogin'),
                    "last_updated": user['lastUpdated'],
                    "groups": [group['profile']['name'] for group in groups_response.data],
                    "applications": [app['label'] for app in apps_response.data],
                    "compliance_controls": ["CC6.1", "CC6.2", "CC6.7"],
                    "collection_timestamp": datetime.utcnow()
                })
                
        except Exception as e:
            logger.error(f"Error collecting Okta user evidence: {e}")
            raise OktaAPIException(f"Failed to collect user evidence: {e}")
            
        return evidence

class OktaLogsCollector:
    """Collect system logs for audit evidence"""
    
    def __init__(self, okta_client: OktaAPIClient):
        self.client = okta_client
        
    async def collect(self, since: datetime = None, event_types: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Collect system logs for audit evidence"""
        if not since:
            since = datetime.utcnow() - timedelta(days=30)
            
        evidence = []
        
        try:
            params = {
                "since": since.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "limit": 1000
            }
            
            if event_types:
                params["filter"] = f"eventType eq \"{event_types[0]}\""
                
            logs_request = APIRequest("GET", "/logs", params=params)
            response = await self.client.make_request(logs_request)
            
            for log_entry in response.data:
                evidence.append({
                    "evidence_type": "audit_log",
                    "event_id": log_entry['uuid'],
                    "event_type": log_entry['eventType'],
                    "event_time": log_entry['published'],
                    "actor": log_entry.get('actor', {}).get('displayName'),
                    "actor_id": log_entry.get('actor', {}).get('id'),
                    "client": log_entry.get('client', {}),
                    "authentication_context": log_entry.get('authenticationContext', {}),
                    "security_context": log_entry.get('securityContext', {}),
                    "target": log_entry.get('target'),
                    "outcome": log_entry.get('outcome', {}).get('result'),
                    "compliance_controls": ["CC6.1", "CC7.2", "CC7.3"],
                    "collection_timestamp": datetime.utcnow()
                })
                
        except Exception as e:
            logger.error(f"Error collecting Okta logs: {e}")
            raise OktaAPIException(f"Failed to collect logs: {e}")
            
        return evidence
```

### 4. GitHub API Client Implementation

```python
# api/clients/github_client.py
import aiohttp
from typing import Dict, List, Any
import base64

class GitHubAPIClient(BaseAPIClient):
    """GitHub API client for development and security evidence"""
    
    @property
    def provider_name(self) -> str:
        return "github"
        
    def get_base_url(self) -> str:
        if self.credentials.credentials.get("enterprise_url"):
            return f"{self.credentials.credentials['enterprise_url']}/api/v3"
        return "https://api.github.com"
        
    async def authenticate(self) -> bool:
        """Authenticate using GitHub personal access token or GitHub App"""
        try:
            headers = await self._prepare_headers()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/user",
                    headers=headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"GitHub authentication failed: {e}")
            return False
            
    async def refresh_credentials(self) -> bool:
        """GitHub tokens don't typically expire, but we can validate them"""
        return await self.authenticate()
        
    async def _prepare_headers(self, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """Prepare headers with authentication"""
        if self.credentials.auth_type == "token":
            headers = {
                "Authorization": f"token {self.credentials.credentials['access_token']}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ruleIQ-compliance-collector"
            }
        elif self.credentials.auth_type == "github_app":
            # Implement GitHub App JWT authentication
            headers = await self._generate_app_headers()
        else:
            raise ValueError(f"Unsupported auth type: {self.credentials.auth_type}")
            
        if additional_headers:
            headers.update(additional_headers)
        return headers
        
    def get_evidence_collector(self, evidence_type: str):
        """Get GitHub evidence collector for specific evidence type"""
        collectors = {
            "repositories": GitHubRepositoryCollector(self),
            "branch_protection": GitHubBranchProtectionCollector(self),
            "security_policies": GitHubSecurityCollector(self),
            "workflow_runs": GitHubWorkflowCollector(self),
            "security_alerts": GitHubSecurityAlertsCollector(self),
            "commit_history": GitHubCommitCollector(self)
        }
        return collectors.get(evidence_type)
        
    def get_health_endpoint(self) -> str:
        return "/user"

class GitHubRepositoryCollector:
    """Collect repository configuration and security evidence"""
    
    def __init__(self, github_client: GitHubAPIClient):
        self.client = github_client
        
    async def collect(self, organization: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Collect repository configurations and security settings"""
        evidence = []
        
        try:
            if organization:
                repos_request = APIRequest("GET", f"/orgs/{organization}/repos", params={"per_page": 100})
            else:
                repos_request = APIRequest("GET", "/user/repos", params={"per_page": 100, "affiliation": "owner,collaborator"})
                
            response = await self.client.make_request(repos_request)
            
            for repo in response.data:
                # Get branch protection rules
                default_branch = repo.get('default_branch', 'main')
                protection_request = APIRequest("GET", f"/repos/{repo['full_name']}/branches/{default_branch}/protection")
                
                try:
                    protection_response = await self.client.make_request(protection_request)
                    branch_protection = protection_response.data
                except:
                    branch_protection = None
                    
                # Get security and analysis settings
                security_request = APIRequest("GET", f"/repos/{repo['full_name']}")
                security_response = await self.client.make_request(security_request)
                
                evidence.append({
                    "evidence_type": "code_repository",
                    "repository_id": repo['id'],
                    "repository_name": repo['name'],
                    "full_name": repo['full_name'],
                    "private": repo['private'],
                    "default_branch": repo['default_branch'],
                    "created_at": repo['created_at'],
                    "updated_at": repo['updated_at'],
                    "pushed_at": repo['pushed_at'],
                    "branch_protection": branch_protection,
                    "security_and_analysis": security_response.data.get('security_and_analysis'),
                    "topics": repo.get('topics', []),
                    "archived": repo['archived'],
                    "disabled": repo['disabled'],
                    "compliance_controls": ["CC8.1", "CC8.2", "CC8.3"],  # Change management controls
                    "collection_timestamp": datetime.utcnow()
                })
                
        except Exception as e:
            logger.error(f"Error collecting GitHub repository evidence: {e}")
            raise GitHubAPIException(f"Failed to collect repository evidence: {e}")
            
        return evidence

class GitHubWorkflowCollector:
    """Collect CI/CD workflow evidence"""
    
    def __init__(self, github_client: GitHubAPIClient):
        self.client = github_client
        
    async def collect(self, repository: str, since: datetime = None, **kwargs) -> List[Dict[str, Any]]:
        """Collect workflow run history for CI/CD evidence"""
        if not since:
            since = datetime.utcnow() - timedelta(days=30)
            
        evidence = []
        
        try:
            # Get workflow runs
            params = {
                "per_page": 100,
                "created": f">={since.strftime('%Y-%m-%d')}"
            }
            
            runs_request = APIRequest("GET", f"/repos/{repository}/actions/runs", params=params)
            response = await self.client.make_request(runs_request)
            
            for run in response.data['workflow_runs']:
                # Get workflow details
                workflow_request = APIRequest("GET", f"/repos/{repository}/actions/workflows/{run['workflow_id']}")
                workflow_response = await self.client.make_request(workflow_request)
                
                evidence.append({
                    "evidence_type": "cicd_execution",
                    "workflow_run_id": run['id'],
                    "workflow_name": workflow_response.data['name'],
                    "repository": repository,
                    "head_branch": run['head_branch'],
                    "head_sha": run['head_sha'],
                    "run_number": run['run_number'],
                    "event": run['event'],
                    "status": run['status'],
                    "conclusion": run['conclusion'],
                    "created_at": run['created_at'],
                    "updated_at": run['updated_at'],
                    "run_started_at": run.get('run_started_at'),
                    "actor": run['actor']['login'],
                    "triggering_actor": run['triggering_actor']['login'],
                    "workflow_path": workflow_response.data['path'],
                    "compliance_controls": ["CC8.1", "CC8.2"],
                    "collection_timestamp": datetime.utcnow()
                })
                
        except Exception as e:
            logger.error(f"Error collecting GitHub workflow evidence: {e}")
            raise GitHubAPIException(f"Failed to collect workflow evidence: {e}")
            
        return evidence
```

### 5. Enterprise API Integration Router

```python
# api/routers/enterprise_integrations.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from api.clients.aws_client import AWSAPIClient
from api.clients.okta_client import OktaAPIClient
from api.clients.github_client import GitHubAPIClient
from api.clients.crowdstrike_client import CrowdStrikeAPIClient
from api.clients.splunk_client import SplunkAPIClient

router = APIRouter(prefix="/enterprise/integrations", tags=["Enterprise API Integrations"])

@router.post("/aws/configure")
async def configure_aws_integration(
    config: AWSIntegrationConfig,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Configure AWS integration with role assumption or access keys"""
    
    try:
        # Create credentials object
        credentials = APICredentials(
            provider="aws",
            auth_type=config.auth_type,  # "access_key" or "role_assumption"
            credentials=config.credentials.dict(),
            scopes=config.scopes
        )
        
        # Test connection
        aws_client = AWSAPIClient(credentials)
        if not await aws_client.authenticate():
            raise HTTPException(status_code=400, detail="AWS authentication failed")
        
        # Store encrypted configuration
        integration_config = await store_integration_config(
            user_id=current_user.id,
            provider="aws",
            credentials=credentials,
            db=db
        )
        
        return {
            "integration_id": integration_config.id,
            "provider": "aws",
            "status": "connected",
            "capabilities": [
                "iam_policies", "security_groups", "vpc_configuration",
                "cloudtrail_logs", "config_rules", "guardduty_findings"
            ],
            "message": "AWS integration configured successfully"
        }
        
    except Exception as e:
        logger.error(f"Error configuring AWS integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/okta/configure")
async def configure_okta_integration(
    config: OktaIntegrationConfig,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Configure Okta integration with API token"""
    
    try:
        credentials = APICredentials(
            provider="okta",
            auth_type="api_token",
            credentials={
                "domain": config.domain,
                "api_token": config.api_token
            }
        )
        
        # Test connection
        okta_client = OktaAPIClient(credentials)
        if not await okta_client.authenticate():
            raise HTTPException(status_code=400, detail="Okta authentication failed")
        
        # Store configuration
        integration_config = await store_integration_config(
            user_id=current_user.id,
            provider="okta",
            credentials=credentials,
            db=db
        )
        
        return {
            "integration_id": integration_config.id,
            "provider": "okta",
            "status": "connected",
            "capabilities": [
                "users", "groups", "applications", "policies",
                "system_logs", "mfa_factors"
            ],
            "message": "Okta integration configured successfully"
        }
        
    except Exception as e:
        logger.error(f"Error configuring Okta integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/github/configure")
async def configure_github_integration(
    config: GitHubIntegrationConfig,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Configure GitHub integration with personal access token or GitHub App"""
    
    try:
        credentials = APICredentials(
            provider="github",
            auth_type=config.auth_type,  # "token" or "github_app"
            credentials=config.credentials.dict()
        )
        
        # Test connection
        github_client = GitHubAPIClient(credentials)
        if not await github_client.authenticate():
            raise HTTPException(status_code=400, detail="GitHub authentication failed")
        
        # Store configuration
        integration_config = await store_integration_config(
            user_id=current_user.id,
            provider="github",
            credentials=credentials,
            db=db
        )
        
        return {
            "integration_id": integration_config.id,
            "provider": "github",
            "status": "connected",
            "capabilities": [
                "repositories", "branch_protection", "security_policies",
                "workflow_runs", "security_alerts", "commit_history"
            ],
            "message": "GitHub integration configured successfully"
        }
        
    except Exception as e:
        logger.error(f"Error configuring GitHub integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collect/foundation")
async def collect_foundation_evidence(
    request: FoundationEvidenceRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Collect foundation evidence from AWS, Okta, and HRIS systems"""
    
    # Validate required integrations are configured
    user_integrations = await get_user_integrations(current_user.id, db)
    integration_map = {i.provider: i for i in user_integrations}
    
    required_integrations = ["aws", "okta"]
    missing_integrations = [
        provider for provider in required_integrations 
        if provider not in integration_map
    ]
    
    if missing_integrations:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required integrations: {missing_integrations}"
        )
    
    # Start evidence collection
    collection_id = str(uuid.uuid4())
    background_tasks.add_task(
        execute_foundation_evidence_collection,
        collection_id=collection_id,
        user_id=current_user.id,
        integration_map=integration_map,
        request=request,
        db=db
    )
    
    return {
        "collection_id": collection_id,
        "status": "initiated",
        "message": "Foundation evidence collection started",
        "estimated_duration": "5-15 minutes",
        "evidence_types": [
            "cloud_infrastructure", "identity_access", "human_resources"
        ]
    }

async def execute_foundation_evidence_collection(
    collection_id: str,
    user_id: str,
    integration_map: Dict[str, Any],
    request: FoundationEvidenceRequest,
    db: AsyncSession
):
    """Background task to collect foundation evidence"""
    
    evidence_results = []
    
    try:
        # Update collection status
        await update_collection_status(collection_id, "in_progress", db)
        
        # Collect AWS evidence
        if "aws" in integration_map:
            aws_credentials = await decrypt_integration_credentials(integration_map["aws"])
            aws_client = AWSAPIClient(aws_credentials)
            
            aws_evidence = await aws_client.collect_evidence("iam_policies")
            aws_evidence.extend(await aws_client.collect_evidence("security_groups"))
            aws_evidence.extend(await aws_client.collect_evidence("cloudtrail_logs"))
            
            evidence_results.extend(aws_evidence)
        
        # Collect Okta evidence
        if "okta" in integration_map:
            okta_credentials = await decrypt_integration_credentials(integration_map["okta"])
            okta_client = OktaAPIClient(okta_credentials)
            
            okta_evidence = await okta_client.collect_evidence("users")
            okta_evidence.extend(await okta_client.collect_evidence("groups"))
            okta_evidence.extend(await okta_client.collect_evidence("system_logs"))
            
            evidence_results.extend(okta_evidence)
        
        # Store evidence results
        await store_evidence_results(collection_id, evidence_results, db)
        await update_collection_status(collection_id, "completed", db)
        
    except Exception as e:
        logger.error(f"Error in foundation evidence collection {collection_id}: {e}")
        await update_collection_status(collection_id, "failed", db, error=str(e))

@router.get("/health")
async def check_integrations_health(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Check health of all configured integrations"""
    
    user_integrations = await get_user_integrations(current_user.id, db)
    health_results = []
    
    for integration in user_integrations:
        try:
            credentials = await decrypt_integration_credentials(integration)
            
            if integration.provider == "aws":
                client = AWSAPIClient(credentials)
            elif integration.provider == "okta":
                client = OktaAPIClient(credentials)
            elif integration.provider == "github":
                client = GitHubAPIClient(credentials)
            else:
                continue
                
            health_result = await client.health_check()
            health_results.append({
                "integration_id": integration.id,
                "provider": integration.provider,
                **health_result
            })
            
        except Exception as e:
            health_results.append({
                "integration_id": integration.id,
                "provider": integration.provider,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow()
            })
    
    overall_status = "healthy" if all(r["status"] == "healthy" for r in health_results) else "degraded"
    
    return {
        "overall_status": overall_status,
        "integrations": health_results,
        "total_integrations": len(health_results),
        "healthy_integrations": len([r for r in health_results if r["status"] == "healthy"])
    }
```

### 6. Complete Integration Implementation Plan

```typescript
// Complete list of API integrations needed

const ENTERPRISE_INTEGRATIONS = {
  // Foundation (Days 1-7)
  foundation: {
    "aws": {
      auth_types: ["access_key", "role_assumption", "sso"],
      evidence_types: ["iam_policies", "security_groups", "vpc_config", "cloudtrail"],
      priority: "critical"
    },
    "azure": {
      auth_types: ["service_principal", "managed_identity"],
      evidence_types: ["rbac", "network_security", "activity_logs"],
      priority: "high"
    },
    "gcp": {
      auth_types: ["service_account", "oauth2"],
      evidence_types: ["iam_policies", "vpc_config", "audit_logs"],
      priority: "high"
    },
    "okta": {
      auth_types: ["api_token", "oauth2"],
      evidence_types: ["users", "groups", "applications", "policies", "logs"],
      priority: "critical"
    },
    "azure_ad": {
      auth_types: ["app_registration", "managed_identity"],
      evidence_types: ["users", "groups", "conditional_access", "sign_in_logs"],
      priority: "high"
    },
    "bamboohr": {
      auth_types: ["api_key"],
      evidence_types: ["employees", "org_chart", "time_off", "training"],
      priority: "medium"
    }
  },
  
  // Security Evidence (Days 8-21)
  security: {
    "crowdstrike": {
      auth_types: ["api_key"],
      evidence_types: ["endpoints", "detections", "policies", "incidents"],
      priority: "critical"
    },
    "sentinelone": {
      auth_types: ["api_token"],
      evidence_types: ["agents", "threats", "policies", "exclusions"],
      priority: "high"
    },
    "qualys": {
      auth_types: ["username_password"],
      evidence_types: ["vulnerabilities", "scans", "assets", "compliance"],
      priority: "high"
    },
    "rapid7": {
      auth_types: ["api_key"],
      evidence_types: ["vulnerabilities", "assets", "scans", "remediation"],
      priority: "medium"
    },
    "splunk": {
      auth_types: ["token", "username_password"],
      evidence_types: ["searches", "alerts", "dashboards", "data_inputs"],
      priority: "critical"
    },
    "microsoft_sentinel": {
      auth_types: ["service_principal"],
      evidence_types: ["incidents", "analytics_rules", "workbooks", "data_connectors"],
      priority: "high"
    }
  },
  
  // Change & SDLC (Days 22-30)
  sdlc: {
    "github": {
      auth_types: ["token", "github_app"],
      evidence_types: ["repositories", "branch_protection", "workflows", "security_alerts"],
      priority: "critical"
    },
    "gitlab": {
      auth_types: ["token", "oauth2"],
      evidence_types: ["projects", "merge_requests", "pipelines", "security_reports"],
      priority: "high"
    },
    "jenkins": {
      auth_types: ["username_password", "api_token"],
      evidence_types: ["jobs", "builds", "plugins", "security_realm"],
      priority: "medium"
    },
    "jira": {
      auth_types: ["basic_auth", "oauth2", "api_token"],
      evidence_types: ["issues", "projects", "workflows", "permissions"],
      priority: "high"
    },
    "servicenow": {
      auth_types: ["basic_auth", "oauth2"],
      evidence_types: ["incidents", "changes", "problems", "cmdb"],
      priority: "medium"
    },
    "hashicorp_vault": {
      auth_types: ["token", "username_password", "aws_iam"],
      evidence_types: ["secrets", "policies", "audit_logs", "leases"],
      priority: "high"
    }
  }
};
```

This comprehensive API integration architecture provides:

1. **Solid Foundation** - Builds on existing integration service
2. **Enterprise APIs** - Native connections to all major enterprise systems
3. **Standardized Clients** - Consistent interface across all providers
4. **Evidence Collection** - Purpose-built for compliance evidence gathering
5. **Security & Monitoring** - Enterprise-grade credential management and health monitoring
6. **MCP Readiness** - Architecture that enables seamless MCP integration

**Ready to start implementing?** We can begin with the highest priority integrations (AWS + Okta) and build from there.