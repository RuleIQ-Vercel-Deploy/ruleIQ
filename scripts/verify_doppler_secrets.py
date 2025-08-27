#!/usr/bin/env python3
"""
Doppler Secrets Verification Script
====================================
This script performs independent verification of all Doppler secrets.
Each verification is standalone and does not rely on cached or historical data.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
from urllib.parse import urlparse

class DopplerSecretsVerifier:
    """Independent verification of Doppler secrets configuration."""
    
    def __init__(self):
        self.verification_results = []
        self.timestamp = datetime.now().isoformat()
        
    def run_doppler_command(self, args: List[str]) -> Tuple[bool, str]:
        """Execute a Doppler CLI command and return result."""
        try:
            result = subprocess.run(
                ['doppler'] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e.stderr}"
    
    def verify_secret_access(self, secret_name: str) -> Dict:
        """Verify individual secret accessibility."""
        verification = {
            "secret_name": secret_name,
            "timestamp": datetime.now().isoformat(),
            "accessible": False,
            "format_valid": False,
            "value_present": False,
            "validation_details": {}
        }
        
        # Test real-time accessibility
        success, value = self.run_doppler_command(['secrets', 'get', secret_name, '--plain'])
        
        if success:
            verification["accessible"] = True
            verification["value_present"] = bool(value.strip())
            
            # Validate format based on secret type
            verification["format_valid"], verification["validation_details"] = self.validate_secret_format(
                secret_name, value.strip()
            )
        else:
            verification["validation_details"]["error"] = value
            
        return verification
    
    def validate_secret_format(self, secret_name: str, value: str) -> Tuple[bool, Dict]:
        """Validate secret format based on its type."""
        validation = {}
        valid = False
        
        # URL validation
        if any(pattern in secret_name for pattern in ['_URL', '_URI', '_HOST']):
            if secret_name.endswith('_HOST'):
                # Host validation
                valid = bool(re.match(r'^[a-zA-Z0-9.-]+$', value))
                validation["type"] = "hostname"
                validation["pattern_match"] = valid
            else:
                # URL validation
                try:
                    result = urlparse(value)
                    valid = all([result.scheme, result.netloc])
                    validation["type"] = "url"
                    validation["has_scheme"] = bool(result.scheme)
                    validation["has_netloc"] = bool(result.netloc)
                except Exception:
                    valid = False
                    validation["type"] = "url"
                    validation["parse_error"] = True
        
        # Port validation
        elif '_PORT' in secret_name:
            try:
                port = int(value)
                valid = 1 <= port <= 65535
                validation["type"] = "port"
                validation["port_value"] = port
                validation["in_valid_range"] = valid
            except (ValueError, TypeError):
                valid = False
                validation["type"] = "port"
                validation["parse_error"] = True
        
        # Boolean validation
        elif secret_name in ['DEBUG', 'ENABLE_AI_FEATURES', 'ENABLE_EMAIL_NOTIFICATIONS', 
                             'ENABLE_FILE_UPLOAD', 'ENABLE_OAUTH']:
            valid = value.lower() in ['true', 'false', '1', '0', 'yes', 'no']
            validation["type"] = "boolean"
            validation["valid_boolean"] = valid
        
        # Numeric validation
        elif any(pattern in secret_name for pattern in ['_SIZE', '_TIMEOUT', '_RECYCLE', 
                                                        '_OVERFLOW', '_MINUTES', '_DAYS', '_WORKERS']):
            try:
                num = float(value)
                valid = num >= 0
                validation["type"] = "numeric"
                validation["numeric_value"] = num
                validation["non_negative"] = valid
            except (ValueError, TypeError):
                valid = False
                validation["type"] = "numeric"
                validation["parse_error"] = True
        
        # Key/Token validation
        elif any(pattern in secret_name for pattern in ['_KEY', '_TOKEN', '_SECRET', 'PASSWORD']):
            # Check for non-empty and reasonable length
            valid = len(value) >= 8  # Minimum security requirement
            validation["type"] = "secret_key"
            validation["length"] = len(value)
            validation["meets_minimum_length"] = valid
            validation["contains_special_chars"] = bool(re.search(r'[^a-zA-Z0-9]', value))
        
        # Version validation
        elif '_VERSION' in secret_name:
            valid = bool(re.match(r'^v?\d+(\.\d+)*.*$', value))
            validation["type"] = "version"
            validation["valid_format"] = valid
        
        # Generic string validation
        else:
            valid = bool(value)  # Non-empty
            validation["type"] = "string"
            validation["non_empty"] = valid
            validation["length"] = len(value)
        
        return valid, validation
    
    def verify_environment_configs(self) -> List[Dict]:
        """Verify environment-specific configurations."""
        environments = ['dev', 'staging', 'production']
        config_results = []
        
        for env in environments:
            config = {
                "environment": env,
                "exists": False,
                "accessible": False,
                "secret_count": 0,
                "locked": False
            }
            
            # Check if environment exists
            success, output = self.run_doppler_command(['configs', '--project', 'ruleiq', '--json'])
            
            if success:
                try:
                    configs = json.loads(output)
                    env_configs = [c for c in configs if c.get('name') == env]
                    if env_configs:
                        config["exists"] = True
                        config["locked"] = env_configs[0].get('locked', False)
                        
                        # Try to access the environment
                        success, output = self.run_doppler_command(
                            ['secrets', '--config', env, '--only-names', '--json']
                        )
                        
                        if success:
                            config["accessible"] = True
                            secrets = json.loads(output)
                            config["secret_count"] = len(secrets)
                except json.JSONDecodeError:
                    pass
            
            config_results.append(config)
        
        return config_results
    
    def test_runtime_injection(self) -> Dict:
        """Test automatic secret injection at runtime."""
        test_result = {
            "cli_injection": False,
            "sdk_available": False,
            "fallback_mechanism": False
        }
        
        # Test CLI injection
        success, output = self.run_doppler_command(['run', '--', 'echo', '$DATABASE_URL'])
        test_result["cli_injection"] = success and output.strip() != '$DATABASE_URL'
        
        # Check Python SDK availability
        try:
            import doppler_sdk
            test_result["sdk_available"] = True
        except ImportError:
            test_result["sdk_available"] = False
        
        # Test fallback mechanism (check for .env file)
        test_result["fallback_mechanism"] = os.path.exists('.env') or os.path.exists('.env.local')
        
        return test_result
    
    def generate_report(self) -> str:
        """Generate comprehensive verification report."""
        report = f"""# Doppler Secrets Management Verification Report

