"""
Process correlations for refinery unit operations.

Contains empirical correlations for yields, properties, and performance
of various refinery process units (hydrocracking, FCC, reforming, etc.).

Extracted from the Process Correlations sheet of PRELIM_v1.6.xlsm.
"""

import json
import os
from typing import List, Any


class ProcessCorrelations:
    """
    Container for process correlation data.
    
    The Process Correlations sheet contains empirical relationships
    for predicting yields and properties of various refinery units
    based on feed properties and operating conditions.
    """
    
    def __init__(self):
        """Load process correlations data from JSON file."""
        data_file = os.path.join(os.path.dirname(__file__), 'process_correlations_raw.json')
        with open(data_file, 'r') as f:
            self._raw_data = json.load(f)
    
    def get_raw_data(self) -> List[List[Any]]:
        """
        Get the raw data matrix from the Process Correlations sheet.
        
        Returns:
            List of rows (each row is a list of values)
        """
        return self._raw_data
    
    # TODO: Add specific correlation methods as calculation logic is implemented
    # e.g., get_hydrocracking_yields(), get_fcc_yields(), etc.


# Singleton instance
_process_correlations = None

def get_process_correlations() -> ProcessCorrelations:
    """Get the singleton ProcessCorrelations instance."""
    global _process_correlations
    if _process_correlations is None:
        _process_correlations = ProcessCorrelations()
    return _process_correlations

