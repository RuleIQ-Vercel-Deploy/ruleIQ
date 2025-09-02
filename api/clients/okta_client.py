"""
Okta API client for identity and access management evidence collection
"""

import aiohttp
from typing import Dict, List
from datetime import datetime, timedelta

from .base_api_client import (
    BaseAPIClient,
    APICredentials,
    APIRequest,
    EvidenceItem,
    BaseEvidenceCollector,
    APIException,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


class OktaAPIException(APIException):
    """Okta-specific API exception"""

    pass


class OktaAPIClient(BaseAPIClient):
    """Okta API client for identity and access management evidence"""

    def __init__(self, credentials: APICredentials) -> None:
        super().__init__(credentials)
        self.domain = credentials.credentials.get("domain")
        if not self.domain:
            raise ValueError("Okta domain is required")

    @property
    def provider_name(self) -> str:
        return "okta"

    def get_base_url(self) -> str:
        return f"https://{self.domain}.okta.com/api/v1"

    async def authenticate(self) -> bool:
        """Authenticate using Okta API token"""
        try:
            # Test authentication with a simple API call
            headers = await self._prepare_headers()

            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(
                f"{self.base_url}/users/me", headers=headers
            ) as response:
                if response.status == 200:
                    user_info = await response.json()
                    logger.info(
                        f"Okta authentication successful for user: {user_info.get('profile', {}).get('login')}"
                    )
                    return True
                elif response.status == 401:
                    logger.error("Okta authentication failed: Invalid API token")
                    return False
                else:
                    logger.error(
                        f"Okta authentication failed with status: {response.status}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Okta authentication failed: {e}")
            return False

    async def refresh_credentials(self) -> bool:
        """Okta API tokens don't typically expire, but we can validate them"""
        return await self.authenticate()

    async def _prepare_headers(
        self, additional_headers: Dict[str, str] = None
    ) -> Dict[str, str]:
        """Prepare headers with API token"""
        headers = {
            "Authorization": f"SSWS {self.credentials.credentials['api_token']}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ruleIQ-compliance-collector/1.0",
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
            "mfa_factors": OktaMFACollector(self),
            "zones": OktaZoneCollector(self),
            "auth_servers": OktaAuthServerCollector(self),
        }
        return collectors.get(evidence_type)

    def get_supported_evidence_types(self) -> List[str]:
        """Get list of supported evidence types for Okta"""
        return [
            "users",
            "groups",
            "applications",
            "policies",
            "system_logs",
            "mfa_factors",
            "zones",
            "auth_servers",
        ]

    def get_health_endpoint(self) -> str:
        return "/users/me"


class OktaUserCollector(BaseEvidenceCollector):
    """Collect user and access evidence from Okta"""

    async def collect(self, **kwargs) -> List[EvidenceItem]:
        """Collect user accounts, status, and access patterns"""
        evidence = []

        try:
            # Collect all users with pagination
            url = "/users"
            params = {"limit": 200}

            while url:
                users_request = APIRequest(
                    "GET", url, params=params if url == "/users" else None
                )
                response = await self.api_client.make_request(users_request)

                for user in response.data:
                    try:
                        # Get user groups
                        groups_request = APIRequest(
                            "GET", f"/users/{user['id']}/groups"
                        )
                        groups_response = await self.api_client.make_request(
                            groups_request
                        )

                        # Get user applications
                        apps_request = APIRequest(
                            "GET", f"/users/{user['id']}/appLinks"
                        )
                        apps_response = await self.api_client.make_request(apps_request)

                        # Get user roles
                        roles_request = APIRequest("GET", f"/users/{user['id']}/roles")
                        roles_response = await self.api_client.make_request(
                            roles_request
                        )

                        # Get MFA factors
                        factors_request = APIRequest(
                            "GET", f"/users/{user['id']}/factors"
                        )
                        factors_response = await self.api_client.make_request(
                            factors_request
                        )

                        evidence_item = self.create_evidence_item(
                            evidence_type="identity_user",
                            resource_id=user["id"],
                            resource_name=user["profile"]["login"],
                            data={
                                "user_id": user["id"],
                                "username": user["profile"]["login"],
                                "email": user["profile"]["email"],
                                "first_name": user["profile"].get("firstName"),
                                "last_name": user["profile"].get("lastName"),
                                "display_name": user["profile"].get("displayName"),
                                "mobile_phone": user["profile"].get("mobilePhone"),
                                "status": user["status"],
                                "created": user["created"],
                                "activated": user.get("activated"),
                                "status_changed": user.get("statusChanged"),
                                "last_login": user.get("lastLogin"),
                                "last_updated": user["lastUpdated"],
                                "password_changed": user.get("passwordChanged"),
                                "profile": user["profile"],
                                "credentials": {
                                    "password": user.get("credentials", {}).get(
                                        "password", {}
                                    ),
                                    "recovery_question": user.get(
                                        "credentials", {}
                                    ).get("recovery_question", {}),
                                    "provider": user.get("credentials", {}).get(
                                        "provider", {}
                                    ),
                                },
                                "groups": [
                                    {
                                        "id": group["id"],
                                        "name": group["profile"]["name"],
                                        "description": group["profile"].get(
                                            "description"
                                        ),
                                    }
                                    for group in groups_response.data
                                ],
                                "applications": [
                                    {
                                        "id": app["id"],
                                        "label": app["label"],
                                        "link_url": app.get("linkUrl"),
                                    }
                                    for app in apps_response.data
                                ],
                                "roles": [
                                    {
                                        "id": role["id"],
                                        "type": role["type"],
                                        "status": role["status"],
                                        "created": role["created"],
                                        "last_updated": role["lastUpdated"],
                                    }
                                    for role in roles_response.data
                                ],
                                "mfa_factors": [
                                    {
                                        "id": factor["id"],
                                        "factor_type": factor["factorType"],
                                        "provider": factor["provider"],
                                        "status": factor["status"],
                                        "created": factor["created"],
                                        "last_updated": factor["lastUpdated"],
                                    }
                                    for factor in factors_response.data
                                ],
                            },
                            compliance_controls=[
                                "CC6.1",
                                "CC6.2",
                                "CC6.7",
                            ],  # SOC 2 user access controls
                            quality_score=self._calculate_user_quality_score(
                                user, factors_response.data
                            ),
                        )

                        evidence.append(evidence_item)

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to get full details for user {user['profile']['login']}: {e}"
                        )
                        # Still add basic user info
                        evidence_item = self.create_evidence_item(
                            evidence_type="identity_user",
                            resource_id=user["id"],
                            resource_name=user["profile"]["login"],
                            data={
                                "user_id": user["id"],
                                "username": user["profile"]["login"],
                                "status": user["status"],
                                "created": user["created"],
                                "last_login": user.get("lastLogin"),
                            },
                            compliance_controls=["CC6.1", "CC6.2"],
                            quality_score=0.5,  # Lower score due to incomplete data
                        )
                        evidence.append(evidence_item)
                        continue

                # Check for pagination
                url = None
                if hasattr(response, "headers") and "Link" in response.headers:
                    # Parse Link header for next page
                    link_header = response.headers["Link"]
                    if 'rel="next"' in link_header:
                        # Extract next URL from link header
                        import re

                        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                        if next_match:
                            next_url = next_match.group(1)
                            # Extract just the path from the full URL
                            url = next_url.split("/api/v1")[-1]
                            params = None  # URL already contains params

        except Exception as e:
            self.logger.error(f"Error collecting Okta user evidence: {e}")
            raise OktaAPIException(f"Failed to collect user evidence: {e}")

        return evidence

    def _calculate_user_quality_score(self, user: Dict, mfa_factors: List) -> float:
        """Calculate quality score for Okta user"""
        score = 1.0

        # Check if user has MFA enabled
        active_mfa = [f for f in mfa_factors if f["status"] == "ACTIVE"]
        if not active_mfa:
            score -= 0.4
        elif len(active_mfa) == 1:
            score -= 0.1  # Single factor is ok but multi-factor is better

        # Check user status
        if user["status"] not in ["ACTIVE", "PASSWORD_EXPIRED"]:
            score -= 0.2

        # Check if user has logged in recently
        if user.get("lastLogin"):
            try:
                last_login = datetime.fromisoformat(
                    user["lastLogin"].replace("Z", "+00:00")
                )
                days_since_login = (datetime.now(last_login.tzinfo) - last_login).days
                if days_since_login > 90:  # Inactive user
                    score -= 0.3
                elif days_since_login > 30:
                    score -= 0.1
            except Exception:
                pass  # Ignore date parsing errors

        # Check if essential profile fields are filled
        profile = user.get("profile", {})
        required_fields = ["firstName", "lastName", "email"]
        missing_fields = [field for field in required_fields if not profile.get(field)]
        if missing_fields:
            score -= 0.1 * len(missing_fields)

        return max(0.0, score)


