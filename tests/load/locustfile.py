"""
Load testing configuration for ComplianceGPT using Locust.

Usage:
    locust -f tests/load/locustfile.py --host=http://localhost:8000

For web UI:
    locust -f tests/load/locustfile.py --host=http://localhost:8000 --web-host=0.0.0.0

For headless mode:
    locust -f tests/load/locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 300
"""

import random
from uuid import uuid4

from locust import HttpUser, between, events, task


class ComplianceGPTUser(HttpUser):
    """Simulates a typical ComplianceGPT user workflow."""

    wait_time = between(1, 5)  # Simulate user think time between requests

    def on_start(self):
        """Called when a simulated user starts. Set up test data."""
        # In a real load test, you'd authenticate and get a valid token
        self.headers = {
            "Authorization": f"Bearer load_test_token_{uuid4()}",
            "Content-Type": "application/json",
        }

        # Mock IDs for testing (in real tests, these would be valid UUIDs)
        self.business_profile_id = str(uuid4())
        self.framework_id = str(uuid4())

        # Simulate login/authentication
        self.authenticate()

    def authenticate(self):
        """Simulate user authentication."""
        try:
            response = self.client.post(
                "/api/auth/login",
                json={
                    "username": f"loadtest_user_{random.randint(1, 1000)}@example.com",
                    "password": "loadtest_password",
                },
                catch_response=True,
            )

            if response.status_code in [200, 401]:  # 401 expected for mock users
                response.success()
            else:
                response.failure(f"Unexpected auth response: {response.status_code}")

        except Exception as e:
            print(f"Auth failed: {e}")

    @task(10)
    def view_dashboard(self):
        """Simulates a user loading their main dashboard - most common action."""
        with self.client.get(
            "/api/business-profiles", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Dashboard load failed: {response.status_code}")

    @task(8)
    def view_evidence_items(self):
        """Simulates viewing evidence items."""
        with self.client.get(
            "/api/evidence", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Evidence view failed: {response.status_code}")

    @task(6)
    def view_frameworks(self):
        """Simulates viewing compliance frameworks."""
        with self.client.get(
            "/api/frameworks", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Frameworks view failed: {response.status_code}")

    @task(5)
    def chat_with_assistant(self):
        """Simulates AI assistant interaction."""
        messages = [
            "What is my current compliance status?",
            "Show me my evidence for ISO27001",
            "What gaps do I need to address?",
            "How can I improve my compliance score?",
            "What evidence should I collect next?",
        ]

        with self.client.post(
            "/api/chat/conversations",
            json={
                "title": f"Load Test Chat {random.randint(1, 1000)}",
                "initial_message": random.choice(messages),
            },
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Chat failed: {response.status_code}")

    @task(4)
    def generate_policy(self):
        """Simulates policy generation - moderately heavy operation."""
        with self.client.post(
            "/api/policies/generate",
            json={
                "business_profile_id": self.business_profile_id,
                "framework_id": self.framework_id,
                "policy_type": "information_security",
                "customizations": {
                    "company_name": f"Load Test Company {random.randint(1, 100)}",
                    "industry": random.choice(
                        ["Technology", "Healthcare", "Finance", "Manufacturing"]
                    ),
                },
            },
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201, 401]:
                response.success()
            else:
                response.failure(f"Policy generation failed: {response.status_code}")

    @task(3)
    def check_readiness_score(self):
        """Simulates checking compliance readiness."""
        with self.client.get(
            f"/api/readiness/{self.business_profile_id}",
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 404]:
                response.success()
            else:
                response.failure(f"Readiness check failed: {response.status_code}")

    @task(2)
    def generate_light_report(self):
        """Simulates generating a JSON report - medium load operation."""
        with self.client.post(
            "/api/reports/generate",
            json={
                "business_profile_id": self.business_profile_id,
                "report_type": "compliance_status",
                "format": "json",
                "parameters": {"frameworks": ["ISO27001"], "period_days": 30},
            },
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Light report failed: {response.status_code}")

    @task(1)
    def generate_heavy_report(self):
        """Simulates generating a PDF report - heavy operation."""
        with self.client.post(
            "/api/reports/generate",
            json={
                "business_profile_id": self.business_profile_id,
                "report_type": "executive_summary",
                "format": "pdf",
                "parameters": {
                    "frameworks": ["ISO27001", "SOC2", "GDPR"],
                    "period_days": 90,
                    "include_charts": True,
                },
            },
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Heavy report failed: {response.status_code}")

    @task(1)
    def integration_operations(self):
        """Simulates integration-related operations."""
        operations = [
            ("GET", "/api/integrations", {}),
            (
                "POST",
                "/api/integrations/google_workspace/test",
                {"credentials": {"test": True}},
            ),
        ]

        method, endpoint, data = random.choice(operations)

        if method == "GET":
            with self.client.get(
                endpoint, headers=self.headers, catch_response=True
            ) as response:
                if response.status_code in [200, 401]:
                    response.success()
                else:
                    response.failure(f"Integration GET failed: {response.status_code}")
        else:
            with self.client.post(
                endpoint, json=data, headers=self.headers, catch_response=True
            ) as response:
                if response.status_code in [
                    200,
                    401,
                    400,
                ]:  # 400 expected for test credentials
                    response.success()
                else:
                    response.failure(f"Integration POST failed: {response.status_code}")


class AdminUser(HttpUser):
    """Simulates an admin user with different usage patterns."""

    wait_time = between(2, 8)  # Admins tend to spend more time on each operation
    weight = 1  # Fewer admin users compared to regular users

    def on_start(self):
        """Admin user setup."""
        self.headers = {
            "Authorization": f"Bearer admin_token_{uuid4()}",
            "Content-Type": "application/json",
        }

    @task(5)
    def manage_report_schedules(self):
        """Admin manages report schedules."""
        # List schedules
        with self.client.get(
            "/api/reports/schedules", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Schedule list failed: {response.status_code}")

    @task(3)
    def view_system_stats(self):
        """Admin views system statistics."""
        endpoints = ["/api/reports/stats", "/api/evidence/stats", "/health"]

        for endpoint in random.sample(endpoints, k=random.randint(1, len(endpoints))):
            with self.client.get(
                endpoint, headers=self.headers, catch_response=True
            ) as response:
                if response.status_code in [200, 401, 404]:
                    response.success()
                else:
                    response.failure(
                        f"Stats endpoint {endpoint} failed: {response.status_code}"
                    )

    @task(2)
    def bulk_operations(self):
        """Admin performs bulk operations."""
        # Simulate bulk evidence processing
        with self.client.post(
            "/api/evidence/bulk-process",
            json={"evidence_ids": [str(uuid4()) for _ in range(10)]},
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201, 401, 404]:
                response.success()
            else:
                response.failure(f"Bulk operation failed: {response.status_code}")


class HeavyReportUser(HttpUser):
    """Simulates users who primarily generate reports - tests report system load."""

    wait_time = between(5, 15)  # Report generation takes time
    weight = 1  # Small percentage of users

    def on_start(self):
        self.headers = {
            "Authorization": f"Bearer report_user_token_{uuid4()}",
            "Content-Type": "application/json",
        }
        self.business_profile_id = str(uuid4())

    @task(3)
    def generate_executive_reports(self):
        """Generate executive summary reports."""
        with self.client.post(
            "/api/reports/generate",
            json={
                "business_profile_id": self.business_profile_id,
                "report_type": "executive_summary",
                "format": "pdf",
                "parameters": {"frameworks": ["ISO27001", "SOC2"]},
            },
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Executive report failed: {response.status_code}")

    @task(2)
    def generate_gap_analysis(self):
        """Generate gap analysis reports."""
        with self.client.post(
            "/api/reports/generate",
            json={
                "business_profile_id": self.business_profile_id,
                "report_type": "gap_analysis",
                "format": "pdf",
                "parameters": {
                    "frameworks": ["ISO27001"],
                    "severity_filter": "high",
                    "include_remediation_plan": True,
                },
            },
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Gap analysis failed: {response.status_code}")

    @task(1)
    def download_reports(self):
        """Download previously generated reports."""
        report_types = ["executive_summary", "evidence_report", "audit_readiness"]

        with self.client.get(
            f"/api/reports/generate/{random.choice(report_types)}/download",
            params={"business_profile_id": self.business_profile_id, "format": "pdf"},
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 404]:
                response.success()
            else:
                response.failure(f"Report download failed: {response.status_code}")


# Event listeners for custom metrics
@events.request.add_listener
def my_request_handler(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    start_time,
    url,
    **kwargs,
):
    """Custom request handler to log specific metrics."""
    if exception:
        print(f"Request failed: {name} - {exception}")
    elif response.status_code >= 400:
        print(f"HTTP error: {name} - {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the load test starts."""
    print("ComplianceGPT load test starting...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the load test stops."""
    print("ComplianceGPT load test completed.")

    # Print summary of results
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
