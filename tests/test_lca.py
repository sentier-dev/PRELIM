"""
Tests for LCA modules.
"""

import pytest
from prelim.lca.flows import get_flow_registry, Flow, FlowType
from prelim.lca.inventory import LifeCycleInventory
from prelim.lca.impact_assessment import ImpactAssessment


class TestFlows:
    """Test flow registry."""
    
    def test_load_flow_registry(self):
        """Test that flow registry loads."""
        registry = get_flow_registry()
        assert registry is not None
        
        flows = registry.list_flows()
        assert len(flows) > 0
    
    def test_get_co2_flow(self):
        """Test retrieving CO2 flow."""
        registry = get_flow_registry()
        co2 = registry.get_flow('Carbon dioxide', 'air')
        
        assert co2 is not None
        assert co2.name == 'Carbon dioxide'
        assert co2.compartment == 'air'
        assert co2.flow_type == FlowType.EMISSION_AIR


class TestInventory:
    """Test life cycle inventory."""
    
    def test_create_inventory(self):
        """Test creating an inventory."""
        inv = LifeCycleInventory('Test Process')
        assert inv.name == 'Test Process'
        assert len(inv) == 0
    
    def test_add_emissions(self):
        """Test adding emissions to inventory."""
        inv = LifeCycleInventory('Test Process')
        
        # Add CO2 emission
        inv.add_emission('Carbon dioxide', 'air', 100.0, 'kg')
        
        assert len(inv) == 1
        
        # Get emissions
        emissions = inv.get_emissions('air')
        assert len(emissions) == 1
        assert emissions[0].amount == 100.0
    
    def test_add_resources(self):
        """Test adding resource inputs."""
        inv = LifeCycleInventory('Test Process')
        
        # Add natural gas
        inv.add_resource('Natural gas', 1000.0, 'm3')
        
        resources = inv.get_resources()
        assert len(resources) == 1
        assert resources[0].amount == 1000.0


class TestImpactAssessment:
    """Test impact assessment."""
    
    def test_create_assessment(self):
        """Test creating impact assessment."""
        assessment = ImpactAssessment()
        assert assessment is not None
        assert len(assessment.impact_categories) > 0
    
    def test_calculate_co2_impact(self):
        """Test calculating global warming impact."""
        inv = LifeCycleInventory('Test Process')
        inv.add_emission('Carbon dioxide', 'air', 100.0, 'kg')
        
        assessment = ImpactAssessment()
        impacts = assessment.calculate_impacts(inv)
        
        # CO2 has GWP of 1, so 100 kg CO2 = 100 kg CO2 eq
        gwp = impacts.get('kg CO2 eq / kg')
        assert gwp == 100.0
    
    def test_calculate_multiple_impacts(self):
        """Test calculating multiple impact categories."""
        inv = LifeCycleInventory('Test Process')
        inv.add_emission('Carbon dioxide', 'air', 100.0, 'kg')
        inv.add_emission('sulfur dioxide', 'air', 10.0, 'kg')
        
        assessment = ImpactAssessment()
        impacts = assessment.calculate_impacts(inv)
        
        # Should have both GWP and acidification
        assert impacts.get('kg CO2 eq / kg') > 0
        assert impacts.get('kg SO2 eq / kg') > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

