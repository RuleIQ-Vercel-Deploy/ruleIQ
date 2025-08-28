#!/usr/bin/env python
import os
import sys
import pytest

# Force test database
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5433/compliance_test'
os.environ['TEST_DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5433/compliance_test'

# Remove Doppler
for key in list(os.environ.keys()):
    if 'DOPPLER' in key:
        del os.environ[key]

# Run with maximum verbosity
sys.exit(pytest.main([
    'tests/database/test_freemium_models.py::TestConversionEvent::test_create_conversion_event',
    '-vvs',
    '--tb=long',
    '--capture=no'
]))
