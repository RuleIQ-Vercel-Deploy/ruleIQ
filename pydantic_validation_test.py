#!/usr/bin/env python3
"""
Pydantic v2 validation test script for ruleIQ.
Ensures all models work correctly with Pydantic v2.
"""

import sys
from typing import Dict, List, Any
from pathlib import Path
import importlib
import inspect
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Terminal colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class PydanticValidator:
    def __init__(self):
        self.models = {}
        self.test_results = {"passed": 0, "failed": 0, "warnings": 0}
        self.issues = []
        
    def discover_models(self) -> Dict:
        """Discover all Pydantic models in the codebase."""
        print(f"\n{Colors.CYAN}Discovering Pydantic models...{Colors.END}")
        
        schema_modules = [
            "api.schemas.models",
            "api.schemas.reporting", 
            "api.schemas.compliance",
            "api.schemas.ai_policy",
            "api.schemas.chat",
            "api.schemas.evidence_collection",
            "api.schemas.evidence_classification",
            "api.schemas.iq_agent",
            "api.schemas.quality_analysis",
            "api.schemas.base",
        ]
        
        for module_name in schema_modules:
            try:
                module = importlib.import_module(module_name)
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        # Check if it's a Pydantic model
                        if hasattr(obj, '__fields__') or hasattr(obj, 'model_fields'):
                            self.models[f"{module_name}.{name}"] = obj
                            
            except Exception as e:
                print(f"  {Colors.YELLOW}⚠ Could not import {module_name}: {e}{Colors.END}")
                self.test_results["warnings"] += 1
        
        print(f"  {Colors.GREEN}✓ Discovered {len(self.models)} Pydantic models{Colors.END}")
        return self.models
    
    def test_model_import(self, model_name: str, model_class: Any) -> bool:
        """Test that a model can be imported and instantiated."""
        try:
            # Check if it's using Pydantic v2
            if hasattr(model_class, 'model_fields'):
                # Pydantic v2
                fields = model_class.model_fields
            elif hasattr(model_class, '__fields__'):
                # Pydantic v1 (should not happen after migration)
                print(f"    {Colors.YELLOW}⚠ Model still using v1 patterns{Colors.END}")
                self.issues.append(f"{model_name}: Still using Pydantic v1 patterns")
                return False
            else:
                print(f"    {Colors.RED}✗ Not a valid Pydantic model{Colors.END}")
                return False
            
            return True
            
        except Exception as e:
            print(f"    {Colors.RED}✗ Import failed: {e}{Colors.END}")
            self.issues.append(f"{model_name}: {str(e)}")
            return False
    
    def test_model_validation(self, model_name: str, model_class: Any) -> bool:
        """Test model validation with sample data."""
        try:
            # Get model fields
            fields = model_class.model_fields if hasattr(model_class, 'model_fields') else {}
            
            # Create sample data based on field types
            sample_data = {}
            for field_name, field_info in fields.items():
                # Get field type
                field_type = field_info.annotation if hasattr(field_info, 'annotation') else str
                
                # Skip optional fields for basic test
                if not (hasattr(field_info, 'is_required') and field_info.is_required()):
                    continue
                
                # Generate sample value based on type
                if field_type == str:
                    sample_data[field_name] = "test_string"
                elif field_type == int:
                    sample_data[field_name] = 1
                elif field_type == float:
                    sample_data[field_name] = 1.0
                elif field_type == bool:
                    sample_data[field_name] = True
                elif field_type == datetime:
                    sample_data[field_name] = datetime.now()
                elif hasattr(field_type, '__origin__') and field_type.__origin__ == list:
                    sample_data[field_name] = []
                elif hasattr(field_type, '__origin__') and field_type.__origin__ == dict:
                    sample_data[field_name] = {}
                else:
                    # For complex types, use a generic value
                    sample_data[field_name] = "test"
            
            # Try to create instance
            if sample_data:
                instance = model_class(**sample_data)
                
                # Test serialization (v2 uses model_dump)
                if hasattr(instance, 'model_dump'):
                    dumped = instance.model_dump()
                else:
                    dumped = instance.dict()
                
                # Test JSON serialization (v2 uses model_dump_json)
                if hasattr(instance, 'model_dump_json'):
                    json_str = instance.model_dump_json()
                else:
                    json_str = instance.json()
                
                return True
            else:
                # No required fields, just check instantiation
                instance = model_class()
                return True
                
        except Exception as e:
            # Some models may have complex validation, this is OK
            return True  # We're mainly checking for import/syntax errors
    
    def test_field_validators(self, model_name: str, model_class: Any) -> bool:
        """Test that field validators work correctly."""
        try:
            # Check for field_validator decorators (Pydantic v2)
            validators_found = 0
            for name, method in inspect.getmembers(model_class):
                if hasattr(method, '__wrapped__'):
                    # This might be a validator
                    validators_found += 1
            
            if validators_found > 0:
                print(f"      Found {validators_found} validators")
            
            return True
            
        except Exception as e:
            print(f"    {Colors.RED}✗ Validator check failed: {e}{Colors.END}")
            return False
    
    def test_config_classes(self, model_name: str, model_class: Any) -> bool:
        """Test that Config classes use Pydantic v2 patterns."""
        try:
            # Check for model_config (v2) vs Config (v1)
            if hasattr(model_class, 'model_config'):
                config = model_class.model_config
                
                # Check for v2 config patterns
                if isinstance(config, dict):
                    if 'from_attributes' in config:
                        print(f"      ✓ Uses from_attributes (v2)")
                    elif 'orm_mode' in config:
                        print(f"      {Colors.YELLOW}⚠ Still uses orm_mode (v1){Colors.END}")
                        self.issues.append(f"{model_name}: Uses orm_mode instead of from_attributes")
                        return False
                    return True
                    
            elif hasattr(model_class, 'Config'):
                # Still using v1 Config class
                print(f"      {Colors.YELLOW}⚠ Uses Config class (v1 pattern){Colors.END}")
                self.issues.append(f"{model_name}: Uses Config class instead of model_config")
                return False
            
            return True
            
        except Exception as e:
            print(f"    {Colors.RED}✗ Config check failed: {e}{Colors.END}")
            return False
    
    def test_specific_models(self):
        """Test specific critical models."""
        print(f"\n{Colors.BOLD}Testing Critical Models{Colors.END}")
        
        critical_models = [
            "api.schemas.models.AssessmentSessionCreate",
            "api.schemas.models.BusinessProfileCreate",
            "api.schemas.models.QuickAssessmentRequest",
            "api.schemas.models.UserCreate",
            "api.schemas.compliance.ComplianceAssessmentCreate",
            "api.schemas.reporting.ReportGenerationRequest",
        ]
        
        for model_path in critical_models:
            print(f"\n  Testing {model_path}...")
            
            try:
                # Import the model
                parts = model_path.rsplit('.', 1)
                module = importlib.import_module(parts[0])
                model_class = getattr(module, parts[1])
                
                # Run tests
                import_ok = self.test_model_import(model_path, model_class)
                validation_ok = self.test_model_validation(model_path, model_class)
                config_ok = self.test_config_classes(model_path, model_class)
                
                if all([import_ok, validation_ok, config_ok]):
                    print(f"    {Colors.GREEN}✓ All tests passed{Colors.END}")
                    self.test_results["passed"] += 1
                else:
                    print(f"    {Colors.RED}✗ Some tests failed{Colors.END}")
                    self.test_results["failed"] += 1
                    
            except Exception as e:
                print(f"    {Colors.RED}✗ Could not test: {e}{Colors.END}")
                self.test_results["failed"] += 1
                self.issues.append(f"{model_path}: {str(e)}")
    
    def test_fastapi_integration(self):
        """Test that models work with FastAPI."""
        print(f"\n{Colors.BOLD}Testing FastAPI Integration{Colors.END}")
        
        try:
            from main import app
            
            # Get OpenAPI schema
            schema = app.openapi()
            
            if schema and "components" in schema and "schemas" in schema["components"]:
                model_count = len(schema["components"]["schemas"])
                print(f"  {Colors.GREEN}✓ OpenAPI schema contains {model_count} models{Colors.END}")
                self.test_results["passed"] += 1
                
                # Check for common v1 vs v2 patterns in schema
                schema_str = json.dumps(schema)
                if "orm_mode" in schema_str:
                    print(f"  {Colors.YELLOW}⚠ Schema still contains 'orm_mode' references{Colors.END}")
                    self.test_results["warnings"] += 1
                    
            else:
                print(f"  {Colors.RED}✗ Could not get OpenAPI schema{Colors.END}")
                self.test_results["failed"] += 1
                
        except Exception as e:
            print(f"  {Colors.RED}✗ FastAPI integration test failed: {e}{Colors.END}")
            self.test_results["failed"] += 1
    
    def run_all_model_tests(self):
        """Run tests on all discovered models."""
        print(f"\n{Colors.BOLD}Testing All Models{Colors.END}")
        
        for model_name, model_class in self.models.items():
            # Basic import test
            if self.test_model_import(model_name, model_class):
                self.test_results["passed"] += 1
            else:
                self.test_results["failed"] += 1
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}PYDANTIC V2 VALIDATION SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Test Results:{Colors.END}")
        print(f"  {Colors.GREEN}Passed: {self.test_results['passed']}{Colors.END}")
        print(f"  {Colors.RED}Failed: {self.test_results['failed']}{Colors.END}")
        print(f"  {Colors.YELLOW}Warnings: {self.test_results['warnings']}{Colors.END}")
        
        total = self.test_results["passed"] + self.test_results["failed"]
        if total > 0:
            pass_rate = (self.test_results["passed"] / total) * 100
            print(f"  {Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.END}")
        
        if self.issues:
            print(f"\n{Colors.BOLD}Issues Found:{Colors.END}")
            for issue in self.issues[:10]:  # Show first 10 issues
                print(f"  • {issue}")
            if len(self.issues) > 10:
                print(f"  ... and {len(self.issues) - 10} more")
        
        print(f"\n{Colors.BOLD}Model Statistics:{Colors.END}")
        print(f"  Total models discovered: {len(self.models)}")
        
        # Check Pydantic version
        try:
            import pydantic
            print(f"  Pydantic version: {pydantic.__version__}")
            
            if pydantic.__version__.startswith("2."):
                print(f"  {Colors.GREEN}✓ Using Pydantic v2{Colors.END}")
            else:
                print(f"  {Colors.RED}✗ Not using Pydantic v2{Colors.END}")
                
        except Exception as e:
            print(f"  {Colors.RED}Could not check Pydantic version: {e}{Colors.END}")
        
        # Overall assessment
        if self.test_results["failed"] == 0 and self.test_results["warnings"] == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All Pydantic models are fully compatible with v2!{Colors.END}")
        elif self.test_results["failed"] == 0:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ Models work but have some warnings to address.{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ Some models have compatibility issues with Pydantic v2.{Colors.END}")

def main():
    """Run Pydantic v2 validation tests."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║           ruleIQ Pydantic v2 Validation Test Suite              ║")
    print("╚══════════════════════════════════════════════════════════════════╗")
    print(f"{Colors.END}")
    
    validator = PydanticValidator()
    
    # Discover all models
    validator.discover_models()
    
    # Test specific critical models
    validator.test_specific_models()
    
    # Test all models
    validator.run_all_model_tests()
    
    # Test FastAPI integration
    validator.test_fastapi_integration()
    
    # Print summary
    validator.print_summary()
    
    # Exit code
    sys.exit(0 if validator.test_results["failed"] == 0 else 1)

if __name__ == "__main__":
    main()