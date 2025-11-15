"""
Core calculation engine for PRELIM refinery model.

Provides a calculation graph system to evaluate formulas with proper
dependency resolution.
"""

import re
from typing import Dict, Any, Optional, Set, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class CellType(Enum):
    """Type of cell value."""
    CONSTANT = "constant"  # Fixed value
    FORMULA = "formula"    # Calculated from formula
    INPUT = "input"        # User input


@dataclass
class Cell:
    """
    Represents a single cell in the calculation graph.
    """
    address: str  # e.g., "CokingRefineryCalcs!A1"
    value: Any = None
    cell_type: CellType = CellType.CONSTANT
    formula: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    calculated: bool = False
    
    def __hash__(self):
        return hash(self.address)


class CalculationEngine:
    """
    Manages calculation graph and formula evaluation.
    
    This engine:
    1. Builds a dependency graph from formulas
    2. Resolves calculation order
    3. Evaluates formulas with proper sequencing
    """
    
    def __init__(self):
        """Initialize the calculation engine."""
        self.cells: Dict[str, Cell] = {}
        self._calculation_order: Optional[List[str]] = None
        self._functions = self._setup_excel_functions()
    
    def add_cell(self, address: str, value: Any = None, 
                 cell_type: CellType = CellType.CONSTANT,
                 formula: Optional[str] = None):
        """
        Add a cell to the calculation graph.
        
        Args:
            address: Cell address (e.g., "Sheet1!A1")
            value: Initial value
            cell_type: Type of cell
            formula: Formula string (if cell_type is FORMULA)
        """
        cell = Cell(
            address=address,
            value=value,
            cell_type=cell_type,
            formula=formula
        )
        
        if formula:
            cell.dependencies = self._extract_dependencies(formula)
        
        self.cells[address] = cell
        self._calculation_order = None  # Invalidate calculation order
    
    def set_value(self, address: str, value: Any):
        """
        Set a cell value (for inputs or constants).
        
        Args:
            address: Cell address
            value: New value
        """
        if address in self.cells:
            self.cells[address].value = value
            self.cells[address].calculated = True
            # Mark dependent cells as needing recalculation
            self._invalidate_dependents(address)
        else:
            self.add_cell(address, value=value, cell_type=CellType.INPUT)
    
    def get_value(self, address: str) -> Any:
        """
        Get the value of a cell.
        
        Args:
            address: Cell address
            
        Returns:
            Cell value
        """
        if address not in self.cells:
            return None
        
        cell = self.cells[address]
        
        if not cell.calculated and cell.cell_type == CellType.FORMULA:
            self._calculate_cell(address)
        
        return cell.value
    
    def calculate_all(self):
        """Calculate all formula cells in proper dependency order."""
        order = self._get_calculation_order()
        
        for address in order:
            cell = self.cells[address]
            if cell.cell_type == CellType.FORMULA:
                self._calculate_cell(address)
    
    def _calculate_cell(self, address: str):
        """
        Calculate a single cell's value from its formula.
        
        Args:
            address: Cell address
        """
        cell = self.cells[address]
        
        if cell.calculated:
            return
        
        if cell.cell_type != CellType.FORMULA:
            cell.calculated = True
            return
        
        # Ensure dependencies are calculated first
        for dep_address in cell.dependencies:
            if dep_address in self.cells:
                dep_cell = self.cells[dep_address]
                if not dep_cell.calculated and dep_cell.cell_type == CellType.FORMULA:
                    self._calculate_cell(dep_address)
        
        # Evaluate formula
        try:
            cell.value = self._evaluate_formula(cell.formula, address)
            cell.calculated = True
        except Exception as e:
            print(f"Error calculating {address}: {e}")
            cell.value = None
            cell.calculated = True
    
    def _evaluate_formula(self, formula: str, current_address: str) -> Any:
        """
        Evaluate an Excel formula.
        
        Args:
            formula: Formula string (starting with =)
            current_address: Address of cell being evaluated
            
        Returns:
            Calculated value
        """
        if not formula or not formula.startswith('='):
            return None
        
        # Remove leading =
        expr = formula[1:]
        
        # Replace cell references with values
        expr = self._replace_cell_references(expr, current_address)
        
        # Replace Excel functions with Python equivalents
        expr = self._replace_functions(expr)
        
        # Evaluate the expression
        try:
            # Use a restricted evaluation for safety
            result = eval(expr, {"__builtins__": {}}, self._functions)
            return result
        except Exception as e:
            raise ValueError(f"Cannot evaluate formula '{formula}': {e}")
    
    def _replace_cell_references(self, expr: str, current_address: str) -> str:
        """
        Replace cell references in formula with their values.
        
        Args:
            expr: Formula expression
            current_address: Current cell address (for resolving relative refs)
            
        Returns:
            Expression with cell references replaced
        """
        # Pattern for sheet references
        pattern = r"'([^']+)'!([A-Z]+\d+)"
        
        def replacer(match):
            sheet = match.group(1)
            cell_ref = match.group(2)
            full_address = f"{sheet}!{cell_ref}"
            value = self.get_value(full_address)
            return str(value) if value is not None else "0"
        
        expr = re.sub(pattern, replacer, expr)
        
        # Pattern for same-sheet references (simplified)
        current_sheet = current_address.split('!')[0] if '!' in current_address else ""
        pattern2 = r'(?<![A-Z])([A-Z]+\d+)(?![A-Z0-9])'
        
        def replacer2(match):
            cell_ref = match.group(1)
            full_address = f"{current_sheet}!{cell_ref}" if current_sheet else cell_ref
            value = self.get_value(full_address)
            return str(value) if value is not None else "0"
        
        expr = re.sub(pattern2, replacer2, expr)
        
        return expr
    
    def _replace_functions(self, expr: str) -> str:
        """Replace Excel functions with Python equivalents."""
        # Simple replacements
        replacements = {
            'IF(': '__if(',
            'SUM(': 'sum([',
            'MAX(': 'max([',
            'MIN(': 'min([',
        }
        
        for excel_func, python_func in replacements.items():
            expr = expr.replace(excel_func, python_func)
        
        # Close sum/max/min lists
        if 'sum([' in expr or 'max([' in expr or 'min([' in expr:
            expr = expr.replace(')', '])')
        
        return expr
    
    def _extract_dependencies(self, formula: str) -> Set[str]:
        """
        Extract cell addresses that formula depends on.
        
        Args:
            formula: Formula string
            
        Returns:
            Set of cell addresses
        """
        dependencies = set()
        
        # Sheet references
        pattern1 = r"'([^']+)'!([A-Z]+\d+)"
        for sheet, cell in re.findall(pattern1, formula):
            dependencies.add(f"{sheet}!{cell}")
        
        # Same-sheet references (basic pattern)
        pattern2 = r'(?<![A-Z])([A-Z]+\d+)(?![A-Z0-9])'
        for cell in re.findall(pattern2, formula):
            dependencies.add(cell)
        
        return dependencies
    
    def _get_calculation_order(self) -> List[str]:
        """
        Determine the order in which cells should be calculated.
        
        Uses topological sort on the dependency graph.
        
        Returns:
            List of cell addresses in calculation order
        """
        if self._calculation_order is not None:
            return self._calculation_order
        
        # Simple topological sort
        order = []
        visited = set()
        temp_mark = set()
        
        def visit(address: str):
            if address in temp_mark:
                # Circular dependency - skip for now
                return
            if address in visited:
                return
            
            if address not in self.cells:
                return
            
            temp_mark.add(address)
            cell = self.cells[address]
            
            for dep in cell.dependencies:
                visit(dep)
            
            temp_mark.remove(address)
            visited.add(address)
            order.append(address)
        
        for address in self.cells.keys():
            visit(address)
        
        self._calculation_order = order
        return order
    
    def _invalidate_dependents(self, address: str):
        """Mark cells that depend on this cell as needing recalculation."""
        for cell_address, cell in self.cells.items():
            if address in cell.dependencies:
                cell.calculated = False
                self._invalidate_dependents(cell_address)
    
    def _setup_excel_functions(self) -> Dict[str, Callable]:
        """Set up Excel function equivalents."""
        def __if(condition, true_val, false_val):
            return true_val if condition else false_val
        
        return {
            '__if': __if,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
        }

