"""Test versioning utilities."""

import pytest
from ..golden_datasets.versioning import is_semver


class TestSemanticVersioning:
    """Test semantic versioning validation."""

    def test_valid_semver(self):
        """Test valid semantic versions."""
        valid_versions = [
            "0.0.0",
            "1.0.0",
            "0.1.0",
            "0.0.1",
            "1.2.3",
            "10.20.30",
            "99.99.99",
            "2.0.0",
            "1.10.0",
            "1.0.10",
        ]

        for version in valid_versions:
            assert is_semver(version), f"Version {version} should be valid"

    def test_invalid_semver(self):
        """Test invalid semantic versions."""
        invalid_versions = [
            "1",  # Missing minor and patch
            "1.0",  # Missing patch
            "v1.0.0",  # Has v prefix
            "1.0.0-alpha",  # Has prerelease
            "1.0.0+build",  # Has build metadata
            "1.0.0-alpha.1",  # Has prerelease with dot
            "1.0.0-rc.1+build.123",  # Has both prerelease and build
            "01.0.0",  # Leading zero in major
            "1.01.0",  # Leading zero in minor
            "1.0.01",  # Leading zero in patch
            "1.0.0.0",  # Extra version component
            "1.2",  # Missing patch
            "a.b.c",  # Non-numeric
            "1.2.3.4",  # Too many components
            "1.-2.3",  # Negative number
            "1.2.-3",  # Negative patch
            "-1.2.3",  # Negative major
            "1.2.3 ",  # Trailing space
            " 1.2.3",  # Leading space
            "1. 2.3",  # Space in middle
            "1..3",  # Missing component
            ".1.2",  # Missing major
            "1.2.",  # Missing patch
            "١.٢.٣",  # Non-ASCII digits
        ]

        for version in invalid_versions:
            assert not is_semver(version), f"Version {version} should be invalid"

    def test_edge_cases(self):
        """Test edge cases for version validation."""
        # Empty string
        assert not is_semver("")

        # Just dots
        assert not is_semver("...")
        assert not is_semver("..")
        assert not is_semver(".")

        # Zero versions
        assert is_semver("0.0.0")

        # Large numbers
        assert is_semver("999.999.999")
        assert is_semver("1000.0.0")

        # Single zeros
        assert not is_semver("0")
        assert not is_semver("0.0")

    def test_leading_zeros_rejected(self):
        """Test that leading zeros are properly rejected."""
        # According to semver, leading zeros are not allowed
        assert not is_semver("01.0.0")
        assert not is_semver("001.0.0")
        assert not is_semver("1.01.0")
        assert not is_semver("1.001.0")
        assert not is_semver("1.0.01")
        assert not is_semver("1.0.001")

        # But single zero is fine
        assert is_semver("0.0.0")
        assert is_semver("1.0.0")
        assert is_semver("0.1.0")
        assert is_semver("0.0.1")
        assert is_semver("10.0.0")
        assert is_semver("0.10.0")
        assert is_semver("0.0.10")

    def test_version_comparison_ready(self):
        """Test versions that can be compared numerically."""
        # These should all be valid and comparable
        versions = [
            "0.0.1",
            "0.1.0",
            "1.0.0",
            "1.0.1",
            "1.1.0",
            "2.0.0",
            "10.0.0",
            "10.1.0",
            "10.10.10",
        ]

        for version in versions:
            assert is_semver(version)
            # Parse to ensure numeric comparison would work
            parts = version.split(".")
            assert len(parts) == 3
            assert all(part.isdigit() for part in parts)

    def test_unicode_and_special_chars(self):
        """Test handling of unicode and special characters."""
        invalid_with_special = [
            "1→2→3",  # Arrows instead of dots
            "1•2•3",  # Bullets instead of dots
            "1×2×3",  # Multiplication signs
            "1·2·3",  # Middle dot
            "1‚2‚3",  # Different comma
            "1、2、3",  # Japanese comma
            "①.②.③",  # Circled numbers
            "1️⃣.2️⃣.3️⃣",  # Emoji numbers
        ]

        for version in invalid_with_special:
            assert not is_semver(
                version
            ), f"Version with special chars {version} should be invalid"

    def test_whitespace_handling(self):
        """Test handling of various whitespace."""
        invalid_with_whitespace = [
            "1.2.3\n",  # Newline
            "1.2.3\t",  # Tab
            "1.2.3\r",  # Carriage return
            "1\t.2.3",  # Tab in middle
            "1.2\n.3",  # Newline in middle
            "\n1.2.3",  # Leading newline
            "1.2.3 ",  # Trailing space
            " 1.2.3",  # Leading space
            "1 .2.3",  # Space before dot
            "1. 2.3",  # Space after dot
        ]

        for version in invalid_with_whitespace:
            assert not is_semver(
                version
            ), f"Version with whitespace {version} should be invalid"
