"""
Validation tools for comparing Python model outputs against Excel.

Provides utilities to validate that the Python implementation produces
results consistent with the original Excel model.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from prelim.utils.excel_reader import ExcelFormulaExtractor


@dataclass
class ValidationResult:
    """
    Result of a validation comparison.
    """
    test_name: str
    passed: bool
    python_value: Any
    excel_value: Any
    difference: Optional[float] = None
    relative_error: Optional[float] = None
    message: str = ""
    
    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.test_name}: {self.message}"


class ModelValidator:
    """
    Validates Python model outputs against Excel.
    
    Compares calculated values, ensuring numerical accuracy and
    identifying any discrepancies between implementations.
    """
    
    def __init__(self, excel_filepath: str, tolerance: float = 1e-6):
        """
        Initialize validator.
        
        Args:
            excel_filepath: Path to PRELIM Excel file
            tolerance: Relative tolerance for numerical comparisons
        """
        self.excel_filepath = excel_filepath
        self.tolerance = tolerance
        self.extractor = ExcelFormulaExtractor(excel_filepath)
        self.results: List[ValidationResult] = []
    
    def compare_value(self, 
                     test_name: str,
                     python_value: float,
                     excel_sheet: str,
                     excel_cell: str,
                     relative: bool = True) -> ValidationResult:
        """
        Compare a Python calculated value against Excel.
        
        Args:
            test_name: Name/description of the test
            python_value: Value calculated by Python model
            excel_sheet: Excel sheet name
            excel_cell: Excel cell reference (e.g., 'A1')
            relative: Use relative error (True) or absolute (False)
            
        Returns:
            ValidationResult object
        """
        excel_value = self.extractor.extract_cell_value(excel_sheet, excel_cell)
        
        # Handle None or non-numeric values
        if excel_value is None or python_value is None:
            result = ValidationResult(
                test_name=test_name,
                passed=False,
                python_value=python_value,
                excel_value=excel_value,
                message="One or both values are None"
            )
        elif not isinstance(excel_value, (int, float)) or not isinstance(python_value, (int, float)):
            result = ValidationResult(
                test_name=test_name,
                passed=False,
                python_value=python_value,
                excel_value=excel_value,
                message="Non-numeric values"
            )
        else:
            # Calculate difference
            diff = abs(python_value - excel_value)
            
            if relative and excel_value != 0:
                rel_error = diff / abs(excel_value)
                passed = rel_error <= self.tolerance
                message = f"Rel error: {rel_error:.2e}"
            else:
                passed = diff <= self.tolerance
                rel_error = None
                message = f"Abs diff: {diff:.2e}"
            
            result = ValidationResult(
                test_name=test_name,
                passed=passed,
                python_value=python_value,
                excel_value=excel_value,
                difference=diff,
                relative_error=rel_error,
                message=message
            )
        
        self.results.append(result)
        return result
    
    def compare_array(self,
                     test_name: str,
                     python_array: np.ndarray,
                     excel_sheet: str,
                     excel_range: str) -> ValidationResult:
        """
        Compare an array of Python values against Excel range.
        
        Args:
            test_name: Name/description of the test
            python_array: Array of values from Python
            excel_sheet: Excel sheet name
            excel_range: Excel range (e.g., 'A1:A10')
            
        Returns:
            ValidationResult object
        """
        # TODO: Implement array comparison
        # Would need to extract range from Excel and compare element-wise
        result = ValidationResult(
            test_name=test_name,
            passed=False,
            python_value=python_array,
            excel_value=None,
            message="Array comparison not yet implemented"
        )
        self.results.append(result)
        return result
    
    def validate_assay_calculation(self, assay_name: str) -> Dict[str, ValidationResult]:
        """
        Validate calculations for a specific crude assay.
        
        Args:
            assay_name: Name of the crude assay to validate
            
        Returns:
            Dictionary of ValidationResult objects
        """
        # TODO: Implement full assay validation
        # This would:
        # 1. Set Excel to use the specified assay
        # 2. Read key results from Excel
        # 3. Run Python model with same assay
        # 4. Compare results
        
        validation_results = {}
        
        # Placeholder for demonstration
        validation_results['note'] = ValidationResult(
            test_name=f"Validate {assay_name}",
            passed=False,
            python_value=None,
            excel_value=None,
            message="Full assay validation not yet implemented"
        )
        
        return validation_results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation results.
        
        Returns:
            Dictionary with pass/fail counts and statistics
        """
        if not self.results:
            return {'message': 'No validation results yet'}
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        # Calculate average relative error for passed tests
        rel_errors = [r.relative_error for r in self.results 
                     if r.relative_error is not None and r.passed]
        avg_rel_error = np.mean(rel_errors) if rel_errors else None
        
        return {
            'total_tests': len(self.results),
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / len(self.results) if self.results else 0,
            'avg_relative_error': avg_rel_error
        }
    
    def print_summary(self):
        """Print validation summary to console."""
        summary = self.get_summary()
        
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total tests: {summary.get('total_tests', 0)}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Pass rate: {summary.get('pass_rate', 0)*100:.1f}%")
        
        if summary.get('avg_relative_error'):
            print(f"Avg relative error: {summary['avg_relative_error']:.2e}")
        
        print("\nFailed tests:")
        for result in self.results:
            if not result.passed:
                print(f"  - {result}")
    
    def export_results(self, filepath: str):
        """
        Export validation results to CSV.
        
        Args:
            filepath: Path to output CSV file
        """
        data = []
        for result in self.results:
            data.append({
                'test_name': result.test_name,
                'passed': result.passed,
                'python_value': result.python_value,
                'excel_value': result.excel_value,
                'difference': result.difference,
                'relative_error': result.relative_error,
                'message': result.message
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        print(f"Validation results exported to {filepath}")


def validate_single_assay(assay_name: str, 
                         excel_filepath: str,
                         tolerance: float = 1e-6) -> Dict[str, ValidationResult]:
    """
    Convenience function to validate a single assay.
    
    Args:
        assay_name: Name of crude assay to validate
        excel_filepath: Path to PRELIM Excel file
        tolerance: Relative tolerance for comparisons
        
    Returns:
        Dictionary of validation results
    """
    validator = ModelValidator(excel_filepath, tolerance)
    return validator.validate_assay_calculation(assay_name)

