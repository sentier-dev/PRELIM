"""
Life cycle impact assessment (LCIA).

Calculates environmental impacts from life cycle inventories using
TRACI 2.1 characterization factors.
"""

from typing import Dict, List
from prelim.lca.inventory import LifeCycleInventory
from prelim.data.traci_factors import get_traci_factors


class ImpactAssessment:
    """
    Performs life cycle impact assessment using TRACI 2.1.
    
    Impact categories:
    - Global Warming (kg CO2 eq)
    - Acidification (kg SO2 eq)
    - Particulate Matter (kg PM2.5 eq)
    - Eutrophication (kg N eq)
    - Ozone Depletion (kg CFC-11 eq)
    - Smog Formation (kg O3 eq)
    - Human Toxicity - Cancer (CTUcancer)
    - Human Toxicity - Non-cancer (CTUnoncancer)
    - Ecotoxicity (CTUeco)
    """
    
    def __init__(self):
        """Initialize impact assessment with TRACI factors."""
        self.traci = get_traci_factors()
        self.impact_categories = self.traci.impact_categories
    
    def calculate_impacts(self, inventory: LifeCycleInventory) -> Dict[str, float]:
        """
        Calculate impact scores for all categories.
        
        Args:
            inventory: LifeCycleInventory to assess
            
        Returns:
            Dictionary mapping impact category names to scores
        """
        impacts = {category: 0.0 for category in self.impact_categories}
        
        # Process each inventory entry
        for entry in inventory.entries:
            flow_name = entry.flow.name
            compartment = entry.flow.compartment
            amount = entry.amount
            
            # Get characterization factors for this flow
            factors = self.traci.get_all_factors(flow_name, compartment)
            
            if factors:
                # Multiply amount by each characterization factor
                for category in self.impact_categories:
                    factor = factors.get(category, 0)
                    if factor and factor != 0:
                        impacts[category] += amount * factor
        
        return impacts
    
    def calculate_single_impact(self, inventory: LifeCycleInventory, 
                               category: str) -> float:
        """
        Calculate impact score for a single category.
        
        Args:
            inventory: LifeCycleInventory to assess
            category: Impact category name
            
        Returns:
            Impact score
        """
        if category not in self.impact_categories:
            raise ValueError(f"Unknown impact category: {category}")
        
        score = 0.0
        
        for entry in inventory.entries:
            flow_name = entry.flow.name
            compartment = entry.flow.compartment
            amount = entry.amount
            
            factor = self.traci.get_factor(flow_name, compartment, category)
            if factor and factor != 0:
                score += amount * factor
        
        return score
    
    def get_impact_breakdown(self, inventory: LifeCycleInventory, 
                            category: str) -> Dict[str, float]:
        """
        Get breakdown of contributions to an impact category.
        
        Args:
            inventory: LifeCycleInventory to assess
            category: Impact category name
            
        Returns:
            Dictionary mapping flow names to their contribution
        """
        if category not in self.impact_categories:
            raise ValueError(f"Unknown impact category: {category}")
        
        breakdown = {}
        
        for entry in inventory.entries:
            flow_name = entry.flow.name
            compartment = entry.flow.compartment
            amount = entry.amount
            
            factor = self.traci.get_factor(flow_name, compartment, category)
            if factor and factor != 0:
                contribution = amount * factor
                key = f"{flow_name} ({compartment})"
                if key in breakdown:
                    breakdown[key] += contribution
                else:
                    breakdown[key] = contribution
        
        return breakdown
    
    def normalize_impacts(self, impacts: Dict[str, float], 
                         functional_unit: float = 1.0) -> Dict[str, float]:
        """
        Normalize impact scores to a functional unit.
        
        Args:
            impacts: Dictionary of impact scores
            functional_unit: Functional unit value (e.g., 1 MJ of fuel)
            
        Returns:
            Normalized impact scores
        """
        return {
            category: score / functional_unit 
            for category, score in impacts.items()
        }


def assess_refinery_impacts(inventory: LifeCycleInventory) -> Dict[str, float]:
    """
    Convenience function to assess refinery impacts.
    
    Args:
        inventory: Life cycle inventory for refinery process
        
    Returns:
        Dictionary of impact scores for all TRACI categories
    """
    assessment = ImpactAssessment()
    return assessment.calculate_impacts(inventory)

