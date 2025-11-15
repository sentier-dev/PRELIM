"""
Life cycle inventory flow definitions.

Defines elementary flows (emissions, resources) for LCA calculations.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class FlowType(Enum):
    """Type of elementary flow."""
    EMISSION_AIR = "emission_air"
    EMISSION_WATER = "emission_water"
    EMISSION_SOIL = "emission_soil"
    RESOURCE = "resource"
    WASTE = "waste"


@dataclass
class Flow:
    """
    Represents an elementary flow in LCA.
    """
    name: str
    cas: Optional[str]
    compartment: str  # 'air', 'water', 'soil', 'resource'
    unit: str  # 'kg', 'MJ', 'm3', etc.
    flow_type: FlowType
    uuid: Optional[str] = None
    
    def __hash__(self):
        return hash((self.name, self.compartment))


class FlowRegistry:
    """
    Registry of elementary flows used in PRELIM.
    """
    
    def __init__(self):
        """Initialize flow registry."""
        self._flows: Dict[str, Flow] = {}
        self._initialize_common_flows()
    
    def _initialize_common_flows(self):
        """Initialize common flows used in refinery LCA."""
        common_flows = [
            # Air emissions
            Flow("Carbon dioxide", "124-38-9", "air", "kg", FlowType.EMISSION_AIR),
            Flow("Methane", "74-82-8", "air", "kg", FlowType.EMISSION_AIR),
            Flow("Nitrous oxide", "10024-97-2", "air", "kg", FlowType.EMISSION_AIR),
            Flow("Carbon monoxide", "630-08-0", "air", "kg", FlowType.EMISSION_AIR),
            Flow("nitrogen oxides", "NOX", "air", "kg", FlowType.EMISSION_AIR),
            Flow("sulfur dioxide", "7446-09-5", "air", "kg", FlowType.EMISSION_AIR),
            Flow("VOC, volatile organic compounds", "VOC", "air", "kg", FlowType.EMISSION_AIR),
            Flow("particulates, < 2.5 um", "PM2.5", "air", "kg", FlowType.EMISSION_AIR),
            Flow("particulates, < 10 um", "PM10", "air", "kg", FlowType.EMISSION_AIR),
            
            # Resources
            Flow("Natural gas", "74-82-8", "resource", "m3", FlowType.RESOURCE),
            Flow("Crude oil", "8002-05-9", "resource", "kg", FlowType.RESOURCE),
            Flow("Water", "7732-18-5", "resource", "m3", FlowType.RESOURCE),
            Flow("Electricity", None, "resource", "kWh", FlowType.RESOURCE),
        ]
        
        for flow in common_flows:
            self.register_flow(flow)
    
    def register_flow(self, flow: Flow):
        """
        Register a flow in the registry.
        
        Args:
            flow: Flow object to register
        """
        key = f"{flow.compartment}:{flow.name}"
        self._flows[key] = flow
    
    def get_flow(self, name: str, compartment: str) -> Optional[Flow]:
        """
        Get a flow by name and compartment.
        
        Args:
            name: Flow name
            compartment: Compartment ('air', 'water', etc.)
            
        Returns:
            Flow object or None if not found
        """
        key = f"{compartment}:{name}"
        return self._flows.get(key)
    
    def list_flows(self, flow_type: Optional[FlowType] = None) -> list:
        """
        List all registered flows.
        
        Args:
            flow_type: Optional filter by flow type
            
        Returns:
            List of Flow objects
        """
        flows = list(self._flows.values())
        if flow_type:
            flows = [f for f in flows if f.flow_type == flow_type]
        return flows


# Singleton instance
_flow_registry = None

def get_flow_registry() -> FlowRegistry:
    """Get the singleton FlowRegistry instance."""
    global _flow_registry
    if _flow_registry is None:
        _flow_registry = FlowRegistry()
    return _flow_registry

