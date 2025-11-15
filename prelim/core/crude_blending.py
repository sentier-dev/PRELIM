"""
Crude oil blending calculations.

Converted from Blending_WeightAverageMethod VBA macro in PRELIM_v1.6.xlsm.

Implements weight-averaging method to create custom crude blends from
multiple crude oil assays.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from prelim.data.assays import CrudeAssay, get_assay_inventory


@dataclass
class CrudeBlendComponent:
    """
    A component of a crude blend.
    """
    assay: CrudeAssay
    fraction: float  # Weight fraction (0-1)
    
    def __post_init__(self):
        if not 0 <= self.fraction <= 1:
            raise ValueError(f"Fraction must be between 0 and 1, got {self.fraction}")


class CrudeBlender:
    """
    Blends multiple crude oils using weight-averaging method.
    
    This implements the logic from the Blending_WeightAverageMethod VBA macro,
    which creates a custom blended crude assay from multiple crude oils.
    """
    
    def __init__(self):
        """Initialize crude blender."""
        self.inventory = get_assay_inventory()
        self.refinery_input_vol = 100000 * 0.1589873  # m³ (default)
    
    def blend_crudes(self, components: List[CrudeBlendComponent], 
                     refinery_capacity_bpd: float = 100000) -> CrudeAssay:
        """
        Create a blended crude assay from multiple crude oils.
        
        Args:
            components: List of CrudeBlendComponent objects
            refinery_capacity_bpd: Refinery capacity in barrels per day
            
        Returns:
            New CrudeAssay representing the blended crude
        """
        if not components:
            raise ValueError("At least one crude component required")
        
        # Validate fractions sum to 1
        total_fraction = sum(c.fraction for c in components)
        if not np.isclose(total_fraction, 1.0, rtol=0.01):
            raise ValueError(f"Component fractions must sum to 1.0, got {total_fraction}")
        
        self.refinery_input_vol = refinery_capacity_bpd * 0.1589873  # Convert to m³
        
        # Get all component assays
        n_crudes = len(components)
        
        # Initialize blended assay data structure
        # Use first component's structure as template
        template_assay = components[0].assay
        fractions = template_assay.fractions
        n_fractions = len(fractions)
        
        # Collect data from all components
        component_data = []
        for comp in components:
            data = {
                'assay': comp.assay,
                'fraction': comp.fraction,
                'properties': {}
            }
            
            # Get all properties for all fractions
            for prop_name in comp.assay.list_properties():
                prop_values = []
                for frac_name in fractions:
                    val = comp.assay.get_property(prop_name, frac_name)
                    prop_values.append(val if val is not None else 0.0)
                data['properties'][prop_name] = prop_values
            
            component_data.append(data)
        
        # Perform blending calculations (following VBA logic)
        blended_properties = {}
        
        # For each property, blend across components
        for prop_name in template_assay.list_properties():
            # Different blending methods for different properties
            if prop_name == 'Density':
                # Density uses reciprocal averaging for certain fractions
                blended_values = self._blend_density(
                    component_data, prop_name, fractions
                )
            elif prop_name == 'API gravity':
                # API gravity calculated from density
                blended_values = self._blend_api_gravity(
                    component_data, prop_name, fractions
                )
            elif prop_name in ['Vol Flow', 'Mass Flow']:
                # Flow rates are volume-weighted
                blended_values = self._blend_flows(
                    component_data, prop_name, fractions
                )
            else:
                # Default: weight-averaged blending
                blended_values = self._blend_weighted_average(
                    component_data, prop_name, fractions
                )
            
            blended_properties[prop_name] = blended_values
        
        # Create new CrudeAssay object for blended crude
        blend_name = self._create_blend_name(components)
        
        blend_data = {
            'name': blend_name,
            'assay_number': None,
            'fractions': fractions,
            'cutoff_temps': template_assay.cutoff_temps,
            'properties': {}
        }
        
        # Format properties in the expected structure
        for prop_name, values in blended_properties.items():
            # Get units from first component
            units = component_data[0]['assay']._properties[prop_name]['units']
            blend_data['properties'][prop_name] = {
                'units': units,
                'values': values
            }
        
        return CrudeAssay(blend_data)
    
    def _blend_weighted_average(self, component_data: List[Dict], 
                                prop_name: str, fractions: List[str]) -> List[float]:
        """
        Blend property using simple weight averaging.
        
        This is the default method for most properties.
        """
        n_fractions = len(fractions)
        blended = [0.0] * n_fractions
        
        for i in range(n_fractions):
            weighted_sum = 0.0
            for comp_data in component_data:
                if prop_name in comp_data['properties']:
                    value = comp_data['properties'][prop_name][i]
                    weight = comp_data['fraction']
                    weighted_sum += value * weight
            blended[i] = weighted_sum
        
        return blended
    
    def _blend_density(self, component_data: List[Dict], 
                      prop_name: str, fractions: List[str]) -> List[float]:
        """
        Blend density using harmonic mean (reciprocal averaging).
        
        Following VBA: blend as 1/density then take reciprocal.
        """
        n_fractions = len(fractions)
        blended = [0.0] * n_fractions
        
        for i in range(n_fractions):
            # Calculate normalized density contributions
            reciprocal_sum = 0.0
            
            for comp_data in component_data:
                if prop_name in comp_data['properties']:
                    density = comp_data['properties'][prop_name][i]
                    if density > 0:
                        # Get corresponding volume fraction for this component
                        vol_flow_values = comp_data['properties'].get('Vol Flow', [])
                        if i < len(vol_flow_values) and vol_flow_values[i] > 0:
                            weight = comp_data['fraction']
                            reciprocal_sum += weight / density
            
            # Take reciprocal to get blended density
            if reciprocal_sum > 0:
                blended[i] = 1.0 / reciprocal_sum
            else:
                blended[i] = 0.0
        
        return blended
    
    def _blend_api_gravity(self, component_data: List[Dict],
                          prop_name: str, fractions: List[str]) -> List[float]:
        """
        Blend API gravity.
        
        API gravity is derived from density:
        API = 141.5 / specific_gravity - 131.5
        where specific_gravity = density / 999.105
        """
        # First blend densities
        densities = self._blend_density(component_data, 'Density', fractions)
        
        # Convert to API gravity
        api_values = []
        for density in densities:
            if density > 0:
                specific_gravity = density / 999.105
                api = 141.5 / specific_gravity - 131.5
                api_values.append(api)
            else:
                api_values.append(0.0)
        
        return api_values
    
    def _blend_flows(self, component_data: List[Dict],
                    prop_name: str, fractions: List[str]) -> List[float]:
        """
        Blend flow rates (volume or mass).
        
        Flow rates are summed according to component fractions.
        """
        n_fractions = len(fractions)
        blended = [0.0] * n_fractions
        
        # For blended crude at refinery capacity
        for i in range(n_fractions):
            flow_sum = 0.0
            for comp_data in component_data:
                if prop_name in comp_data['properties']:
                    flow = comp_data['properties'][prop_name][i]
                    weight = comp_data['fraction']
                    flow_sum += flow * weight
            blended[i] = flow_sum
        
        return blended
    
    def _create_blend_name(self, components: List[CrudeBlendComponent]) -> str:
        """Create a name for the blended crude."""
        if len(components) == 1:
            return components[0].assay.name
        
        # Create name from components
        names = []
        for comp in components:
            # Take first part of assay name
            name_part = comp.assay.name.split('_')[0][:15]
            percent = int(comp.fraction * 100)
            names.append(f"{name_part}({percent}%)")
        
        return "Blend: " + " + ".join(names)


def create_custom_blend(crude_names: List[str], 
                       fractions: List[float],
                       refinery_capacity_bpd: float = 100000) -> CrudeAssay:
    """
    Convenience function to create a custom crude blend.
    
    Args:
        crude_names: List of crude assay names to blend
        fractions: List of weight fractions (must sum to 1.0)
        refinery_capacity_bpd: Refinery capacity in barrels per day
        
    Returns:
        CrudeAssay representing the blended crude
        
    Example:
        >>> blend = create_custom_blend(
        ...     ['Alaskan North Slope_Exxon', 'Arab Light_Saudi Aramco'],
        ...     [0.6, 0.4]
        ... )
    """
    inventory = get_assay_inventory()
    
    # Get assays
    components = []
    for name, fraction in zip(crude_names, fractions):
        assay = inventory.get_assay(name)
        if not assay:
            # Try searching
            matches = inventory.search_assays(name)
            if matches:
                assay = inventory.get_assay(matches[0])
            else:
                raise ValueError(f"Crude assay not found: {name}")
        
        components.append(CrudeBlendComponent(assay=assay, fraction=fraction))
    
    blender = CrudeBlender()
    return blender.blend_crudes(components, refinery_capacity_bpd)

