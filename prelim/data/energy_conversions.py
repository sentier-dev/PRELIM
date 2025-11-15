"""
Energy and unit conversion factors.

Contains heating values, density conversions, and other unit conversion
factors used throughout the refinery model.

Extracted from the Energy & Unit Conversions sheet of PRELIM_v1.6.xlsm.
"""

import json
import os
from typing import Dict, Any, Optional


class EnergyConversions:
    """
    Container for energy and unit conversion factors.
    
    Includes:
    - Lower and Higher Heating Values (LHV/HHV) for fuels
    - Density conversions
    - Carbon content ratios
    - Unit conversions (Btu, MJ, kWh, etc.)
    """
    
    def __init__(self):
        """Load energy conversion data from JSON file."""
        data_file = os.path.join(os.path.dirname(__file__), 'energy_conversions_raw.json')
        with open(data_file, 'r') as f:
            self._raw_data = json.load(f)
        
        # Common conversion factors (can be expanded)
        self.conversions = {
            'bbl_to_m3': 0.158987294928,
            'scf_to_m3': 0.0283168466,
            'btu_to_mj': 0.00105505585262,
            'kwh_to_mj': 3.6,
            'lb_to_kg': 0.45359237,
            'gal_to_m3': 0.00378541178,
        }
    
    def get_raw_data(self) -> list:
        """
        Get the raw data matrix from the Energy & Unit Conversions sheet.
        
        Returns:
            List of rows (each row is a list of values)
        """
        return self._raw_data
    
    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert between common energy and volume units.
        
        Args:
            value: Value to convert
            from_unit: Source unit (e.g., 'bbl', 'MJ')
            to_unit: Target unit (e.g., 'm3', 'kWh')
            
        Returns:
            Converted value
        """
        key = f"{from_unit}_to_{to_unit}"
        if key in self.conversions:
            return value * self.conversions[key]
        
        # Try reverse conversion
        reverse_key = f"{to_unit}_to_{from_unit}"
        if reverse_key in self.conversions:
            return value / self.conversions[reverse_key]
        
        raise ValueError(f"No conversion available from {from_unit} to {to_unit}")
    
    # TODO: Add specific getter methods for heating values, densities, etc.


# Singleton instance
_energy_conversions = None

def get_energy_conversions() -> EnergyConversions:
    """Get the singleton EnergyConversions instance."""
    global _energy_conversions
    if _energy_conversions is None:
        _energy_conversions = EnergyConversions()
    return _energy_conversions

