"""
Life cycle inventory (LCI) data structures.

Manages inventory of inputs and outputs for refinery processes.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from prelim.lca.flows import Flow, get_flow_registry


@dataclass
class InventoryEntry:
    """
    A single entry in a life cycle inventory.
    """
    flow: Flow
    amount: float
    unit: str
    comment: Optional[str] = None
    
    def __repr__(self):
        return f"InventoryEntry({self.flow.name}: {self.amount} {self.unit})"


class LifeCycleInventory:
    """
    Life cycle inventory for a refinery process or product.
    
    Contains all inputs (resources) and outputs (products, emissions, waste).
    """
    
    def __init__(self, name: str):
        """
        Initialize inventory.
        
        Args:
            name: Name of the process or product
        """
        self.name = name
        self.entries: List[InventoryEntry] = []
        self.flow_registry = get_flow_registry()
    
    def add_emission(self, flow_name: str, compartment: str, 
                    amount: float, unit: str, comment: Optional[str] = None):
        """
        Add an emission to the inventory.
        
        Args:
            flow_name: Name of the emitted substance
            compartment: Environmental compartment ('air', 'water', 'soil')
            amount: Amount emitted
            unit: Unit of measurement
            comment: Optional comment
        """
        flow = self.flow_registry.get_flow(flow_name, compartment)
        if not flow:
            print(f"Warning: Flow not registered: {flow_name} to {compartment}")
            return
        
        entry = InventoryEntry(flow=flow, amount=amount, unit=unit, comment=comment)
        self.entries.append(entry)
    
    def add_resource(self, flow_name: str, amount: float, 
                    unit: str, comment: Optional[str] = None):
        """
        Add a resource input to the inventory.
        
        Args:
            flow_name: Name of the resource
            amount: Amount consumed
            unit: Unit of measurement
            comment: Optional comment
        """
        flow = self.flow_registry.get_flow(flow_name, "resource")
        if not flow:
            print(f"Warning: Resource not registered: {flow_name}")
            return
        
        entry = InventoryEntry(flow=flow, amount=amount, unit=unit, comment=comment)
        self.entries.append(entry)
    
    def get_emissions(self, compartment: Optional[str] = None) -> List[InventoryEntry]:
        """
        Get all emission entries.
        
        Args:
            compartment: Optional filter by compartment
            
        Returns:
            List of emission entries
        """
        emissions = [e for e in self.entries if 'emission' in e.flow.flow_type.value]
        if compartment:
            emissions = [e for e in emissions if e.flow.compartment == compartment]
        return emissions
    
    def get_resources(self) -> List[InventoryEntry]:
        """Get all resource input entries."""
        return [e for e in self.entries if e.flow.flow_type.value == 'resource']
    
    def get_total_by_flow(self, flow_name: str, compartment: str) -> float:
        """
        Get total amount for a specific flow.
        
        Args:
            flow_name: Flow name
            compartment: Compartment
            
        Returns:
            Total amount (sum of all entries for this flow)
        """
        total = 0.0
        for entry in self.entries:
            if entry.flow.name == flow_name and entry.flow.compartment == compartment:
                total += entry.amount
        return total
    
    def to_dict(self) -> Dict:
        """
        Convert inventory to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            'name': self.name,
            'entries': [
                {
                    'flow': entry.flow.name,
                    'compartment': entry.flow.compartment,
                    'amount': entry.amount,
                    'unit': entry.unit,
                    'comment': entry.comment
                }
                for entry in self.entries
            ]
        }
    
    def __len__(self):
        return len(self.entries)
    
    def __repr__(self):
        return f"LifeCycleInventory(name='{self.name}', entries={len(self.entries)})"

