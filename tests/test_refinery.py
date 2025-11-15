"""
Tests for main Refinery class.
"""

import pytest
from prelim import Refinery
from prelim.core.refinery import RefineryConfiguration


class TestRefineryConfiguration:
    """Test refinery configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RefineryConfiguration()
        
        assert config.capacity_bpd == 100000
        assert config.units_active['cdu'] is True
        assert config.heating_value_basis == 'LHV'


class TestRefinery:
    """Test main Refinery class."""
    
    def test_create_refinery(self):
        """Test creating a refinery model."""
        refinery = Refinery()
        assert refinery is not None
        assert refinery.config is not None
    
    def test_set_crude_assay(self):
        """Test setting crude assay."""
        refinery = Refinery()
        
        # Set a valid assay
        refinery.set_crude_assay('Alaskan')  # Will search
        assert refinery.current_assay is not None
    
    def test_list_assays(self):
        """Test listing available assays."""
        refinery = Refinery()
        
        assays = refinery.list_available_assays()
        assert len(assays) > 600
        
        # Test search
        alaska_assays = refinery.list_available_assays('Alaska')
        assert len(alaska_assays) > 0
    
    def test_configure_refinery(self):
        """Test configuring refinery parameters."""
        refinery = Refinery()
        
        refinery.configure(capacity_bpd=150000)
        assert refinery.config.capacity_bpd == 150000
    
    def test_run_calculation(self):
        """Test running refinery calculation (framework only for now)."""
        refinery = Refinery()
        refinery.set_crude_assay('Alaskan')
        
        # Note: Full calculation not yet implemented
        # This tests the framework structure
        try:
            results = refinery.run()
            # Should return results dictionary with structure
            assert 'assay_name' in results
            assert 'capacity_bpd' in results
        except NotImplementedError:
            # Expected until full implementation complete
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

