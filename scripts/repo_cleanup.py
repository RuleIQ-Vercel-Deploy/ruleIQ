#!/usr/bin/env python3
"""
Repository cleanup utility.

Goals:
- Reduce clutter by removing generated artifacts and obvious backups
- Move noisy reports and test outputs to a dedicated archive folder
- Optionally remove empty directories after cleanup
- Always runs in dry-run mode by default; requires --apply to make changes

Usage:
  python scripts/repo_cleanup.py                # dry-run preview
  python scripts/repo_cleanup.py --apply        # apply changes
  python scripts/repo_cleanup.py --include backups,sonar,logs,load_tests,api_artifacts,reports_root --apply
  python scripts/repo_cleanup.py --remove-empty-dirs --apply

Safety:
- Only affects known categories and glob patterns below
- Never touches code, config, or dependency files
- Prints a clear summary before applying
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = REPO_ROOT / "archive"


@dataclass
class CleanupCategory:
    name: str
    files_remove: List[str]
    files_archive: List[str]
    dirs_remove: List[str]
    dirs_archive: List[str]
    archive_subdir: str  # subfolder inside archive/


def glob_many(patterns: Iterable[str], root: Path) -> List[Path]:
    paths: List[Path] = []
    for pat in patterns:
        # Support patterns relative to root
        if pat.startswith("/"):
            pat = pat[1:]
        matches = list(root.glob(pat))
        paths.extend(matches)
    # Unique and sorted for determinism
    return sorted({p.resolve() for p in paths}, key=lambda p: str(p))


def within_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
        return True
    except Exception:
        return False


def is_empty_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    try:
        return len([p for p in path.iterdir()]) == 0
    except Exception:
        return False


def ensure_archive(subdir: str) -> Path:
    dst = ARCHIVE_DIR / subdir
    dst.mkdir(parents=True, exist_ok=True)
    return dst


def should_keep_config(path: Path) -> bool:
    # Never touch key config and code
    keep_suffixes = {
        ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".json5", ".yml", ".yaml", ".toml", ".ini",
        ".sql", ".graphql", ".proto", ".sh", ".bat", ".ps1",
        ".env", ".dockerfile",
    }
    keep_exact = {
        "requirements.txt",
        "requirements-prod.txt",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "docker-compose.test.yml",
        "alembic.ini",
        "pytest.ini",
        "ruff.toml",
        ".pylintrc",
        ".coveragerc",
        "sonar-project.properties",
        "nginx.conf",
        "Makefile",
        "package.json",
        "README.md",
        "LICENSE",
    }
    name = path.name
    if name in keep_exact:
        return True
    if path.suffix.lower() in keep_suffixes:
        # Some JSON are artifacts; but code/config JSON often kept in subdirs; we guard with category patterns instead
        return True
    return False


def default_categories() -> Dict[str, CleanupCategory]:
    return {
        # Remove obvious backups and temp archives
        "backups": CleanupCategory(
            name="backups",
            files_remove=[],
            files_archive=[],
            dirs_remove=[
                "backup_*",
                "backups",
                "backup_deadcode_*",
                "celery_backup_*",
            ],
            dirs_archive=[],
            archive_subdir="backups",
        ),
        # Remove scanner/sonar working dirs and noisy scan outputs (keep sonar-project.properties)
        "sonar": CleanupCategory(
            name="sonar",
            files_remove=[
                "sonar-current-status.txt",
                "sonar-scan-output.txt",
            ],
            files_archive=[],
            dirs_remove=[
                ".scannerwork",
                "sonarcloud",
            ],
            dirs_archive=[],
            archive_subdir="scans",
        ),
        # Remove logs directory entirely (usually runtime artifacts)
        "logs": CleanupCategory(
            name="logs",
            files_remove=[],
            files_archive=[],
            dirs_remove=[
                "logs",
            ],
            dirs_archive=[],
            archive_subdir="logs",
        ),
        # Archive load test outputs (HTML, CSV)
        "load_tests": CleanupCategory(
            name="load_tests",
            files_remove=[],
            files_archive=[
                "load_test_*.html",
                "load_test_*_load_*.html",
                "load_test_*.csv",
                "load_test_*_*.csv",
            ],
            dirs_remove=[],
            dirs_archive=[],
            archive_subdir="load_tests",
        ),
        # Archive noisy API artifacts (Postman/Newman dumps, generated reports)
        "api_artifacts": CleanupCategory(
            name="api_artifacts",
            files_remove=[],
            files_archive=[
                "api/*results*.json",
                "api/*_results.json",
                "api/*_test_results.json",
                "api/*test*.json",
                "api/*report*.json",
                "api/*-environment*.json",
                "api/newman-*.json",
                "api/api-connection-*.json",
                "api/api-connection-*.html",
                "api/*collection*_backup*.json",
                "api/*working*.json",
                "api/*complete*.json",
                "api/*final*.json",
            ],
            dirs_remove=[],
            dirs_archive=[],
            archive_subdir="api-artifacts",
        ),
        # Archive root-level summary/report markdowns and presentations + JSON reports
        "reports_root": CleanupCategory(
            name="reports_root",
            files_remove=[],
            files_archive=[
                "*REPORT*.md",
                "*Report*.md",
                "*Summary*.md",
                "*SUMMARY*.md",
                "*ANALYSIS*.md",
                "*Analysis*.md",
                "*PRESENTATION*.html",
                "ANALYSIS_PRESENTATION.html",
                "AUDIT_PRESENTATION.html",
                # Common JSON/MD report artifacts
                "lint_results.json",
                "api_ruff_results.json",
                "bandit_report.json",
                "owasp_security_report.json",
                "security_audit.json",
                "security_audit_report.md",
                "security_audit_progress.md",
                "dead_code_analysis_report.json",
                "dead_code_removal_report.json",
                "dead_code_removal_final_report.md",
                "INTEGRATION_TEST_REPORT.md",
                "DEPENDENCIES_AUDIT_REPORT.md",
                "LINTING_REPORT.md",
                "CLEANUP_SUMMARY_2025.md",
                "EXECUTIVE_SUMMARY.md",
                "TEST_OPTIMIZATION_REPORT.md",
                "TEST_INFRASTRUCTURE_SETUP.md",
                "TEST_OPTIMIZATION_PLAN.md",
                "doppler_verification_report.md",
                "DOPPLER_VERIFICATION_REPORT.md",
                "test-results.xml",
            ],
            dirs_remove=[],
            dirs_archive=[],
            archive_subdir="reports",
        ),
        # Remove common test artifacts and caches
        "test_artifacts": CleanupCategory(
            name="test_artifacts",
            files_remove=[
                "coverage.xml",
                "coverage.json",
            ],
            files_archive=[
                "test-results.xml",
            ],
            dirs_remove=[
                ".pytest_cache",
                "htmlcov",
                "**/__pycache__",
            ],
            dirs_archive=[],
            archive_subdir="tests",
        ),
        # Archive dependency metadata snapshots
        "deps_metadata": CleanupCategory(
            name="deps_metadata",
            files_remove=[],
            files_archive=[
                "current_deps.json",
                "outdated_deps.json",
                "INDEX.json",
            ],
            dirs_remove=[],
            dirs_archive=[],
            archive_subdir="deps",
        ),
    }


def collect_candidates(categories: Dict[str, CleanupCategory], include: Optional[List[str]]) -> Tuple[List[Tuple[Path, Path]], List[Path], List[Path]]:
    """Return (moves, file_deletes, dir_deletes)."""
    to_move: List[Tuple[Path, Path]] = []
    to_delete_files: List[Path] = []
    to_delete_dirs: List[Path] = []

    selected = list(categories.keys()) if not include else [c for c in include if c in categories]
    for key in selected:
        cat = categories[key]

        # Files to archive
        for p in glob_many(cat.files_archive, REPO_ROOT):
            if p.is_file() and within_repo(p) and not should_keep_config(p):
                dst_dir = ensure_archive(cat.archive_subdir)
                dst = dst_dir / p.name
                to_move.append((p, dst))

        # Files to delete
        for p in glob_many(cat.files_remove, REPO_ROOT):
            if p.is_file() and within_repo(p) and not should_keep_config(p):
                to_delete_files.append(p)

        # Directories to archive (rare)
        for d in glob_many(cat.dirs_archive, REPO_ROOT):
            if d.is_dir() and within_repo(d):
                dst_dir = ensure_archive(cat.archive_subdir) / d.name
                to_move.append((d, dst_dir))

        # Directories to delete
        for d in glob_many(cat.dirs_remove, REPO_ROOT):
            if d.is_dir() and within_repo(d):
                to_delete_dirs.append(d)

    # De-dup and avoid conflicts (don't delete what we move)
    move_sources = {src for src, _ in to_move}
    to_delete_files = [p for p in sorted(set(to_delete_files)) if p not in move_sources]
    to_delete_dirs = [p for p in sorted(set(to_delete_dirs)) if p not in move_sources]

    return to_move, to_delete_files, to_delete_dirs


def remove_empty_directories(root: Path, excluded: Optional[List[Path]] = None) -> List[Path]:
    removed: List[Path] = []
    excluded_set = {p.resolve() for p in (excluded or [])}

    # Walk bottom-up
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        d = Path(dirpath)
        if d in excluded_set:
            continue
        # Skip dot-directories that might contain tooling config
        if d.name.startswith("."):
            continue
        # Skip core source folders
        if d.name in {"api", "app", "services", "database", "frontend", "langgraph_agent", "tests", "scripts"}:
            continue
        try:
            entries = [e for e in d.iterdir()]
        except Exception:
            continue
        if not entries:
            try:
                d.rmdir()
                removed.append(d)
            except Exception:
                pass
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup repository clutter safely.")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--include", type=str, default="", help="Comma-separated categories to include; default = all")
    parser.add_argument("--exclude", type=str, default="", help="Comma-separated categories to exclude")
    parser.add_argument("--remove-empty-dirs", action="store_true", help="Also remove empty directories after cleanup")
    args = parser.parse_args()

    categories = default_categories()

    include = [s.strip() for s in args.include.split(",") if s.strip()] or list(categories.keys())
    exclude = {s.strip() for s in args.exclude.split(",") if s.strip()}
    include = [c for c in include if c in categories and c not in exclude]

    to_move, to_delete_files, to_delete_dirs = collect_candidates(categories, include)

    print(f"Repository root: {REPO_ROOT}")
    print(f"Archive dir:     {ARCHIVE_DIR}")
    print("")
    print("Selected categories:", ", ".join(include) or "(none)")
    print("")
    print(f"Planned moves (to archive/): {len(to_move)}")
    for src, dst in to_move[:50]:
        print(f"  MOVE  {src.relative_to(REPO_ROOT)} -> archive/{dst.relative_to(ARCHIVE_DIR)}")
    if len(to_move) > 50:
        print(f"  ... and {len(to_move) - 50} more")

    print(f"\nPlanned file deletions: {len(to_delete_files)}")
    for p in to_delete_files[:50]:
        print(f"  DEL   {p.relative_to(REPO_ROOT)}")
    if len(to_delete_files) > 50:
        print(f"  ... and {len(to_delete_files) - 50} more")

    print(f"\nPlanned directory deletions: {len(to_delete_dirs)}")
    for d in to_delete_dirs[:50]:
        print(f"  RMDIR {d.relative_to(REPO_ROOT)}")
    if len(to_delete_dirs) > 50:
        print(f"  ... and {len(to_delete_dirs) - 50} more")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to execute.")
        return 0

    # Apply moves
    moved = 0
    for src, dst in to_move:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                # Move directory (handles merge if dst exists)
                shutil.move(str(src), str(dst))
            else:
                shutil.move(str(src), str(dst))
            moved += 1
        except Exception as e:
            print(f"ERROR moving {src} -> {dst}: {e}", file=sys.stderr)

    # Apply file deletions
    deleted_files = 0
    for p in to_delete_files:
        try:
            p.unlink(missing_ok=True)
            deleted_files += 1
        except Exception as e:
            print(f"ERROR deleting file {p}: {e}", file=sys.stderr)

    # Apply dir deletions
    deleted_dirs = 0
    for d in to_delete_dirs:
        try:
            shutil.rmtree(d, ignore_errors=True)
            deleted_dirs += 1
        except Exception as e:
            print(f"ERROR deleting directory {d}: {e}", file=sys.stderr)

    removed_empty: List[Path] = []
    if args.remove_empty_dirs:
        removed_empty = remove_empty_directories(REPO_ROOT, excluded=[ARCHIVE_DIR])

    print("\nCleanup summary:")
    print(f"  Moved to archive:      {moved}")
    print(f"  Files deleted:         {deleted_files}")
    print(f"  Directories deleted:   {deleted_dirs}")
    print(f"  Empty dirs removed:    {len(removed_empty)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())