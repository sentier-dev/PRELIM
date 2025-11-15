"""
Tests for data loading modules.
"""

import pytest
from prelim.data.constants import get_constants
from prelim.data.traci_factors import get_traci_factors
from prelim.data.energy_conversions import get_energy_conversions


class TestConstants:
    """Test constants data loader."""
    
    def test_load_constants(self):
        """Test that constants load successfully."""
        constants = get_constants()
        assert constants is not None
        
        # Check that we have some units
        units = constants.list_units()
        assert len(units) > 0
        assert 'Crude Unit' in units or any('Crude' in u for u in units)
    
    def test_get_unit_data(self):
        """Test retrieving unit data."""
        constants = get_constants()
        
        # Try to get Crude Unit data
        cdu_data = constants.get_unit_data('Crude Unit')
        assert cdu_data is not None


class TestTRACIFactors:
    """Test TRACI characterization factors."""
    
    def test_load_traci_factors(self):
        """Test that TRACI factors load successfully."""
        traci = get_traci_factors()
        assert traci is not None
        
        # Check impact categories
        categories = traci.impact_categories
        assert 'kg CO2 eq / kg' in categories
        assert 'kg SO2 eq / kg' in categories
    
    def test_get_co2_factor(self):
        """Test retrieving CO2 characterization factor."""
        traci = get_traci_factors()
        
        # CO2 should have GWP of 1.0
        factor = traci.get_factor('Carbon dioxide', 'air', 'kg CO2 eq / kg')
        assert factor == 1.0
    
    def test_get_methane_factor(self):
        """Test retrieving methane characterization factor."""
        traci = get_traci_factors()
        
        # Methane should have GWP around 30 (100-year horizon)
        factor = traci.get_factor('Methane', 'air', 'kg CO2 eq / kg')
        assert factor is not None
        assert 25 < factor < 35  # Roughly GWP100 = 30


class TestEnergyConversions:
    """Test energy conversion factors."""
    
    def test_load_conversions(self):
        """Test that energy conversions load successfully."""
        conv = get_energy_conversions()
        assert conv is not None
        assert len(conv.conversions) > 0
    
    def test_bbl_to_m3_conversion(self):
        """Test barrel to cubic meter conversion."""
        conv = get_energy_conversions()
        
        # 1 barrel = 0.159 m³
        result = conv.convert(1.0, 'bbl', 'm3')
        assert 0.158 < result < 0.160
    
    def test_kwh_to_mj_conversion(self):
        """Test kWh to MJ conversion."""
        conv = get_energy_conversions()
        
        # 1 kWh = 3.6 MJ
        result = conv.convert(1.0, 'kwh', 'mj')
        assert result == 3.6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

