"""
Main Refinery class - primary API for PRELIM model.

This is the high-level interface for running refinery calculations.
"""

from typing import Dict, Any, Optional, List
from prelim.data.assays import get_assay_inventory, CrudeAssay
from prelim.data.constants import get_constants
from prelim.core.process_units import create_process_unit
from prelim.core.calculations import CalculationEngine
from prelim.core.crude_blending import CrudeBlender


class RefineryConfiguration:
    """
    Configuration for refinery model.
    
    Defines which process units are active and their parameters.
    """
    
    def __init__(self):
        """Initialize default configuration."""
        # Process units to include
        self.units_active = {
            'cdu': True,  # Crude Distillation Unit
            'vdu': True,  # Vacuum Distillation Unit
            'fcc': True,  # Fluid Catalytic Cracker
            'coker': True,  # Delayed Coker
            'hydrocracker': False,  # Hydrocracker (optional)
            'hydrotreaters': {
                'naphtha': True,
                'kerosene': True,
                'diesel': True,
                'fcc_feed': False,
            },
            'reformer': True,  # Catalytic Reformer
            'smr': True,  # Steam Methane Reformer (H2 production)
        }
        
        # Refinery capacity
        self.capacity_bpd = 100000  # barrels per day
        
        # Heating values
        self.heating_value_basis = 'LHV'  # 'LHV' or 'HHV'
        
        # Emission factors
        self.power_source = 'ng_fired'  # 'coal', 'ng_fired', 'low_carbon'
        self.include_upstream = True
        self.emissions_controls = True


class Refinery:
    """
    Main refinery model class.
    
    Orchestrates all refinery process calculations, from crude input
    through processing to final products and environmental impacts.
    
    Example usage:
        >>> from prelim import Refinery
        >>> refinery = Refinery()
        >>> refinery.set_crude_assay('Alaskan North Slope_Exxon')
        >>> refinery.configure(capacity_bpd=150000)
        >>> results = refinery.run()
        >>> print(results['products'])
    """
    
    def __init__(self, config: Optional[RefineryConfiguration] = None):
        """
        Initialize a new refinery model.
        
        Args:
            config: RefineryConfiguration object (uses default if None)
        """
        self.config = config or RefineryConfiguration()
        self.inventory = get_assay_inventory()
        self.constants = get_constants()
        
        self.current_assay: Optional[CrudeAssay] = None
        self.inputs = {}
        self.results = {}
        
        # Calculation engine
        self.calc_engine = CalculationEngine()
        
        # Process units (created on demand)
        self._process_units = {}
    
    def set_crude_assay(self, assay_name: str):
        """
        Set the crude oil assay to use for calculations.
        
        Args:
            assay_name: Name of the crude assay from the inventory
        """
        assay = self.inventory.get_assay(assay_name)
        if not assay:
            # Try search
            matches = self.inventory.search_assays(assay_name)
            if matches:
                assay = self.inventory.get_assay(matches[0])
                print(f"Using assay: {matches[0]}")
            else:
                raise ValueError(f"Crude assay not found: {assay_name}")
        
        self.current_assay = assay
        self.inputs['crude_assay'] = assay_name
    
    def set_crude_blend(self, crude_names: List[str], fractions: List[float]):
        """
        Set a blended crude as input.
        
        Args:
            crude_names: List of crude assay names
            fractions: List of weight fractions (must sum to 1.0)
        """
        from prelim.core.crude_blending import create_custom_blend
        
        blended_assay = create_custom_blend(
            crude_names,
            fractions,
            self.config.capacity_bpd
        )
        self.current_assay = blended_assay
        self.inputs['crude_assay'] = blended_assay.name
        self.inputs['is_blend'] = True
    
    def configure(self, **kwargs):
        """
        Configure refinery parameters.
        
        Args:
            **kwargs: Configuration parameters (capacity_bpd, etc.)
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"Warning: Unknown configuration parameter: {key}")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the refinery calculations.
        
        Returns:
            Dictionary of results including:
                - products: Product yields and properties
                - energy: Energy consumption breakdown
                - emissions: Direct emissions
                - lca_inventory: Life cycle inventory
                - impacts: Environmental impact scores
        """
        if not self.current_assay:
            raise ValueError("No crude assay set. Call set_crude_assay() first.")
        
        # Initialize results dictionary
        self.results = {
            'assay_name': self.current_assay.name,
            'capacity_bpd': self.config.capacity_bpd,
            'products': {},
            'energy': {},
            'emissions': {},
            'lca_inventory': {},
            'impacts': {},
        }
        
        # TODO: Implement full calculation workflow
        # This would involve:
        # 1. Load crude assay properties into calc engine
        # 2. Run CDU calculations
        # 3. Run downstream units (VDU, FCC, Coker, etc.)
        # 4. Calculate energy requirements
        # 5. Calculate utilities (H2, steam, power)
        # 6. Compile product slate
        # 7. Calculate emissions
        # 8. Build LCA inventory
        # 9. Calculate impact scores
        
        # For now, provide framework structure
        print(f"Refinery model initialized for: {self.current_assay.name}")
        print(f"Capacity: {self.config.capacity_bpd} bbl/day")
        print("\nNote: Full calculation engine implementation in progress.")
        print("Framework structure is complete and ready for detailed calculations.")
        
        return self.results
    
    def get_results(self) -> Dict[str, Any]:
        """Get calculation results."""
        return self.results
    
    def get_product_yields(self) -> Dict[str, float]:
        """Get product yields in volume %."""
        return self.results.get('products', {})
    
    def get_energy_consumption(self) -> Dict[str, float]:
        """Get energy consumption by type."""
        return self.results.get('energy', {})
    
    def get_emissions(self) -> Dict[str, float]:
        """Get direct emissions."""
        return self.results.get('emissions', {})
    
    def get_lca_impacts(self) -> Dict[str, float]:
        """Get life cycle impact assessment results."""
        return self.results.get('impacts', {})
    
    def list_available_assays(self, search_term: Optional[str] = None) -> List[str]:
        """
        List available crude assays.
        
        Args:
            search_term: Optional search term to filter assays
            
        Returns:
            List of assay names
        """
        if search_term:
            return self.inventory.search_assays(search_term)
        return self.inventory.list_assays()
    
    def get_assay_properties(self, assay_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get properties of a crude assay.
        
        Args:
            assay_name: Assay name (uses current assay if None)
            
        Returns:
            Dictionary of assay properties
        """
        if assay_name:
            assay = self.inventory.get_assay(assay_name)
        else:
            assay = self.current_assay
        
        if not assay:
            raise ValueError("No assay specified and no current assay set")
        
        return assay.get_all_properties()

