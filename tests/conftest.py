"""
Pytest configuration and fixtures for PRELIM tests.
"""

import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def excel_file_path():
    """Provide path to PRELIM Excel file."""
    return os.path.join(os.path.dirname(__file__), '..', 'PRELIM_v1.6.xlsm')


@pytest.fixture(scope="session")
def test_assay_names():
    """Provide list of test assay names."""
    return [
        'Alaskan North Slope_Exxon',
        'Access Western Blend_Crude Monitor'
    ]

