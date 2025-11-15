"""
Integration tests using reference data from Excel.

These tests validate that the Python implementation produces results
consistent with the Excel model for known test cases.
"""

import pytest
import json
import os
from pathlib import Path

# Note: Refinery calculations not fully implemented yet
# These tests will be skipped until implementation is complete


def load_test_fixture(fixture_name: str) -> dict:
    """Load a test fixture from JSON file."""
    fixture_path = Path(__file__).parent / 'fixtures' / fixture_name
    with open(fixture_path, 'r') as f:
        return json.load(f)


def assert_close(actual, expected, rtol=1e-5, atol=1e-8, name="value"):
    """
    Assert two values are close within tolerance.
    
    Args:
        actual: Actual value from Python model
        expected: Expected value from Excel
        rtol: Relative tolerance
        atol: Absolute tolerance
        name: Name of value for error message
    """
    if expected == 0:
        # For zero, use absolute tolerance only
        diff = abs(actual - expected)
        assert diff <= atol, f"{name}: |{actual} - {expected}| = {diff} > {atol} (absolute)"
    else:
        # For non-zero, use relative tolerance
        rel_diff = abs((actual - expected) / expected)
        assert rel_diff <= rtol, f"{name}: |({actual} - {expected})/{expected}| = {rel_diff} > {rtol} (relative)"


class TestReferenceData:
    """Test that we can load and parse reference data."""
    
    def test_load_fixture(self):
        """Test loading a test fixture."""
        fixture = load_test_fixture('tc_001_current_state.json')
        
        assert 'test_id' in fixture
        assert 'expected_results' in fixture
        assert fixture['test_id'] == 'tc_001'
    
    def test_fixture_has_product_data(self):
        """Test that fixture contains product yield data."""
        fixture = load_test_fixture('tc_001_current_state.json')
        
        products = fixture['expected_results']['products']
        
        # Check key products exist
        assert 'gasoline_vol_pct' in products
        assert 'diesel_vol_pct' in products
        assert 'jet_vol_pct' in products
        
        # Check values are reasonable (0-100%)
        assert 0 <= products['gasoline_vol_pct'] <= 1.0
        assert 0 <= products['diesel_vol_pct'] <= 1.0


@pytest.mark.skip(reason="Full calculation implementation in progress")
class TestRefineryCalculation:
    """Integration tests for refinery calculations."""
    
    def test_product_yields_match_excel(self):
        """Test that Python yields match Excel reference data."""
        from prelim import Refinery
        
        # Load reference data
        fixture = load_test_fixture('tc_001_current_state.json')
        expected = fixture['expected_results']['products']
        
        # Create refinery and set inputs
        refinery = Refinery()
        
        # Set assay (need to identify which assay from fixture)
        # For now, use a known assay
        refinery.set_crude_assay('Alaskan North Slope_Exxon')
        
        # Run calculation
        results = refinery.run()
        
        # Compare product yields
        tolerances = fixture.get('validation', {})
        rtol = tolerances.get('relative_tolerance', 1e-5)
        atol = tolerances.get('absolute_tolerance', 1e-8)
        
        # Gasoline yield
        if 'gasoline_vol_pct' in expected:
            assert_close(
                results['products']['gasoline_vol_pct'],
                expected['gasoline_vol_pct'],
                rtol=rtol, atol=atol,
                name="Gasoline volume %"
            )
        
        # Diesel yield
        if 'diesel_vol_pct' in expected:
            assert_close(
                results['products']['diesel_vol_pct'],
                expected['diesel_vol_pct'],
                rtol=rtol, atol=atol,
                name="Diesel volume %"
            )
        
        # Jet fuel yield
        if 'jet_vol_pct' in expected:
            assert_close(
                results['products']['jet_vol_pct'],
                expected['jet_vol_pct'],
                rtol=rtol, atol=atol,
                name="Jet volume %"
            )


@pytest.mark.skip(reason="Requires Excel automation or manual test case generation")
class TestMultipleAssays:
    """Test calculations across multiple crude assays."""
    
    @pytest.mark.parametrize("fixture_file", [
        "tc_001_current_state.json",
        # Add more as they are created:
        # "tc_002_alaska_heavy.json",
        # "tc_003_arab_light.json",
        # ...
    ])
    def test_assay_calculation(self, fixture_file):
        """Test calculation for a specific assay."""
        from prelim import Refinery
        
        fixture = load_test_fixture(fixture_file)
        
        # Setup and run
        refinery = Refinery()
        # ... set inputs from fixture
        results = refinery.run()
        
        # Validate all critical fields
        critical_fields = fixture['validation']['critical_fields']
        for field_path in critical_fields:
            # Parse field path like "products.gasoline_vol_pct"
            parts = field_path.split('.')
            
            # Get expected value
            expected_data = fixture['expected_results']
            for part in parts:
                expected_data = expected_data[part]
            
            # Get actual value
            actual_data = results
            for part in parts:
                actual_data = actual_data[part]
            
            # Compare
            assert_close(actual_data, expected_data, name=field_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

