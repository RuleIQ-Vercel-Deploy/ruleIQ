"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

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

    def run_doppler_command(self, args: List[str]) ->Tuple[bool, str]:
        """Execute a Doppler CLI command and return result."""
        try:
            result = subprocess.run(['doppler'] + args, capture_output=True,
                text=True, check=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f'Error: {e.stderr}'

    def verify_secret_access(self, secret_name: str) ->Dict:
        """Verify individual secret accessibility."""
        verification = {'secret_name': secret_name, 'timestamp': datetime.
            now().isoformat(), 'accessible': False, 'format_valid': False,
            'value_present': False, 'validation_details': {}}
        success, value = self.run_doppler_command(['secrets', 'get',
            secret_name, '--plain'])
        if success:
            verification['accessible'] = True
            verification['value_present'] = bool(value.strip())
            verification['format_valid'], verification['validation_details'
                ] = self.validate_secret_format(secret_name, value.strip())
        else:
            verification['validation_details']['error'] = value
        return verification

    def validate_secret_format(self, secret_name: str, value: str) ->Tuple[
        bool, Dict]:
        """Validate secret format based on its type."""
        validation = {}
        valid = False
        if any(pattern in secret_name for pattern in ['_URL', '_URI', '_HOST']
            ):
            if secret_name.endswith('_HOST'):
                valid = bool(re.match('^[a-zA-Z0-9.-]+$', value))
                validation['type'] = 'hostname'
                validation['pattern_match'] = valid
            else:
                try:
                    result = urlparse(value)
                    valid = all([result.scheme, result.netloc])
                    validation['type'] = 'url'
                    validation['has_scheme'] = bool(result.scheme)
                    validation['has_netloc'] = bool(result.netloc)
                except (ValueError, KeyError, IndexError):
                    valid = False
                    validation['type'] = 'url'
                    validation['parse_error'] = True
        elif '_PORT' in secret_name:
            try:
                port = int(value)
                valid = 1 <= port <= 65535
                validation['type'] = 'port'
                validation['port_value'] = port
                validation['in_valid_range'] = valid
            except (ValueError, TypeError):
                valid = False
                validation['type'] = 'port'
                validation['parse_error'] = True
        elif secret_name in ['DEBUG', 'ENABLE_AI_FEATURES',
            'ENABLE_EMAIL_NOTIFICATIONS', 'ENABLE_FILE_UPLOAD', 'ENABLE_OAUTH'
            ]:
            valid = value.lower() in ['true', 'false', '1', '0', 'yes', 'no']
            validation['type'] = 'boolean'
            validation['valid_boolean'] = valid
        elif any(pattern in secret_name for pattern in ['_SIZE', '_TIMEOUT',
            '_RECYCLE', '_OVERFLOW', '_MINUTES', '_DAYS', '_WORKERS']):
            try:
                num = float(value)
                valid = num >= 0
                validation['type'] = 'numeric'
                validation['numeric_value'] = num
                validation['non_negative'] = valid
            except (ValueError, TypeError):
                valid = False
                validation['type'] = 'numeric'
                validation['parse_error'] = True
        elif any(pattern in secret_name for pattern in ['_KEY', '_TOKEN',
            '_SECRET', 'PASSWORD']):
            valid = len(value) >= 8
            validation['type'] = 'secret_key'
            validation['length'] = len(value)
            validation['meets_minimum_length'] = valid
            validation['contains_special_chars'] = bool(re.search(
                '[^a-zA-Z0-9]', value))
        elif '_VERSION' in secret_name:
            valid = bool(re.match('^v?\\d+(\\.\\d+)*.*$', value))
            validation['type'] = 'version'
            validation['valid_format'] = valid
        else:
            valid = bool(value)
            validation['type'] = 'string'
            validation['non_empty'] = valid
            validation['length'] = len(value)
        return valid, validation

    def verify_environment_configs(self) ->List[Dict]:
        """Verify environment-specific configurations."""
        environments = ['dev', 'staging', 'production']
        config_results = []
        for env in environments:
            config = {'environment': env, 'exists': False, 'accessible': 
                False, 'secret_count': 0, 'locked': False}
            success, output = self.run_doppler_command(['configs',
                '--project', 'ruleiq', '--json'])
            if success:
                try:
                    configs = json.loads(output)
                    env_configs = [c for c in configs if c.get('name') == env]
                    if env_configs:
                        config['exists'] = True
                        config['locked'] = env_configs[0].get('locked', False)
                        success, output = self.run_doppler_command([
                            'secrets', '--config', env, '--only-names',
                            '--json'])
                        if success:
                            config['accessible'] = True
                            secrets = json.loads(output)
                            config['secret_count'] = len(secrets)
                except json.JSONDecodeError:
                    pass
            config_results.append(config)
        return config_results

    def test_runtime_injection(self) ->Dict:
        """Test automatic secret injection at runtime."""
        test_result = {'cli_injection': False, 'sdk_available': False,
            'fallback_mechanism': False}
        success, output = self.run_doppler_command(['run', '--', 'echo',
            '$DATABASE_URL'])
        test_result['cli_injection'] = success and output.strip(
            ) != '$DATABASE_URL'
        try:
            import doppler_sdk
            test_result['sdk_available'] = True
        except ImportError:
            test_result['sdk_available'] = False
        test_result['fallback_mechanism'] = os.path.exists('.env'
            ) or os.path.exists('.env.local')
        return test_result

    def generate_report(self) ->str:
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
        success, output = self.run_doppler_command(['secrets',
            '--only-names', '--json'])
        if success:
            secrets = json.loads(output)
            for secret_name in secrets:
                result = self.verify_secret_access(secret_name)
                self.verification_results.append(result)
                status_icons = {'accessible': '✅' if result['accessible'] else
                    '❌', 'format': '✅' if result['format_valid'] else '⚠️',
                    'value': '✅' if result['value_present'] else '❌'}
                details = result['validation_details']
                detail_str = f"Type: {details.get('type', 'unknown')}"
                report += f"""| {secret_name} | {status_icons['accessible']} | {status_icons['format']} | {status_icons['value']} | {detail_str} |
"""
        report += '\n## 3. Environment Configuration Status\n\n'
        report += (
            '| Environment | Exists | Accessible | Secret Count | Locked |\n')
        report += (
            '|-------------|--------|------------|--------------|--------|\n')
        env_configs = self.verify_environment_configs()
        for config in env_configs:
            report += (
                f"| {config['environment']} | {'✅' if config['exists'] else '❌'} | ",
                )
            report += (
                f"{'✅' if config['accessible'] else '❌'} | {config['secret_count']} | ",
                )
            report += f"{'🔒' if config['locked'] else '🔓'} |\n"
        report += '\n## 4. Runtime Injection Verification\n\n'
        injection_test = self.test_runtime_injection()
        report += f"""- **CLI Injection**: {'✅ Working' if injection_test['cli_injection'] else '❌ Not Working'}
"""
        report += f"""- **Python SDK**: {'✅ Available' if injection_test['sdk_available'] else '❌ Not Installed'}
"""
        report += f"""- **Fallback Mechanism**: {'✅ Present' if injection_test['fallback_mechanism'] else '⚠️ No .env file'}
"""
        report += '\n## 5. Recommendations\n\n'
        critical_secrets = ['DATABASE_URL', 'JWT_SECRET_KEY', 'SECRET_KEY']
        missing_critical = []
        for secret in critical_secrets:
            result = next((r for r in self.verification_results if r[
                'secret_name'] == secret), None)
            if result and not result['value_present']:
                missing_critical.append(secret)
        if missing_critical:
            report += (
                f"⚠️ **Critical secrets missing values**: {', '.join(missing_critical)}\n\n",
                )
        format_issues = [r['secret_name'] for r in self.
            verification_results if not r['format_valid']]
        if format_issues:
            report += (
                f"⚠️ **Secrets with format issues**: {', '.join(format_issues[:5])}\n\n",
                )
        if not injection_test['sdk_available']:
            report += (
                '📦 **Install Doppler Python SDK**: `pip install doppler-sdk`\n\n',
                )
        total_secrets = len(self.verification_results)
        accessible = sum(1 for r in self.verification_results if r[
            'accessible'])
        valid_format = sum(1 for r in self.verification_results if r[
            'format_valid'])
        has_value = sum(1 for r in self.verification_results if r[
            'value_present'])
        report += f'\n## 6. Verification Metrics\n\n'
        report += f'- **Total Secrets**: {total_secrets}\n'
        report += f"""- **Accessible**: {accessible}/{total_secrets} ({accessible * 100 // total_secrets}%)
"""
        report += f"""- **Valid Format**: {valid_format}/{total_secrets} ({valid_format * 100 // total_secrets}%)
"""
        report += f"""- **Has Value**: {has_value}/{total_secrets} ({has_value * 100 // total_secrets}%)
"""
        return report

    def save_verification_results(self) ->None:
        """Save detailed verification results to JSON."""
        results = {'timestamp': self.timestamp, 'project': 'ruleiq',
            'verification_results': self.verification_results,
            'environment_configs': self.verify_environment_configs(),
            'runtime_injection': self.test_runtime_injection()}
        with open('doppler_verification_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(
            '✅ Detailed results saved to doppler_verification_results.json')


def main() ->int:
    """Main execution function."""
    logger.info('🔍 Starting Doppler Secrets Verification...')
    logger.info('=' * 50)
    verifier = DopplerSecretsVerifier()
    report = verifier.generate_report()
    with open('doppler_verification_report.md', 'w') as f:
        f.write(report)
    logger.info('✅ Verification report saved to doppler_verification_report.md',
        )
    verifier.save_verification_results()
    logger.info('\n📊 Verification Summary:')
    total = len(verifier.verification_results)
    accessible = sum(1 for r in verifier.verification_results if r[
        'accessible'])
    logger.info('  - Total Secrets: %s' % total)
    logger.info('  - Accessible: %s/%s' % (accessible, total))
    if accessible == total:
        logger.info('✅ All secrets are accessible!')
        return 0
    else:
        logger.info('⚠️  %s secrets are not accessible' % (total - accessible))
        return 1


if __name__ == '__main__':
    sys.exit(main())
