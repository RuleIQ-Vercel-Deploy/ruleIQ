#!/usr/bin/env python3
"""
Validate that GitHub Actions workflows follow security best practices.
This script checks for pinned actions, proper permissions, and security anti-patterns.
"""

import os
import re
import sys
import glob
import json
import yaml
from typing import Dict, List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class SecurityValidator:
    """Validator for GitHub Actions security best practices"""

    def __init__(self) -> None:
        self.issues = []
        self.warnings = []
        self.passed = []

    def validate_workflow_file(self, filepath: str) -> Dict:
        """Validate a single workflow file for security issues"""
        results = {
            'file': filepath,
            'issues': [],
            'warnings': [],
            'passed': []
        }

        print(f"\n{Colors.BLUE}Validating:{Colors.RESET} {filepath}")

        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Check for unpinned actions
        self._check_unpinned_actions(content, lines, results)

        # Check for permissions
        self._check_permissions(content, results)

        # Check for security anti-patterns
        self._check_anti_patterns(content, results)

        # Check for secrets handling
        self._check_secrets_handling(content, results)

        return results

    def _check_unpinned_actions(self, content: str, lines: List[str], results: Dict):
        """Check for unpinned action references"""
        # Pattern to find action uses
        action_pattern = re.compile(r'uses:\s*([^\s]+)')

        for i, line in enumerate(lines, 1):
            # Skip commented lines
            stripped_line = line.strip()
            if stripped_line.startswith('#'):
                continue

            match = action_pattern.search(line)
            if match:
                action = match.group(1)

                # Skip local actions
                if action.startswith('./') or action.startswith('../'):
                    continue

                # Check if action is pinned to SHA
                if '@' in action:
                    ref = action.split('@')[1]

                    # Check if it's a 40-character SHA (full commit hash)
                    sha_pattern = re.compile(r'^[a-f0-9]{40}')
                    if not sha_pattern.match(ref.split(' ')[0]):  # Handle comments after SHA
                        results['issues'].append({
                            'line': i,
                            'type': 'unpinned_action',
                            'message': f"Action '{action}' is not pinned to a commit SHA",
                            'severity': 'HIGH'
                        })
                    else:
                        results['passed'].append({
                            'line': i,
                            'type': 'pinned_action',
                            'message': f"Action '{action}' is properly pinned"
                        })
                else:
                    results['issues'].append({
                        'line': i,
                        'type': 'missing_version',
                        'message': f"Action '{action}' has no version specified",
                        'severity': 'CRITICAL'
                    })

    def _check_permissions(self, content: str, results: Dict):
        """Check for workflow permissions configuration and verify minimal permissions"""
        try:
            # Parse the workflow YAML to analyze permissions structure
            workflow = yaml.safe_load(content)
        except yaml.YAMLError:
            results['warnings'].append({
                'type': 'yaml_parse_error',
                'message': "Could not parse YAML to analyze permissions structure",
                'severity': 'LOW'
            })
            workflow = None

        if 'permissions:' not in content:
            results['warnings'].append({
                'type': 'missing_permissions',
                'message': "No permissions section found - consider adding explicit permissions",
                'severity': 'MEDIUM'
            })
        else:
            # Check for overly broad permissions
            if re.search(r'permissions:\s*write-all', content):
                results['issues'].append({
                    'type': 'broad_permissions',
                    'message': "Using 'write-all' permissions is too broad",
                    'severity': 'HIGH'
                })

            # Check for appropriate read-only defaults
            if re.search(r'permissions:\s*read-all', content):
                results['warnings'].append({
                    'type': 'broad_read_permissions',
                    'message': "Consider using more specific permissions instead of 'read-all'",
                    'severity': 'LOW'
                })

            # Analyze minimal permissions if YAML was parsed successfully
            if workflow:
                self._analyze_minimal_permissions(workflow, content, results)

            results['passed'].append({
                'type': 'has_permissions',
                'message': "Workflow has permissions section defined"
            })

    def _analyze_minimal_permissions(self, workflow: Dict, content: str, results: Dict):
        """Analyze if permissions are minimal for the workflow's needs"""
        # Check workflow-level permissions
        workflow_perms = workflow.get('permissions', {})
        jobs = workflow.get('jobs', {})

        # Check if actions/github-script is used
        uses_github_script = 'actions/github-script' in content
        uses_docker_push = 'docker/build-push-action' in content

        # Analyze workflow-level permissions
        if isinstance(workflow_perms, dict):
            # Check for unnecessary pull-requests: write at workflow level
            if workflow_perms.get('pull-requests') == 'write' and not uses_github_script:
                results['warnings'].append({
                    'type': 'unnecessary_permission',
                    'message': "Workflow has 'pull-requests: write' but doesn't appear to use actions/github-script",
                    'severity': 'MEDIUM'
                })

            # Check for unnecessary checks: write at workflow level
            if workflow_perms.get('checks') == 'write':
                has_check_creation = False
                for job_name, job in jobs.items():
                    if 'actions/github-script' in str(job):
                        # Could be creating checks
                        has_check_creation = True
                        break

                if not has_check_creation:
                    results['warnings'].append({
                        'type': 'unnecessary_permission',
                        'message': "Workflow has 'checks: write' but doesn't appear to create check runs",
                        'severity': 'MEDIUM'
                    })

            # Check for packages: write without Docker push
            if workflow_perms.get('packages') == 'write' and not uses_docker_push:
                results['warnings'].append({
                    'type': 'unnecessary_permission',
                    'message': "Workflow has 'packages: write' but doesn't appear to push Docker images",
                    'severity': 'MEDIUM'
                })

            # Recommend job-level permissions when possible
            if len(jobs) > 1:
                write_perms = [k for k, v in workflow_perms.items() if v == 'write']
                if write_perms:
                    results['warnings'].append({
                        'type': 'workflow_level_write_permissions',
                        'message': f"Consider moving write permissions ({', '.join(write_perms)}) to job level for better isolation",
                        'severity': 'LOW'
                    })

        # Check each job for appropriate permissions
        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                continue

            job_perms = job.get('permissions', {})

            # If job uses github-script and doesn't have permissions, warn
            if 'actions/github-script' in str(job) and not job_perms:
                if not workflow_perms or workflow_perms.get('pull-requests') != 'write':
                    results['warnings'].append({
                        'type': 'missing_job_permission',
                        'message': f"Job '{job_name}' uses github-script but may lack pull-requests: write permission",
                        'severity': 'MEDIUM'
                    })

    def _check_anti_patterns(self, content: str, results: Dict):
        """Check for security anti-patterns"""
        lines = content.split('\n')

        # Check for pull_request_target without safeguards
        if 'pull_request_target' in content:
            if '# SECURITY WARNING' not in content:
                results['warnings'].append({
                    'type': 'pull_request_target',
                    'message': "Using 'pull_request_target' without security warning comment",
                    'severity': 'HIGH'
                })

            # Check if there's code checkout from PR
            if 'pull_request_target' in content and 'ref: ${{ github.event.pull_request.head.sha }}' in content:
                results['issues'].append({
                    'type': 'unsafe_pr_checkout',
                    'message': "Checking out PR code with pull_request_target is dangerous",
                    'severity': 'CRITICAL'
                })

        # Check for inline scripts with user input
        if re.search(r'run:.*\$\{\{.*github\.event\..*\}\}', content):
            results['warnings'].append({
                'type': 'unescaped_user_input',
                'message': "Using GitHub event data directly in run commands - potential injection risk",
                'severity': 'HIGH'
            })

        # Check for hardcoded credentials - improved patterns for both shell and YAML style
        credential_patterns = [
            # Shell-style environment variable assignments
            (r'[A-Z_]*(?:KEY|TOKEN|SECRET|PASSWORD|APIKEY|API_KEY)[A-Z_]*\s*=\s*["\'][^"\']+["\']', 'shell-style'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'shell-style'),
            # YAML-style key-value pairs (Comment 5 fix)
            (r'^[ \t]*[A-Z_]*(?:SECRET|TOKEN|PASSWORD|KEY|APIKEY|API_KEY)[A-Z_]*:\s*["\'][^"\']+["\']', 'yaml-style'),
            (r'^[ \t]*[A-Z_]*(?:SECRET|TOKEN|PASSWORD|KEY|APIKEY|API_KEY)[A-Z_]*:\s*[^\s$]+', 'yaml-style-unquoted'),
            # Inline secrets in strings
            (r'(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\'][a-zA-Z0-9+/=_-]{16,}["\']', 'inline-secret'),
        ]

        # Skip patterns that are likely not secrets (Comment 5 improvement)
        safe_patterns = [
            r'NEXT_PUBLIC_',  # Next.js public environment variables
            r'\$\{\{.*secrets\.',  # Using GitHub secrets (not hardcoded)
            r'\$\{\{.*env\.',  # Using environment variables
            r'test[_-]?(?:secret|key|token|password)',  # Test credentials
            r'example[_-]?(?:secret|key|token|password)',  # Example credentials
        ]

        found_secrets = []
        for i, line in enumerate(lines, 1):
            # Skip commented lines
            if line.strip().startswith('#'):
                continue

            # Skip lines that use GitHub secrets or env vars (not hardcoded)
            skip_line = False
            for safe_pattern in safe_patterns:
                if re.search(safe_pattern, line, re.IGNORECASE):
                    skip_line = True
                    break

            if skip_line:
                continue

            # Check each credential pattern
            for pattern, style in credential_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    secret_text = match.group(0)

                    # Additional filtering for false positives
                    if any(safe in secret_text.upper() for safe in ['NEXT_PUBLIC_', 'EXAMPLE', 'TEST', 'DUMMY', 'PLACEHOLDER']):
                        continue

                    # Check if it looks like a real secret (has some entropy)
                    potential_secret = re.search(r'["\']([^"\']+)["\']', secret_text)
                    if potential_secret:
                        secret_value = potential_secret.group(1)
                        # Skip if it's obviously a placeholder
                        if secret_value in ['', 'xxx', '...', 'your-key-here', 'your-secret-here', 'TODO']:
                            continue

                    found_secrets.append({
                        'line': i,
                        'style': style,
                        'text': secret_text[:50] + '...' if len(secret_text) > 50 else secret_text
                    })

        # Report found secrets with line numbers
        if found_secrets:
            for secret in found_secrets[:3]:  # Report first 3 to avoid spam
                results['issues'].append({
                    'line': secret['line'],
                    'type': 'potential_hardcoded_secret',
                    'message': f"Potential hardcoded credential found ({secret['style']}): {secret['text']}",
                    'severity': 'CRITICAL'
                })

            if len(found_secrets) > 3:
                results['issues'].append({
                    'type': 'potential_hardcoded_secret',
                    'message': f"...and {len(found_secrets) - 3} more potential hardcoded credentials",
                    'severity': 'CRITICAL'
                })

    def _check_secrets_handling(self, content: str, results: Dict):
        """Check for proper secrets handling"""
        # Check if secrets are being used
        if '${{ secrets.' in content:
            results['passed'].append({
                'type': 'uses_secrets',
                'message': "Properly using GitHub secrets for sensitive data"
            })

            # Check for secrets in unsafe contexts
            if re.search(r'echo.*\$\{\{\s*secrets\.', content):
                results['issues'].append({
                    'type': 'secrets_in_logs',
                    'message': "Secrets might be exposed in logs via echo command",
                    'severity': 'HIGH'
                })

    def generate_report(self, all_results: List[Dict]) -> Tuple[bool, str]:
        """Generate a comprehensive security report"""
        total_issues = 0
        total_warnings = 0
        total_passed = 0

        report_lines = [
            f"\n{Colors.BOLD}GitHub Actions Security Validation Report{Colors.RESET}",
            "=" * 60
        ]

        for result in all_results:
            file_name = os.path.basename(result['file'])
            issues_count = len(result['issues'])
            warnings_count = len(result['warnings'])
            passed_count = len(result['passed'])

            total_issues += issues_count
            total_warnings += warnings_count
            total_passed += passed_count

            if issues_count > 0:
                status = f"{Colors.RED}✗ FAILED{Colors.RESET}"
            elif warnings_count > 0:
                status = f"{Colors.YELLOW}⚠ WARNING{Colors.RESET}"
            else:
                status = f"{Colors.GREEN}✓ PASSED{Colors.RESET}"

            report_lines.append(f"\n{file_name}: {status}")

            # Report issues
            if result['issues']:
                report_lines.append(f"  {Colors.RED}Issues:{Colors.RESET}")
                for issue in result['issues']:
                    line_info = f"line {issue['line']}" if 'line' in issue else ""
                    report_lines.append(f"    - [{issue['severity']}] {issue['message']} {line_info}")

            # Report warnings
            if result['warnings']:
                report_lines.append(f"  {Colors.YELLOW}Warnings:{Colors.RESET}")
                for warning in result['warnings']:
                    line_info = f"line {warning['line']}" if 'line' in warning else ""
                    report_lines.append(f"    - [{warning['severity']}] {warning['message']} {line_info}")

            # Report passed checks (summary only)
            if result['passed']:
                report_lines.append(f"  {Colors.GREEN}Passed:{Colors.RESET} {passed_count} checks")

        # Summary
        report_lines.extend([
            "\n" + "=" * 60,
            f"{Colors.BOLD}Summary:{Colors.RESET}",
            f"  Total Files Scanned: {len(all_results)}",
            f"  {Colors.RED}Critical Issues: {total_issues}{Colors.RESET}",
            f"  {Colors.YELLOW}Warnings: {total_warnings}{Colors.RESET}",
            f"  {Colors.GREEN}Passed Checks: {total_passed}{Colors.RESET}"
        ])

        # Recommendations
        if total_issues > 0:
            report_lines.extend([
                f"\n{Colors.BOLD}Recommendations:{Colors.RESET}",
                "1. Pin all GitHub Actions to specific commit SHAs",
                "2. Review and fix permission settings",
                "3. Remove any hardcoded credentials",
                "4. Add security comments for dangerous patterns",
                "5. Run 'python fix_github_actions_security.py' to auto-fix pinning issues"
            ])

        report = "\n".join(report_lines)

        # Return success status and report
        return total_issues == 0, report

