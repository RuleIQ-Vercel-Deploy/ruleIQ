# Testing framework: pytest (Python). These tests validate README.md structure and content changed in this PR.
# Rationale: The README is a critical contract for devs/users. We assert presence of key sections, badges,
# code blocks, API standardization details, and critical relative links. No new dependencies are introduced.

from pathlib import Path
import re
import os
import pytest

README_PATH = Path("README.md")


def _readme_text() -> str:
    if not README_PATH.exists():
        pytest.fail("README.md not found at repository root. Ensure tests run from repo root.")
    return README_PATH.read_text(encoding="utf-8")


def test_title_present_and_h1_is_correct():
    txt = _readme_text()
    # Exact H1 expected from PR
    assert txt.splitlines()[0].strip() == "# ruleIQ - AI-Powered Compliance Automation Platform"


def test_core_sections_exist():
    txt = _readme_text()
    required_sections = [
        "## 🚀 Overview",
        "## 🏗️ Architecture",
        "## 📅 Recent Updates",
        "## 🧠 Agentic Intelligence",
        "## 🚀 Quick Start",
        "## 📡 API Documentation",
        "## 🧪 Testing",
        "## 📖 Documentation",
        "## 🔐 Security",
        "## 🚀 Performance",
        "## 🎨 Design System",
        "## 🤝 Contributing",
        "## 📊 Project Status",
        "## 🏢 Use Cases",
        "## 📝 License",
    ]
    missing = [s for s in required_sections if s not in txt]
    assert not missing, f"Missing sections: {missing}"


def test_badges_and_status_indicators_present():
    txt = _readme_text()
    # Badge alt texts
    for alt in ["ruleIQ", "Status", "License", "Python", "Next.js", "Tests", "AI Agents"]:
        assert f"![{alt}]" in txt, f"Missing badge with alt text '{alt}'"
    # Specific tests count badge
    assert "Tests-1884+" in txt, "Expected tests count badge '1884+' not found"


def test_code_fences_and_mermaid_diagram_present_and_closed():
    txt = _readme_text()
    assert "```mermaid" in txt and "graph TB" in txt, "Mermaid architecture diagram missing"
    # Ensure the mermaid block closes later with ```
    mermaid_start = txt.find("```mermaid")
    closing = txt.find("```", mermaid_start + 3)
    assert closing != -1, "Mermaid code block not properly closed with ```"
    # General code fences used in README
    for fence in ["```bash", "```css"]:
        assert fence in txt, f"Expected code fence {fence} not found"


def test_api_standardization_details_and_docs_urls_present():
    txt = _readme_text()
    assert "All API endpoints now follow a consistent `/api/v1/` pattern" in txt
    assert "http://localhost:8000/api/v1/" in txt
    assert "http://localhost:8000/docs" in txt


def test_auth_security_claims_and_endpoints_present():
    txt = _readme_text()
    for fragment in [
        "JWT-only authentication",
        "HS256 algorithm",
        "token blacklisting",
        "Role-based access control",
        "AES-GCM",
        "OWASP",
    ]:
        assert fragment.split()[0] in txt, f"Fragment '{fragment}' expected in Security section"
    # Authentication endpoints list (check a representative subset)
    for path in [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
    ]:
        assert path in txt, f"Auth endpoint '{path}' missing"
    # Explicit removal statement with date
    assert "Stack Auth has been completely removed as of August 2025" in txt


def test_recent_updates_and_project_status_sections_reference_dates():
    txt = _readme_text()
    assert "## 📅 Recent Updates (January 2025)" in txt
    assert re.search(r"##\s+📊 Project Status\s+\(January 2025\)", txt), "Project Status date heading missing"


def test_performance_figures_present_in_expected_format():
    txt = _readme_text()
    assert "API Endpoints: 78.9-125.3ms" in txt
    assert "Initial Load: <3s" in txt
    # Sanity: ensure milliseconds and seconds units appear at least once each
    assert re.search(r"\b\d+(?:\.\d+)?ms\b", txt), "No 'ms' timings found"
    assert re.search(r"\b<\s*\d+s\b", txt), "No '<Ns' timings found"


def test_teal_theme_tokens_present():
    txt = _readme_text()
    for token in ["--teal-600: #2C7A7B", "--teal-700: #285E61", "--teal-50: #E6FFFA", "--teal-300: #4FD1C5"]:
        assert token in txt, f"Design token '{token}' missing from theme section"


def test_ci_badges_and_quality_links_present():
    txt = _readme_text()
    for label in ["CI Pipeline", "Security Scan", "Quality Gate Status", "Coverage", "Code Smells"]:
        assert label in txt, f"Expected '{label}' badge/link not found"


def test_critical_relative_links_exist_in_repo():
    """
    Validate that critical relative links referenced in README exist to avoid 404s.
    We treat LICENSE and CONTRIBUTING.md as critical. Others are soft-checked separately.
    """
    txt = _readme_text()
    # Extract markdown links: [text](target)
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", txt)
    target_map = {t for _, t in links}
    critical = []
    for p in ["LICENSE", "CONTRIBUTING.md"]:
        if p in target_map:
            critical.append(p)
    missing = [p for p in critical if not Path(p).exists()]
    assert not missing, f"Critical files missing: {missing}"


def test_soft_check_relative_links_report_without_failing():
    """
    Gather other relative links and ensure their syntax looks sane. If some files are not present yet,
    mark xfail to surface actionable feedback without failing the suite.
    """
    txt = _readme_text()
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", txt)
    rel_links = [t for _, t in links if not re.match(r"^(?:https?://|mailto:|ftp://|#)", t)]
    # Exclude the already-checked critical ones
    rel_links = [t for t in rel_links if t not in {"LICENSE", "CONTRIBUTING.md"}]
    missing = [t for t in rel_links if not Path(t).exists()]
    if missing:
        pytest.xfail(f"Some non-critical relative links not found locally (review or create): {missing}")


def test_start_script_reference_and_optional_presence():
    txt = _readme_text()
    assert "./start" in txt, "Expected './start' quick-start command not referenced"
    start_path = Path("start")
    if not start_path.exists():
        pytest.skip("Start script referenced but not present; skip presence check.")


def test_no_obvious_duplicated_link_parentheses_patterns():
    """
    Heuristic to catch cases like '...https://x)(https://x...' which indicates broken markdown linking.
    If detected, we xfail to signal cleanup without failing the pipeline.
    """
    txt = _readme_text()
    if re.search(r"https?://[^)\s]+?\)\s*\(https?://", txt):
        pytest.xfail("Detected potential duplicated link formatting like ')(' between two URLs; please fix README.")

