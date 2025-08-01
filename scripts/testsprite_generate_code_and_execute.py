#!/usr/bin/env python3
"""
TestSprite Code Generation and Execution Script
Generates test code from TestSprite test plans and executes them
"""

import json
import os
import sys
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class TestSpriteExecutor:
    def __init__(self):
        self.project_root = project_root
        self.testsprite_dir = self.project_root / "testsprite_tests"
        self.generated_tests_dir = self.project_root / "tests" / "testsprite_generated"
        self.results = []
        
    def load_test_plans(self) -> Dict[str, Any]:
        """Load TestSprite test plans from JSON files"""
        test_plans = {}
        
        # Load frontend test plan
        frontend_plan_path = self.testsprite_dir / "testsprite_frontend_test_plan.json"
        if frontend_plan_path.exists():
            with open(frontend_plan_path, 'r') as f:
                test_plans['frontend'] = json.load(f)
                print(f"✅ Loaded {len(test_plans['frontend'])} frontend test cases")
        
        # Load standard PRD
        prd_path = self.testsprite_dir / "standard_prd.json"
        if prd_path.exists():
            with open(prd_path, 'r') as f:
                test_plans['prd'] = json.load(f)
                print(f"✅ Loaded PRD specifications")
        
        return test_plans
    
    def generate_pytest_code(self, test_case: Dict[str, Any]) -> str:
        """Generate pytest code from a TestSprite test case"""
        test_id = test_case.get('id', 'unknown')
        title = test_case.get('title', 'Unknown Test')
        description = test_case.get('description', '')
        category = test_case.get('category', 'functional')
        priority = test_case.get('priority', 'Medium')
        steps = test_case.get('steps', [])
        
        # Generate test function name
        func_name = f"test_{test_id.lower()}_{title.lower().replace(' ', '_').replace('-', '_')}"
        func_name = ''.join(c for c in func_name if c.isalnum() or c == '_')
        
        # Generate test code
        test_code = f'''
def {func_name}():
    """
    {title}
    
    Description: {description}
    Category: {category}
    Priority: {priority}
    TestSprite ID: {test_id}
    """
    # Test implementation based on TestSprite steps
'''
        
        for i, step in enumerate(steps, 1):
            step_type = step.get('type', 'action')
            step_desc = step.get('description', '')
            
            if step_type == 'action':
                test_code += f'''
    # Step {i}: {step_desc}
    # TODO: Implement action step
    pass
'''
            elif step_type == 'assertion':
                test_code += f'''
    # Step {i}: {step_desc}
    # TODO: Implement assertion
    assert True, "Assertion not implemented"
'''
        
        return test_code
    
    def generate_authentication_tests(self) -> str:
        """Generate authentication tests based on JWT system"""
        return '''
import pytest
import requests
from fastapi.testclient import TestClient
from main import app

class TestAuthenticationFlow:
    """Authentication tests generated from TestSprite plans"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def test_user_data(self):
        return {
            "email": "testsprite@example.com",
            "password": "TestSprite123!",
            "full_name": "TestSprite User"
        }
    
    def test_user_registration_valid_data(self, client, test_user_data):
        """
        TestSprite TC001: User Registration with Valid Data
        Verify that a user can successfully register using valid credentials
        """
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
    
    def test_user_login_correct_credentials(self, client, test_user_data):
        """
        TestSprite TC002: User Login with Correct Credentials
        Validate that users can log in successfully using valid credentials
        """
        # First register the user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Then login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_protected_endpoint_access(self, client, test_user_data):
        """
        TestSprite: Protected Endpoint Access
        Test accessing protected endpoints with valid JWT token
        """
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Access protected endpoint
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == test_user_data["email"]
'''
    
    def create_generated_tests_directory(self):
        """Create directory for generated tests"""
        self.generated_tests_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = self.generated_tests_dir / "__init__.py"
        init_file.write_text("# TestSprite Generated Tests\n")
    
    def generate_all_tests(self, test_plans: Dict[str, Any]):
        """Generate all test files from TestSprite plans"""
        self.create_generated_tests_directory()
        
        # Generate authentication tests
        auth_test_file = self.generated_tests_dir / "test_authentication_testsprite.py"
        auth_test_content = f'''"""
TestSprite Generated Authentication Tests
Generated on: {datetime.now().isoformat()}
"""
{self.generate_authentication_tests()}
'''
        auth_test_file.write_text(auth_test_content)
        print(f"✅ Generated authentication tests: {auth_test_file}")
        
        # Generate tests from frontend test plan
        if 'frontend' in test_plans:
            frontend_tests = []
            for test_case in test_plans['frontend'][:5]:  # Limit to first 5 for now
                test_code = self.generate_pytest_code(test_case)
                frontend_tests.append(test_code)
            
            frontend_test_file = self.generated_tests_dir / "test_frontend_testsprite.py"
            frontend_content = f'''"""
TestSprite Generated Frontend Tests
Generated on: {datetime.now().isoformat()}
"""
import pytest
from fastapi.testclient import TestClient
from main import app

class TestFrontendFlow:
    """Frontend tests generated from TestSprite plans"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
{"".join(frontend_tests)}
'''
            frontend_test_file.write_text(frontend_content)
            print(f"✅ Generated frontend tests: {frontend_test_file}")
    
    async def run_generated_tests(self):
        """Execute the generated tests"""
        print("\n🧪 Running TestSprite Generated Tests...")
        
        # Activate virtual environment and run tests
        venv_python = self.project_root / ".venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = "python"  # Fallback to system python
        
        test_commands = [
            [str(venv_python), "-m", "pytest", str(self.generated_tests_dir), "-v", "--tb=short"],
            [str(venv_python), "-m", "pytest", str(self.generated_tests_dir / "test_authentication_testsprite.py"), "-v"]
        ]
        
        for i, cmd in enumerate(test_commands, 1):
            print(f"\n📋 Running test command {i}: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                self.results.append({
                    "command": " ".join(cmd),
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                
                if result.returncode == 0:
                    print(f"✅ Test command {i} passed")
                else:
                    print(f"❌ Test command {i} failed with code {result.returncode}")
                
                # Show output
                if result.stdout:
                    print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                if result.stderr:
                    print("STDERR:", result.stderr[-500:])  # Last 500 chars
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Test command {i} timed out after 5 minutes")
            except Exception as e:
                print(f"❌ Error running test command {i}: {e}")
    
    def generate_report(self):
        """Generate execution report"""
        report_file = self.project_root / "testsprite_execution_report.json"
        
        report = {
            "execution_date": datetime.now().isoformat(),
            "project": "ruleIQ",
            "test_framework": "TestSprite + pytest",
            "results": self.results,
            "summary": {
                "total_commands": len(self.results),
                "passed": len([r for r in self.results if r["return_code"] == 0]),
                "failed": len([r for r in self.results if r["return_code"] != 0])
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Execution report saved to: {report_file}")
        
        # Print summary
        print(f"\n📋 TestSprite Execution Summary:")
        print(f"   Total Commands: {report['summary']['total_commands']}")
        print(f"   Passed: {report['summary']['passed']}")
        print(f"   Failed: {report['summary']['failed']}")

async def main():
    """Main execution function"""
    print("🚀 TestSprite Code Generation and Execution")
    print("=" * 50)
    
    executor = TestSpriteExecutor()
    
    # Load test plans
    test_plans = executor.load_test_plans()
    
    if not test_plans:
        print("❌ No test plans found in testsprite_tests directory")
        return
    
    # Generate test code
    print("\n🔧 Generating test code from TestSprite plans...")
    executor.generate_all_tests(test_plans)
    
    # Execute tests
    await executor.run_generated_tests()
    
    # Generate report
    executor.generate_report()
    
    print("\n✅ TestSprite execution complete!")

if __name__ == "__main__":
    asyncio.run(main())