class OktaGroupCollector(BaseEvidenceCollector):
    """Collect group and membership evidence from Okta"""

    async def collect(self, **kwargs) -> List[EvidenceItem]:
        """Collect groups and their memberships"""
        evidence = []

        try:
            # Collect all groups
            url = "/groups"
            params = {"limit": 200}

            while url:
                groups_request = APIRequest(
                    "GET", url, params=params if url == "/groups" else None
                )
                response = await self.api_client.make_request(groups_request)

                for group in response.data:
                    try:
                        # Get group members
                        members_request = APIRequest(
                            "GET", f"/groups/{group['id']}/users"
                        )
                        members_response = await self.api_client.make_request(
                            members_request
                        )

                        # Get group applications
                        apps_request = APIRequest("GET", f"/groups/{group['id']}/apps")
                        apps_response = await self.api_client.make_request(apps_request)

                        # Get group roles
                        roles_request = APIRequest(
                            "GET", f"/groups/{group['id']}/roles"
                        )
                        roles_response = await self.api_client.make_request(
                            roles_request
                        )

                        evidence_item = self.create_evidence_item(
                            evidence_type="identity_group",
                            resource_id=group["id"],
                            resource_name=group["profile"]["name"],
                            data={
                                "group_id": group["id"],
                                "name": group["profile"]["name"],
                                "description": group["profile"].get("description"),
                                "type": group["type"],
                                "created": group["created"],
                                "last_updated": group["lastUpdated"],
                                "last_membership_updated": group.get(
                                    "lastMembershipUpdated"
                                ),
                                "object_class": group.get("objectClass", []),
                                "profile": group["profile"],
                                "members": [
                                    {
                                        "id": member["id"],
                                        "username": member["profile"]["login"],
                                        "email": member["profile"]["email"],
                                        "status": member["status"],
                                    }
                                    for member in members_response.data
                                ],
                                "member_count": len(members_response.data),
                                "applications": [
                                    {
                                        "id": app["id"],
                                        "name": app["name"],
                                        "label": app["label"],
                                        "status": app["status"],
                                    }
                                    for app in apps_response.data
                                ],
                                "roles": [
                                    {
                                        "id": role["id"],
                                        "type": role["type"],
                                        "status": role["status"],
                                    }
                                    for role in roles_response.data
                                ],
                            },
                            compliance_controls=[
                                "CC6.1",
                                "CC6.2",
                            ],  # SOC 2 group access controls
                            quality_score=self._calculate_group_quality_score(
                                group, members_response.data
                            ),
                        )

                        evidence.append(evidence_item)

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to get full details for group {group['profile']['name']}: {e}"
                        )
                        continue

                # Handle pagination
                url = None
                if hasattr(response, "headers") and "Link" in response.headers:
                    link_header = response.headers["Link"]
                    if 'rel="next"' in link_header:
                        import re

                        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                        if next_match:
                            next_url = next_match.group(1)
                            url = next_url.split("/api/v1")[-1]
                            params = None

        except Exception as e:
            self.logger.error(f"Error collecting Okta group evidence: {e}")
            raise OktaAPIException(f"Failed to collect group evidence: {e}")

        return evidence

    def _calculate_group_quality_score(self, group: Dict, members: List) -> float:
        """Calculate quality score for Okta group"""
        score = 1.0

        # Check if group has description
        if not group["profile"].get("description"):
            score -= 0.2

        # Check if group has appropriate number of members
        member_count = len(members)
        if member_count == 0:
            score -= 0.3  # Empty groups are suspicious
        elif member_count > 100:
            score -= 0.1  # Very large groups might need review

        # Check group type
        if group["type"] == "OKTA_GROUP":
            score += 0.1  # Okta-managed groups are generally better controlled

        return max(0.0, score)


