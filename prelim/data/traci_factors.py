"""
TRACI 2.1 characterization factors for life cycle impact assessment.

Extracted from the TRACI CFs sheet of PRELIM_v1.6.xlsm.
"""

import os
import pandas as pd
from typing import Dict, Optional


class TRACIFactors:
    """
    TRACI 2.1 characterization factors for environmental impact assessment.
    
    Includes factors for:
    - Global Warming (kg CO2 eq / kg)
    - Acidification (kg SO2 eq / kg)
    - Particulate Matter (kg PM2.5 eq / kg)
    - Eutrophication (kg N eq / kg)
    - Ozone Depletion (kg CFC-11 eq / kg)
    - Smog (kg O3 eq / kg)
    - Human Toxicity (CTUcancer, CTUnoncancer)
    - Ecotoxicity (CTUeco)
    """
    
    def __init__(self):
        """Load TRACI factors from CSV file."""
        data_file = os.path.join(os.path.dirname(__file__), 'traci_factors.csv')
        self._df = pd.read_csv(data_file)
        
        # Create lookup by flow name
        self._by_flow = {}
        for _, row in self._df.iterrows():
            flow_name = row.get('Flow')
            compartment = row.get('Compartment')
            if flow_name and compartment:
                key = f"{compartment}:{flow_name}"
                self._by_flow[key] = row.to_dict()
    
    def get_factor(self, flow_name: str, compartment: str, 
                   impact_category: str) -> Optional[float]:
        """
        Get characterization factor for a specific flow and impact category.
        
        Args:
            flow_name: Name of the elementary flow
            compartment: Environmental compartment (e.g., 'air', 'water', 'soil')
            impact_category: Impact category column name (e.g., 'kg CO2 eq / kg')
            
        Returns:
            Characterization factor value or None if not found
        """
        key = f"{compartment}:{flow_name}"
        if key in self._by_flow:
            return self._by_flow[key].get(impact_category)
        return None
    
    def get_all_factors(self, flow_name: str, compartment: str) -> Optional[Dict]:
        """
        Get all characterization factors for a specific flow.
        
        Args:
            flow_name: Name of the elementary flow
            compartment: Environmental compartment
            
        Returns:
            Dictionary of all factors or None if flow not found
        """
        key = f"{compartment}:{flow_name}"
        return self._by_flow.get(key)
    
    def list_flows(self) -> list:
        """Get list of all flows with characterization factors."""
        return list(self._by_flow.keys())
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the full TRACI factors dataframe."""
        return self._df.copy()
    
    @property
    def impact_categories(self) -> list:
        """Get list of available impact category columns."""
        return [
            'kg CO2 eq / kg',
            'kg SO2 eq / kg',
            'kg PM2.5 eq / kg',
            'kg N eq / kg',
            'kg CFC-11 eq / kg',
            'kg O3 eq / kg',
            'CTUcancer / kg',
            'CTUnoncancer / kg',
            'CTUeco / kg'
        ]


# Singleton instance
_traci_factors = None

def get_traci_factors() -> TRACIFactors:
    """Get the singleton TRACIFactors instance."""
    global _traci_factors
    if _traci_factors is None:
        _traci_factors = TRACIFactors()
    return _traci_factors