**Generated**: {self.timestamp}
**Project**: ruleiq

## 1. Executive Summary

This report provides independent verification of all Doppler secrets configuration.
Each verification was performed standalone without relying on cached or historical data.

## 2. Secret-by-Secret Verification

| Secret Name | Accessible | Format Valid | Value Present | Details |
|-------------|------------|--------------|---------------|---------|
"""
        
        # Get all secrets
        success, output = self.run_doppler_command(['secrets', '--only-names', '--json'])
        
        if success:
            secrets = json.loads(output)
            
            for secret_name in secrets:
                result = self.verify_secret_access(secret_name)
                self.verification_results.append(result)
                
                status_icons = {
                    "accessible": "✅" if result["accessible"] else "❌",
                    "format": "✅" if result["format_valid"] else "⚠️",
                    "value": "✅" if result["value_present"] else "❌"
                }
                
                details = result["validation_details"]
                detail_str = f"Type: {details.get('type', 'unknown')}"
                
                report += f"| {secret_name} | {status_icons['accessible']} | {status_icons['format']} | {status_icons['value']} | {detail_str} |\n"
        
        # Environment configurations
        report += "\n## 3. Environment Configuration Status\n\n"
        report += "| Environment | Exists | Accessible | Secret Count | Locked |\n"
        report += "|-------------|--------|------------|--------------|--------|\n"
        
        env_configs = self.verify_environment_configs()
        for config in env_configs:
            report += f"| {config['environment']} | {'✅' if config['exists'] else '❌'} | "
            report += f"{'✅' if config['accessible'] else '❌'} | {config['secret_count']} | "
            report += f"{'🔒' if config['locked'] else '🔓'} |\n"
        
        # Runtime injection test
        report += "\n## 4. Runtime Injection Verification\n\n"
        injection_test = self.test_runtime_injection()
        
        report += f"- **CLI Injection**: {'✅ Working' if injection_test['cli_injection'] else '❌ Not Working'}\n"
        report += f"- **Python SDK**: {'✅ Available' if injection_test['sdk_available'] else '❌ Not Installed'}\n"
        report += f"- **Fallback Mechanism**: {'✅ Present' if injection_test['fallback_mechanism'] else '⚠️ No .env file'}\n"
        
        # Recommendations
        report += "\n## 5. Recommendations\n\n"
        
        # Check for missing critical secrets
        critical_secrets = ['DATABASE_URL', 'JWT_SECRET_KEY', 'SECRET_KEY']
        missing_critical = []
        
        for secret in critical_secrets:
            result = next((r for r in self.verification_results if r['secret_name'] == secret), None)
            if result and not result['value_present']:
                missing_critical.append(secret)
        
        if missing_critical:
            report += f"⚠️ **Critical secrets missing values**: {', '.join(missing_critical)}\n\n"
        
        # Check for format issues
        format_issues = [r['secret_name'] for r in self.verification_results if not r['format_valid']]
        if format_issues:
            report += f"⚠️ **Secrets with format issues**: {', '.join(format_issues[:5])}\n\n"
        
        if not injection_test['sdk_available']:
            report += "📦 **Install Doppler Python SDK**: `pip install doppler-sdk`\n\n"
        
        # Success metrics
        total_secrets = len(self.verification_results)
        accessible = sum(1 for r in self.verification_results if r['accessible'])
        valid_format = sum(1 for r in self.verification_results if r['format_valid'])
        has_value = sum(1 for r in self.verification_results if r['value_present'])
        
        report += f"\n## 6. Verification Metrics\n\n"
        report += f"- **Total Secrets**: {total_secrets}\n"
        report += f"- **Accessible**: {accessible}/{total_secrets} ({accessible*100//total_secrets}%)\n"
        report += f"- **Valid Format**: {valid_format}/{total_secrets} ({valid_format*100//total_secrets}%)\n"
        report += f"- **Has Value**: {has_value}/{total_secrets} ({has_value*100//total_secrets}%)\n"
        
        return report
    
    def save_verification_results(self):
        """Save detailed verification results to JSON."""
        results = {
            "timestamp": self.timestamp,
            "project": "ruleiq",
            "verification_results": self.verification_results,
            "environment_configs": self.verify_environment_configs(),
            "runtime_injection": self.test_runtime_injection()
        }
        
        with open('doppler_verification_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("✅ Detailed results saved to doppler_verification_results.json")

def main():
    """Main execution function."""
    print("🔍 Starting Doppler Secrets Verification...")
    print("=" * 50)
    
    verifier = DopplerSecretsVerifier()
    
    # Generate report
    report = verifier.generate_report()
    
    # Save report
    with open('doppler_verification_report.md', 'w') as f:
        f.write(report)
    
    print("✅ Verification report saved to doppler_verification_report.md")
    
    # Save detailed JSON results
    verifier.save_verification_results()
    
    # Print summary
    print("\n📊 Verification Summary:")
    total = len(verifier.verification_results)
    accessible = sum(1 for r in verifier.verification_results if r['accessible'])
    print(f"  - Total Secrets: {total}")
    print(f"  - Accessible: {accessible}/{total}")
    
    if accessible == total:
        print("✅ All secrets are accessible!")
        return 0
    else:
        print(f"⚠️  {total - accessible} secrets are not accessible")
        return 1

if __name__ == "__main__":
    sys.exit(main())