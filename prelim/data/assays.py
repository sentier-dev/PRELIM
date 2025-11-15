"""
Crude oil assay data and loader.

Contains data for 650+ crude oil assays with their distillation curves and properties.
Extracted from the Assay Inventory sheet of PRELIM_v1.6.xlsm.
"""

import json
import os
from typing import Dict, List, Any, Optional


class CrudeAssay:
    """
    Represents a single crude oil assay with its properties and fractions.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize from assay data dictionary.
        
        Args:
            data: Dictionary with assay name, properties, fractions, etc.
        """
        self.name = data['name']
        self.assay_number = data.get('assay_number')
        self.fractions = data['fractions']
        self.cutoff_temps = data['cutoff_temps']
        self._properties = data['properties']
    
    def get_property(self, property_name: str, fraction: Optional[str] = None) -> Any:
        """
        Get a property value for a specific fraction or full crude.
        
        Args:
            property_name: Name of the property (e.g., 'API gravity', 'Sulfur')
            fraction: Name of the fraction (e.g., 'Naphtha', 'Diesel') or None for full crude
            
        Returns:
            Property value or None if not found
        """
        if property_name not in self._properties:
            return None
        
        prop_data = self._properties[property_name]
        
        if fraction is None:
            # Return full crude value (first in list)
            return prop_data['values'][0] if prop_data['values'] else None
        
        # Find fraction index
        try:
            idx = self.fractions.index(fraction)
            return prop_data['values'][idx] if idx < len(prop_data['values']) else None
        except ValueError:
            return None
    
    def get_all_properties(self, fraction: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all properties for a specific fraction or full crude.
        
        Args:
            fraction: Name of the fraction or None for full crude
            
        Returns:
            Dictionary of property names to values
        """
        result = {}
        
        if fraction is None:
            idx = 0  # Full crude is first
        else:
            try:
                idx = self.fractions.index(fraction)
            except ValueError:
                return result
        
        for prop_name, prop_data in self._properties.items():
            if idx < len(prop_data['values']):
                result[prop_name] = {
                    'value': prop_data['values'][idx],
                    'units': prop_data['units']
                }
        
        return result
    
    def list_properties(self) -> List[str]:
        """Get list of all available properties."""
        return list(self._properties.keys())
    
    def __repr__(self):
        return f"CrudeAssay(name='{self.name}', assay_number={self.assay_number})"


class AssayInventory:
    """
    Container for all crude oil assays.
    
    Provides methods to search and access crude oil assay data.
    """
    
    def __init__(self):
        """Load assay inventory from JSON file."""
        data_file = os.path.join(os.path.dirname(__file__), 'assay_inventory.json')
        with open(data_file, 'r') as f:
            assay_list = json.load(f)
        
        self._assays = {assay['name']: CrudeAssay(assay) for assay in assay_list}
        self._by_number = {
            assay['assay_number']: CrudeAssay(assay) 
            for assay in assay_list 
            if assay.get('assay_number') is not None
        }
    
    def get_assay(self, name: str) -> Optional[CrudeAssay]:
        """
        Get an assay by name.
        
        Args:
            name: Exact name of the crude assay
            
        Returns:
            CrudeAssay object or None if not found
        """
        return self._assays.get(name)
    
    def get_assay_by_number(self, assay_number: int) -> Optional[CrudeAssay]:
        """
        Get an assay by its number.
        
        Args:
            assay_number: Assay number
            
        Returns:
            CrudeAssay object or None if not found
        """
        return self._by_number.get(assay_number)
    
    def list_assays(self) -> List[str]:
        """Get list of all assay names."""
        return list(self._assays.keys())
    
    def search_assays(self, search_term: str) -> List[str]:
        """
        Search for assays by name.
        
        Args:
            search_term: String to search for (case-insensitive)
            
        Returns:
            List of matching assay names
        """
        search_lower = search_term.lower()
        return [name for name in self._assays.keys() if search_lower in name.lower()]
    
    def count(self) -> int:
        """Get total number of assays."""
        return len(self._assays)
    
    def __len__(self):
        return len(self._assays)
    
    def __getitem__(self, name: str) -> CrudeAssay:
        return self._assays[name]


# Singleton instance
_inventory = None

def get_assay_inventory() -> AssayInventory:
    """Get the singleton AssayInventory instance."""
    global _inventory
    if _inventory is None:
        _inventory = AssayInventory()
    return _inventory