class OktaApplicationCollector(BaseEvidenceCollector):
    """Collect application and access evidence from Okta"""

    async def collect(self, **kwargs) -> List[EvidenceItem]:
        """Collect applications and their configurations"""
        evidence = []

        try:
            # Collect all applications
            url = "/apps"
            params = {"limit": 200}

            while url:
                apps_request = APIRequest(
                    "GET", url, params=params if url == "/apps" else None
                )
                response = await self.api_client.make_request(apps_request)

                for app in response.data:
                    try:
                        # Get application users
                        users_request = APIRequest("GET", f"/apps/{app['id']}/users")
                        users_response = await self.api_client.make_request(
                            users_request
                        )

                        # Get application groups
                        groups_request = APIRequest("GET", f"/apps/{app['id']}/groups")
                        groups_response = await self.api_client.make_request(
                            groups_request
                        )

                        evidence_item = self.create_evidence_item(
                            evidence_type="identity_application",
                            resource_id=app["id"],
                            resource_name=app["label"],
                            data={
                                "app_id": app["id"],
                                "name": app["name"],
                                "label": app["label"],
                                "status": app["status"],
                                "last_updated": app["lastUpdated"],
                                "created": app["created"],
                                "features": app.get("features", []),
                                "sign_on_mode": app.get("signOnMode"),
                                "accessibility": app.get("accessibility", {}),
                                "visibility": app.get("visibility", {}),
                                "settings": app.get("settings", {}),
                                "assigned_users": [
                                    {
                                        "id": user["id"],
                                        "username": user.get("credentials", {}).get(
                                            "userName"
                                        ),
                                        "status": user.get("status"),
                                        "created": user.get("created"),
                                        "last_updated": user.get("lastUpdated"),
                                    }
                                    for user in users_response.data
                                ],
                                "user_count": len(users_response.data),
                                "assigned_groups": [
                                    {
                                        "id": group["id"],
                                        "priority": group.get("priority"),
                                    }
                                    for group in groups_response.data
                                ],
                                "group_count": len(groups_response.data),
                            },
                            compliance_controls=[
                                "CC6.1",
                                "CC6.2",
                                "CC6.8",
                            ],  # SOC 2 application access controls
                            quality_score=self._calculate_app_quality_score(
                                app, users_response.data
                            ),
                        )

                        evidence.append(evidence_item)

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to get full details for app {app['label']}: {e}"
                        )
                        continue

                # Handle pagination
                url = None
                if hasattr(response, "headers") and "Link" in response.headers:
                    link_header = response.headers["Link"]
                    if 'rel="next"' in link_header:
                        import re

                        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                        if next_match:
                            next_url = next_match.group(1)
                            url = next_url.split("/api/v1")[-1]
                            params = None

        except Exception as e:
            self.logger.error(f"Error collecting Okta application evidence: {e}")
            raise OktaAPIException(f"Failed to collect application evidence: {e}")

        return evidence

    def _calculate_app_quality_score(self, app: Dict, users: List) -> float:
        """Calculate quality score for Okta application"""
        score = 1.0

        # Check application status
        if app["status"] != "ACTIVE":
            score -= 0.2

        # Check sign-on mode security
        sign_on_mode = app.get("signOnMode", "")
        if sign_on_mode in ["SAML_2_0", "OPENID_CONNECT"]:
            score += 0.2  # Secure SSO protocols
        elif sign_on_mode == "BASIC_AUTH":
            score -= 0.3  # Less secure

        # Check if app has users assigned
        if len(users) == 0:
            score -= 0.1  # Unused apps might be unnecessary

        return max(0.0, score)


