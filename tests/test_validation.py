"""Validation test to ensure test infrastructure is working"""

import pytest
import os


def test_basic_functionality():
    """Basic test to validate test infrastructure"""
    assert True


def test_environment_setup():
    """Test that environment is properly configured"""
    assert os.getenv("ENVIRONMENT") == "testing"


@pytest.mark.unit
def test_unit_marker():
    """Test that unit marker works"""
    assert 1 + 1 == 2


def test_python_path():
    """Test that Python path is set correctly"""
    import sys

    current_dir = os.getcwd()
    assert current_dir in sys.path


def test_imports_work():
    """Test that basic imports work"""
    try:
        from config.settings import settings

        assert settings is not None
        assert settings.environment.value == "testing"
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")
