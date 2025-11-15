"""
Constants and reference parameters for refinery process units.

Extracted from the Constants sheet of PRELIM_v1.6.xlsm.
"""

import json
import os
from typing import Dict, Any, Optional


class RefineryConstants:
    """
    Container for refinery process unit constants and parameters.
    
    Provides access to default values, ranges, and units for various
    refinery process parameters.
    """
    
    def __init__(self):
        """Load constants data from JSON file."""
        data_file = os.path.join(os.path.dirname(__file__), 'constants_data.json')
        with open(data_file, 'r') as f:
            self._data = json.load(f)
    
    def get_unit_data(self, unit_name: str) -> Dict[str, Any]:
        """
        Get all data for a specific process unit.
        
        Args:
            unit_name: Name of the process unit (e.g., 'Crude Unit', 'FCC')
            
        Returns:
            Dictionary containing all parameters for the unit
        """
        return self._data.get(unit_name, {})
    
    def get_parameter(self, unit_name: str, subunit: Optional[str], 
                     parameter: str, field: str = 'value') -> Any:
        """
        Get a specific parameter value.
        
        Args:
            unit_name: Name of the process unit
            subunit: Name of the subprocess (optional, use None for unit-level params)
            parameter: Name of the parameter
            field: Which field to retrieve ('value', 'min', 'max', 'default', 'units')
            
        Returns:
            The requested parameter value
        """
        unit_data = self._data.get(unit_name, {})
        
        if subunit:
            param_data = unit_data.get(subunit, {}).get(parameter, {})
        else:
            param_data = unit_data.get('_params', {}).get(parameter, {})
        
        return param_data.get(field)
    
    def list_units(self) -> list:
        """Get list of all process units with constants defined."""
        return list(self._data.keys())
    
    def list_parameters(self, unit_name: str, subunit: Optional[str] = None) -> list:
        """
        Get list of all parameters for a unit or subunit.
        
        Args:
            unit_name: Name of the process unit
            subunit: Name of the subprocess (optional)
            
        Returns:
            List of parameter names
        """
        unit_data = self._data.get(unit_name, {})
        
        if subunit:
            return list(unit_data.get(subunit, {}).keys())
        else:
            return list(unit_data.get('_params', {}).keys())


# Singleton instance
_constants = None

def get_constants() -> RefineryConstants:
    """Get the singleton RefineryConstants instance."""
    global _constants
    if _constants is None:
        _constants = RefineryConstants()
    return _constants

