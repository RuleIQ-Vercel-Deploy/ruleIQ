#!/usr/bin/env python3
"""
Context Change Detection and Monitoring Script

This script monitors file system changes and identifies when context documentation
should be updated based on code changes that affect architectural understanding.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import hashlib

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


class ContextMonitor:
    """Monitor file changes and detect context-affecting modifications."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self.context_dir = project_root / "docs" / "context"
        self.config_file = self.context_dir / "monitor_config.json"
        self.state_file = self.context_dir / "monitor_state.json"

        # Load configuration
        self.config = self._load_config()
        self.state = self._load_state()

    def _load_config(self) -> Dict:
        """Load monitoring configuration."""
        default_config = {
            "watched_patterns": [
                # Backend critical files
                "api/routers/*.py",
                "services/**/*.py",
                "database/*.py",
                "config/*.py",
                "alembic/versions/*.py",
                # Frontend critical files
                "frontend/app/**/*.tsx",
                "frontend/components/**/*.tsx",
                "frontend/lib/stores/*.ts",
                "frontend/lib/api/*.ts",
                "frontend/types/*.ts",
                # Configuration files
                "docker-compose.yml",
                "requirements.txt",
                "frontend/package.json",
                "frontend/next.config.mjs",
                "frontend/tailwind.config.ts",
                # Documentation files
                "*.md",
                "docs/**/*.md",
            ],
            "context_triggers": {
                "database": {
                    "patterns": ["database/*.py", "alembic/versions/*.py"],
                    "context_files": ["DATABASE_CONTEXT.md"],
                    "impact": "high",
                },
                "api": {
                    "patterns": ["api/routers/*.py", "api/middleware/*.py"],
                    "context_files": ["API_CONTEXT.md", "ARCHITECTURE_CONTEXT.md"],
                    "impact": "medium",
                },
                "ai_services": {
                    "patterns": ["services/ai/*.py"],
                    "context_files": ["AI_SERVICES_CONTEXT.md"],
                    "impact": "high",
                },
                "frontend": {
                    "patterns": [
                        "frontend/app/**/*.tsx",
                        "frontend/components/**/*.tsx",
                        "frontend/lib/**/*.ts",
                    ],
                    "context_files": ["FRONTEND_CONTEXT.md"],
                    "impact": "medium",
                },
                "testing": {
                    "patterns": ["tests/**/*.py", "frontend/tests/**/*.ts*"],
                    "context_files": ["TESTING_CONTEXT.md"],
                    "impact": "low",
                },
                "architecture": {
                    "patterns": ["config/*.py", "docker-compose.yml", "main.py"],
                    "context_files": ["ARCHITECTURE_CONTEXT.md"],
                    "impact": "high",
                },
            },
            "excluded_patterns": [
                "__pycache__/**",
                "node_modules/**",
                ".git/**",
                "*.pyc",
                "*.log",
                ".next/**",
                "venv/**",
            ],
        }

        if self.config_file.exists():
            with open(self.config_file) as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            # Create default config
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def _load_state(self) -> Dict:
        """Load previous monitoring state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"file_hashes": {}, "last_scan": None, "context_updates_needed": []}

    def _save_state(self):
        """Save current monitoring state."""
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for change detection."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except (OSError, IOError):
            return ""

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file matches a glob pattern."""
        from fnmatch import fnmatch

        relative_path = str(file_path.relative_to(self.project_root))
        return fnmatch(relative_path, pattern)

    def _is_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded from monitoring."""
        for pattern in self.config["excluded_patterns"]:
            if self._matches_pattern(file_path, pattern):
                return True
        return False

    def _should_monitor_file(self, file_path: Path) -> bool:
        """Check if file should be monitored for changes."""
        if self._is_excluded(file_path):
            return False

        for pattern in self.config["watched_patterns"]:
            if self._matches_pattern(file_path, pattern):
                return True
        return False

    def scan_for_changes(self) -> Dict[str, List[Path]]:
        """Scan for file changes and categorize by context area."""
        changes_by_area = {}

        # Scan all files in project
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._is_excluded(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file

                if not self._should_monitor_file(file_path):
                    continue

                current_hash = self._get_file_hash(file_path)
                relative_path = str(file_path.relative_to(self.project_root))
                previous_hash = self.state["file_hashes"].get(relative_path)

                # Check for changes
                if current_hash != previous_hash:
                    self.state["file_hashes"][relative_path] = current_hash

                    # Categorize change by context area
                    for area, config in self.config["context_triggers"].items():
                        for pattern in config["patterns"]:
                            if self._matches_pattern(file_path, pattern):
                                if area not in changes_by_area:
                                    changes_by_area[area] = []
                                changes_by_area[area].append(file_path)
                                break

        self.state["last_scan"] = datetime.now().isoformat()
        self._save_state()

        return changes_by_area

    def analyze_change_impact(self, changes_by_area: Dict[str, List[Path]]) -> List[Dict]:
        """Analyze the impact of detected changes."""
        impact_analysis = []

        for area, changed_files in changes_by_area.items():
            area_config = self.config["context_triggers"][area]

            analysis = {
                "area": area,
                "impact_level": area_config["impact"],
                "changed_files": [str(f.relative_to(self.project_root)) for f in changed_files],
                "context_files_affected": area_config["context_files"],
                "timestamp": datetime.now().isoformat(),
                "recommendations": self._get_update_recommendations(area, changed_files),
            }

            impact_analysis.append(analysis)

        return impact_analysis

    def _get_update_recommendations(self, area: str, changed_files: List[Path]) -> List[str]:
        """Generate context update recommendations for changed files."""
        recommendations = []

        # Area-specific recommendations
        if area == "database":
            recommendations.extend(
                [
                    "Review database schema changes for migration impact",
                    "Update model relationship documentation",
                    "Verify foreign key constraint changes",
                    "Check for performance index impacts",
                ]
            )
        elif area == "ai_services":
            recommendations.extend(
                [
                    "Update AI model configuration documentation",
                    "Review circuit breaker pattern changes",
                    "Document new AI tool integrations",
                    "Update performance optimization metrics",
                ]
            )
        elif area == "api":
            recommendations.extend(
                [
                    "Update OpenAPI specification",
                    "Review authentication/authorization changes",
                    "Document new endpoint functionality",
                    "Update rate limiting configuration",
                ]
            )
        elif area == "frontend":
            recommendations.extend(
                [
                    "Update component architecture documentation",
                    "Review state management changes",
                    "Document new user interface patterns",
                    "Update accessibility compliance status",
                ]
            )
        elif area == "architecture":
            recommendations.extend(
                [
                    "Update system architecture diagrams",
                    "Review infrastructure configuration changes",
                    "Document deployment impact",
                    "Update technology stack documentation",
                ]
            )

        # File-specific recommendations
        for file_path in changed_files:
            file_name = file_path.name
            if file_name.endswith(".py") and "test" not in file_name:
                recommendations.append(f"Review business logic changes in {file_name}")
            elif file_name.endswith(".tsx") or file_name.endswith(".ts"):
                recommendations.append(f"Review frontend component changes in {file_name}")
            elif file_name.endswith(".json") and "package" in file_name:
                recommendations.append("Review dependency changes and security implications")

        return list(set(recommendations))  # Remove duplicates

    def generate_change_report(self, impact_analysis: List[Dict]) -> str:
        """Generate a markdown report of detected changes."""
        if not impact_analysis:
            return "No context-affecting changes detected."

        report_lines = [
            "# Context Change Detection Report",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Changes Detected**: {len(impact_analysis)} areas affected",
            "",
        ]

        # Sort by impact level
        impact_order = {"high": 0, "medium": 1, "low": 2}
        sorted_analysis = sorted(
            impact_analysis, key=lambda x: impact_order.get(x["impact_level"], 3)
        )

        for analysis in sorted_analysis:
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                analysis["impact_level"], "⚪"
            )

            report_lines.extend(
                [
                    f"## {impact_emoji} {analysis['area'].title()} Changes ({analysis['impact_level'].upper()} IMPACT)",
                    "",
                    f"**Files Changed**: {len(analysis['changed_files'])}",
                    f"**Context Files Affected**: {', '.join(analysis['context_files_affected'])}",
                    "",
                    "### Changed Files",
                    "",
                ]
            )

            for file_path in analysis["changed_files"]:
                report_lines.append(f"- `{file_path}`")

            report_lines.extend(["", "### Recommended Context Updates", ""])

            for recommendation in analysis["recommendations"]:
                report_lines.append(f"- {recommendation}")

            report_lines.append("")

        # Add action items
        report_lines.extend(
            ["## Required Actions", "", "### High Priority (Update Immediately)", ""]
        )

        high_impact_areas = [a for a in sorted_analysis if a["impact_level"] == "high"]
        if high_impact_areas:
            for analysis in high_impact_areas:
                for context_file in analysis["context_files_affected"]:
                    report_lines.append(f"- [ ] Update `docs/context/{context_file}`")
        else:
            report_lines.append("- No high-impact changes requiring immediate updates")

        report_lines.extend(["", "### Medium Priority (Update Within Week)", ""])

        medium_impact_areas = [a for a in sorted_analysis if a["impact_level"] == "medium"]
        if medium_impact_areas:
            for analysis in medium_impact_areas:
                for context_file in analysis["context_files_affected"]:
                    report_lines.append(f"- [ ] Review and update `docs/context/{context_file}`")
        else:
            report_lines.append("- No medium-impact changes requiring weekly updates")

        return "\n".join(report_lines)

    def run_monitoring_cycle(self) -> str:
        """Run a complete monitoring cycle and return results."""
        print("🔍 Scanning for context-affecting changes...")

        changes_by_area = self.scan_for_changes()

        if not changes_by_area:
            print("✅ No context-affecting changes detected")
            return "No changes detected"

        print(f"📊 Analyzing impact of changes in {len(changes_by_area)} areas...")
        impact_analysis = self.analyze_change_impact(changes_by_area)

        print("📝 Generating change report...")
        report = self.generate_change_report(impact_analysis)

        # Save report
        report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.context_dir / f"change_report_{report_timestamp}.md"

        with open(report_file, "w") as f:
            f.write(report)

        print(f"📄 Change report saved: {report_file}")

        # Update change log
        self._update_change_log(impact_analysis)

        return report

    def _update_change_log(self, impact_analysis: List[Dict]):
        """Update the context change log with new changes."""
        change_log_file = self.context_dir / "CHANGE_LOG.md"

        if not change_log_file.exists():
            return

        # Read existing change log
        with open(change_log_file, "r") as f:
            content = f.read()

        # Generate new entry
        today = datetime.now().strftime("%Y-%m-%d")
        new_entry_lines = [
            f"## {today} - Automated Change Detection",
            "",
            "### **Context Updates Required**",
            f"- **Detection Time**: {datetime.now().strftime('%H:%M:%S')}",
            f"- **Areas Affected**: {len(impact_analysis)}",
            f"- **Impact**: {', '.join(set(a['impact_level'] for a in impact_analysis))}",
            "",
        ]

        for analysis in impact_analysis:
            new_entry_lines.extend(
                [
                    f"#### **{analysis['area'].title()} Changes ({analysis['impact_level'].upper()} Impact)**",
                    f"- **Files Changed**: {len(analysis['changed_files'])}",
                    f"- **Context Files**: {', '.join(analysis['context_files_affected'])}",
                    "- **Action Required**: Review and update context documentation",
                    "",
                ]
            )

        new_entry_lines.append("---\n")

        # Insert new entry after the first occurrence of "---"
        lines = content.split("\n")
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                insert_index = i + 1
                break

        # Insert the new entry
        lines[insert_index:insert_index] = new_entry_lines

        # Write back to file
        with open(change_log_file, "w") as f:
            f.write("\n".join(lines))


def main():
    """Main entry point for context monitoring."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Context Monitor Usage:

python scripts/context_monitor.py [--help]

This script monitors file changes and detects when context documentation
should be updated. It generates reports and updates change logs automatically.

The script monitors:
- Backend code changes (API, services, database)
- Frontend code changes (components, stores, types)
- Configuration changes (Docker, dependencies)
- Documentation changes

It categorizes changes by impact level and generates actionable recommendations
for updating context documentation.
        """)
        return

    try:
        monitor = ContextMonitor()
        report = monitor.run_monitoring_cycle()

        print("\n" + "=" * 60)
        print("CONTEXT CHANGE DETECTION SUMMARY")
        print("=" * 60)
        print(report)

    except Exception as e:
        print(f"❌ Error during context monitoring: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
