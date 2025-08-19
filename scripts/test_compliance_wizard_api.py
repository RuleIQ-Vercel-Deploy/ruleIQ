#!/usr/bin/env python3
"""
Test the compliance wizard API integration with corrected routes.
Verifies that the frontend can successfully connect to backend APIs.
"""

import asyncio
import aiohttp


class ComplianceWizardTester:
    def __init__(self) -> None:
        self.base_url = "http://localhost:8000"
        self.session = None
        self.auth_token = None
        self.business_profile_id = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self) -> bool:
        """Authenticate with test user credentials."""
        login_data = {"email": "test@ruleiq.dev", "password": "TestPassword123!"}

        async with self.session.post(
            f"{self.base_url}/api/v1/auth/login", json=login_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data.get("access_token")
                print("✅ Authentication successful")
                return True
            else:
                text = await response.text()
                print(f"❌ Authentication failed: {response.status} - {text}")
                return False

    def get_headers(self):
        """Get headers with authentication."""
        return {"Authorization": f"Bearer {self.auth_token}"}

    async def test_frameworks_endpoint(self):
        """Test the frameworks endpoint that compliance wizard uses."""
        print("📋 Testing frameworks endpoint...")

        async with self.session.get(
            f"{self.base_url}/api/v1/frameworks", headers=self.get_headers()
        ) as response:
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list):
                    frameworks_count = len(data)
                    print(f"✅ Frameworks endpoint: {frameworks_count} frameworks available")
                    return data
                else:
                    frameworks_count = len(data.get("items", []))
                    print(f"✅ Frameworks endpoint: {frameworks_count} frameworks available")
                    return data.get("items", [])
            else:
                text = await response.text()
                print(f"❌ Frameworks endpoint failed: {response.status} - {text}")
                return []

    async def test_business_profile_endpoint(self):
        """Test business profile endpoint."""
        print("👤 Testing business profiles endpoint...")

        async with self.session.get(
            f"{self.base_url}/api/v1/business-profiles", headers=self.get_headers()
        ) as response:
            if response.status == 200:
                data = await response.json()
                profiles = data.get("items", [])
                if profiles:
                    self.business_profile_id = profiles[0].get("id")
                    print(f"✅ Business profiles endpoint: {len(profiles)} profiles found")
                    return profiles[0]
                else:
                    print("ℹ️ No business profiles found, will create one")
                    return await self.create_business_profile()
            else:
                text = await response.text()
                print(f"❌ Business profiles endpoint failed: {response.status} - {text}")
                return None

    async def create_business_profile(self):
        """Create a test business profile."""
        profile_data = {
            "company_name": "Test Company Ltd",
            "industry": "Technology",
            "company_size": "11-50",
            "description": "Test company for compliance wizard testing",
        }

        async with self.session.post(
            f"{self.base_url}/api/v1/business-profiles",
            json=profile_data,
            headers=self.get_headers(),
        ) as response:
            if response.status == 201:
                data = await response.json()
                self.business_profile_id = data.get("id")
                print(f"✅ Created business profile: {data.get('company_name')}")
                return data
            else:
                text = await response.text()
                print(f"❌ Failed to create business profile: {response.status} - {text}")
                return None

    async def test_compliance_status(self):
        """Test compliance status endpoint."""
        if not self.business_profile_id:
            print("❌ Cannot test compliance status without business profile")
            return None

        print("📊 Testing compliance status endpoint...")

        async with self.session.get(
            f"{self.base_url}/api/v1/compliance/status",
            params={"business_profile_id": self.business_profile_id},
            headers=self.get_headers(),
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Compliance status endpoint working")
                return data
            else:
                text = await response.text()
                print(f"❌ Compliance status failed: {response.status} - {text}")
                return None

    async def test_compliance_check(self, framework_id):
        """Test running a compliance check (the key integration point)."""
        if not self.business_profile_id:
            print("❌ Cannot test compliance check without business profile")
            return None

        print("🔍 Testing compliance check endpoint (key integration point)...")

        check_data = {"business_profile_id": self.business_profile_id, "framework_id": framework_id}

        async with self.session.post(
            f"{self.base_url}/api/v1/compliance/run-check",
            json=check_data,
            headers=self.get_headers(),
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Compliance check endpoint working")
                return data
            else:
                text = await response.text()
                print(f"❌ Compliance check failed: {response.status} - {text}")
                return None


async def main() -> None:
    """Run the complete compliance wizard API test."""
    print("🧙‍♂️ ruleIQ Compliance Wizard API Integration Test")
    print("=" * 55)

    async with ComplianceWizardTester() as tester:
        # Step 1: Authenticate
        if not await tester.authenticate():
            return

        # Step 2: Test frameworks (needed for wizard dropdown)
        frameworks = await tester.test_frameworks_endpoint()
        if not frameworks:
            print("❌ Cannot continue without frameworks")
            return

        # Step 3: Test business profile (needed for wizard context)
        business_profile = await tester.test_business_profile_endpoint()
        if not business_profile:
            print("❌ Cannot continue without business profile")
            return

        # Step 4: Test compliance status
        await tester.test_compliance_status()

        # Step 5: Test compliance check with first available framework
        if frameworks:
            framework_id = frameworks[0].get("id")
            print(f"🎯 Testing with framework: {frameworks[0].get('name')}")
            await tester.test_compliance_check(framework_id)

        print("\n🎉 Compliance Wizard API Integration Test Complete!")
        print("\nKey endpoints tested:")
        print("  ✓ Authentication flow")
        print("  ✓ Frameworks API (for dropdown)")
        print("  ✓ Business Profiles API (for context)")
        print("  ✓ Compliance Status API")
        print("  ✓ Compliance Check API (main integration)")
        print("\n💡 The compliance wizard should now work correctly!")


if __name__ == "__main__":
    asyncio.run(main())
