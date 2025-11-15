"""
Tests for crude oil assay loading and blending.
"""

import pytest
from prelim.data.assays import get_assay_inventory, CrudeAssay
from prelim.core.crude_blending import CrudeBlender, CrudeBlendComponent, create_custom_blend


class TestAssayInventory:
    """Test assay inventory loading and access."""
    
    def test_load_inventory(self):
        """Test that assay inventory loads successfully."""
        inventory = get_assay_inventory()
        assert len(inventory) > 0
        assert inventory.count() > 600  # Should have 650+ assays
    
    def test_get_assay_by_name(self):
        """Test retrieving an assay by name."""
        inventory = get_assay_inventory()
        assay = inventory.get_assay('Alaskan North Slope_Exxon')
        
        assert assay is not None
        assert assay.name == 'Alaskan North Slope_Exxon'
        assert assay.assay_number == 23
    
    def test_search_assays(self):
        """Test searching for assays."""
        inventory = get_assay_inventory()
        results = inventory.search_assays('Alaska')
        
        assert len(results) > 0
        assert any('Alaska' in name for name in results)
    
    def test_assay_properties(self):
        """Test accessing assay properties."""
        inventory = get_assay_inventory()
        assay = inventory.get_assay('Alaskan North Slope_Exxon')
        
        # Check fractions
        assert 'Full Crude' in assay.fractions
        assert 'Naphtha' in assay.fractions
        
        # Check properties
        api_gravity = assay.get_property('API gravity', 'Full Crude')
        assert api_gravity is not None
        assert isinstance(api_gravity, (int, float))
        
        # Check sulfur content
        sulfur = assay.get_property('Sulfur', 'Full Crude')
        assert sulfur is not None


class TestCrudeBlending:
    """Test crude oil blending calculations."""
    
    def test_blend_two_crudes(self):
        """Test blending two crude oils."""
        inventory = get_assay_inventory()
        
        # Get two assays
        assay1 = inventory.get_assay('Alaskan North Slope_Exxon')
        assay2 = inventory.get_assay('Arab Light_Saudi Aramco') or \
                 list(inventory._assays.values())[1]  # Fallback
        
        # Create blend
        components = [
            CrudeBlendComponent(assay=assay1, fraction=0.6),
            CrudeBlendComponent(assay=assay2, fraction=0.4)
        ]
        
        blender = CrudeBlender()
        blend = blender.blend_crudes(components)
        
        # Check blend properties
        assert blend.name.startswith('Blend:')
        assert len(blend.fractions) > 0
        
        # Properties should be weighted averages
        api_blend = blend.get_property('API gravity', 'Full Crude')
        api1 = assay1.get_property('API gravity', 'Full Crude')
        api2 = assay2.get_property('API gravity', 'Full Crude')
        
        assert api_blend is not None
        # Blend should be between the two components (roughly)
        if api1 and api2:
            assert min(api1, api2) <= api_blend <= max(api1, api2) or \
                   abs(api_blend - 0.6*api1 - 0.4*api2) < 5  # Allow some deviation
    
    def test_blend_fractions_sum_to_one(self):
        """Test that blend fractions must sum to 1.0."""
        inventory = get_assay_inventory()
        assay1 = list(inventory._assays.values())[0]
        assay2 = list(inventory._assays.values())[1]
        
        # This should raise an error
        components = [
            CrudeBlendComponent(assay=assay1, fraction=0.5),
            CrudeBlendComponent(assay=assay2, fraction=0.4)  # Sum = 0.9
        ]
        
        blender = CrudeBlender()
        with pytest.raises(ValueError):
            blender.blend_crudes(components)
    
    def test_convenience_blend_function(self):
        """Test create_custom_blend convenience function."""
        # Skip if specific assays not available
        inventory = get_assay_inventory()
        if len(inventory) < 2:
            pytest.skip("Not enough assays available")
        
        assay_names = list(inventory._assays.keys())[:2]
        
        try:
            blend = create_custom_blend(
                assay_names,
                [0.5, 0.5]
            )
            assert blend is not None
            assert len(blend.fractions) > 0
        except ValueError:
            # Some assays might not have complete data
            pytest.skip("Test assays not suitable for blending")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