def main():
    """Main function to validate all workflow files"""
    workflow_dir = '.github/workflows'

    if not os.path.exists(workflow_dir):
        print(f"{Colors.RED}Error:{Colors.RESET} {workflow_dir} directory not found")
        return 1

    # Find all workflow files
    workflow_files = glob.glob(os.path.join(workflow_dir, '*.yml')) + \
                    glob.glob(os.path.join(workflow_dir, '*.yaml'))

    if not workflow_files:
        print(f"{Colors.YELLOW}No workflow files found in {workflow_dir}{Colors.RESET}")
        return 0

    print(f"{Colors.BOLD}Starting GitHub Actions Security Validation{Colors.RESET}")
    print(f"Found {len(workflow_files)} workflow files to validate")

    validator = SecurityValidator()
    all_results = []

    # Validate each workflow file
    for filepath in sorted(workflow_files):
        results = validator.validate_workflow_file(filepath)
        all_results.append(results)

    # Generate and print report
    success, report = validator.generate_report(all_results)
    print(report)

    # Write detailed report to file
    report_file = 'github_actions_security_report.json'
    with open(report_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n{Colors.BLUE}Detailed report saved to:{Colors.RESET} {report_file}")

    # Exit with appropriate code
    if not success:
        print(f"\n{Colors.RED}Security validation failed!{Colors.RESET} Fix the issues and run again.")
        return 1
    else:
        print(f"\n{Colors.GREEN}All security checks passed!{Colors.RESET}")
        return 0

if __name__ == '__main__':
    sys.exit(main())