class OktaLogsCollector(BaseEvidenceCollector):
    """Collect system logs for audit evidence"""

    async def collect(
        self, since: datetime = None, event_types: List[str] = None, **kwargs
    ) -> List[EvidenceItem]:
        """Collect system logs for audit evidence"""
        if not since:
            since = datetime.utcnow() - timedelta(days=7)  # Last 7 days by default

        evidence = []

        try:
            params = {
                "since": since.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "limit": 1000,
                "sortOrder": "DESCENDING",
            }

            if event_types:
                # Okta uses filter parameter for event type filtering
                params["filter"] = f'eventType eq "{event_types[0]}"'
                for event_type in event_types[1:]:
                    params["filter"] += f' or eventType eq "{event_type}"'

            # Collect logs with pagination
            url = "/logs"

            while url and len(evidence) < 10000:  # Limit to avoid too much data
                logs_request = APIRequest(
                    "GET", url, params=params if url == "/logs" else None
                )
                response = await self.api_client.make_request(logs_request)

                for log_entry in response.data:
                    evidence_item = self.create_evidence_item(
                        evidence_type="audit_log",
                        resource_id=log_entry["uuid"],
                        resource_name=log_entry["eventType"],
                        data={
                            "event_id": log_entry["uuid"],
                            "event_type": log_entry["eventType"],
                            "event_time": log_entry["published"],
                            "version": log_entry.get("version"),
                            "severity": log_entry.get("severity"),
                            "legacy_event_type": log_entry.get("legacyEventType"),
                            "display_message": log_entry.get("displayMessage"),
                            "actor": (
                                {
                                    "id": log_entry.get("actor", {}).get("id"),
                                    "type": log_entry.get("actor", {}).get("type"),
                                    "alternate_id": log_entry.get("actor", {}).get(
                                        "alternateId"
                                    ),
                                    "display_name": log_entry.get("actor", {}).get(
                                        "displayName"
                                    ),
                                    "detail": log_entry.get("actor", {}).get(
                                        "detail", {}
                                    ),
                                }
                                if log_entry.get("actor")
                                else None
                            ),
                            "client": (
                                {
                                    "user_agent": log_entry.get("client", {}).get(
                                        "userAgent", {}
                                    ),
                                    "zone": log_entry.get("client", {}).get("zone"),
                                    "device": log_entry.get("client", {}).get("device"),
                                    "id": log_entry.get("client", {}).get("id"),
                                    "ip_address": log_entry.get("client", {}).get(
                                        "ipAddress"
                                    ),
                                    "geographical_context": log_entry.get(
                                        "client", {}
                                    ).get("geographicalContext", {}),
                                }
                                if log_entry.get("client")
                                else None
                            ),
                            "authentication_context": log_entry.get(
                                "authenticationContext", {}
                            ),
                            "security_context": log_entry.get("securityContext", {}),
                            "target": [
                                {
                                    "id": target.get("id"),
                                    "type": target.get("type"),
                                    "alternate_id": target.get("alternateId"),
                                    "display_name": target.get("displayName"),
                                    "detail": target.get("detail", {}),
                                }
                                for target in log_entry.get("target", [])
                            ],
                            "transaction": log_entry.get("transaction", {}),
                            "debug_context": log_entry.get("debugContext", {}),
                            "outcome": (
                                {
                                    "result": log_entry.get("outcome", {}).get(
                                        "result"
                                    ),
                                    "reason": log_entry.get("outcome", {}).get(
                                        "reason"
                                    ),
                                }
                                if log_entry.get("outcome")
                                else None
                            ),
                            "request": log_entry.get("request", {}),
                        },
                        compliance_controls=[
                            "CC6.1",
                            "CC7.2",
                            "CC7.3",
                        ],  # SOC 2 monitoring and logging
                        quality_score=self._calculate_log_quality_score(log_entry),
                    )

                    evidence.append(evidence_item)

                # Handle pagination
                url = None
                if hasattr(response, "headers") and "Link" in response.headers:
                    link_header = response.headers["Link"]
                    if 'rel="next"' in link_header:
                        import re

                        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                        if next_match:
                            next_url = next_match.group(1)
                            url = next_url.split("/api/v1")[-1]
                            params = None

        except Exception as e:
            self.logger.error(f"Error collecting Okta logs: {e}")
            raise OktaAPIException(f"Failed to collect logs: {e}")

        return evidence

    def _calculate_log_quality_score(self, log_entry: Dict) -> float:
        """Calculate quality score for audit log entry"""
        score = 1.0

        # Check if essential fields are present
        required_fields = ["actor", "client", "eventType", "published"]
        missing_fields = [
            field for field in required_fields if not log_entry.get(field)
        ]

        if missing_fields:
            score -= 0.2 * len(missing_fields)

        # Check if it's a security-relevant event
        security_events = [
            "user.authentication.auth_via_mfa",
            "user.authentication.sso",
            "user.lifecycle.create",
            "user.lifecycle.delete",
            "policy.lifecycle.create",
            "policy.lifecycle.update",
            "application.lifecycle.create",
            "application.lifecycle.delete",
        ]

        if log_entry.get("eventType") in security_events:
            score += 0.1  # Security events are more valuable

        # Check outcome
        outcome = log_entry.get("outcome", {}).get("result")
        if outcome == "FAILURE":
            score += 0.2  # Failed events are important for security monitoring

        return max(0.0, score)


# Additional collectors for completeness
class OktaPolicyCollector(BaseEvidenceCollector):
    async def collect(self, **kwargs) -> List[EvidenceItem]:
        # Implementation for policy collection
        return []


class OktaMFACollector(BaseEvidenceCollector):
    async def collect(self, **kwargs) -> List[EvidenceItem]:
        # Implementation for MFA factor collection
        return []


class OktaZoneCollector(BaseEvidenceCollector):
    async def collect(self, **kwargs) -> List[EvidenceItem]:
        # Implementation for network zone collection
        return []


class OktaAuthServerCollector(BaseEvidenceCollector):
    async def collect(self, **kwargs) -> List[EvidenceItem]:
        # Implementation for authorization server collection
        return []
