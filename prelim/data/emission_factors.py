"""
Emission factors for refinery processes.

Extracted from the Emission Factors sheet of PRELIM_v1.6.xlsm.
Note: This sheet has a complex structure with multiple data tables and toggles.
"""

import json
import os
from typing import Dict, Any, Optional


class EmissionFactors:
    """
    Container for emission factors data.
    
    The Emission Factors sheet contains:
    - Emission factor toggles (power source, upstream emissions, etc.)
    - Energy requirements for steam and hydrogen production
    - Carbon and sulfur ratios
    - Various emission factors by scenario
    """
    
    def __init__(self):
        """Load emission factors data from JSON file."""
        data_file = os.path.join(os.path.dirname(__file__), 'emission_factors_raw.json')
        with open(data_file, 'r') as f:
            self._raw_data = json.load(f)
    
    def get_raw_data(self) -> list:
        """
        Get the raw data matrix from the Emission Factors sheet.
        
        Returns:
            List of rows (each row is a list of values)
        """
        return self._raw_data
    
    # TODO: Add specific getter methods as the calculation logic is implemented
    # This will require understanding how the Excel formulas use these factors


# Singleton instance
_emission_factors = None

def get_emission_factors() -> EmissionFactors:
    """Get the singleton EmissionFactors instance."""
    global _emission_factors
    if _emission_factors is None:
        _emission_factors = EmissionFactors()
    return _emission_factors

