"""
Batch processing for running calculations across multiple crude assays.

Converted from Float_all_assays VBA macro in PRELIM_v1.6.xlsm.

Allows running refinery calculations for all assays in the inventory
and collecting results.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import pandas as pd

from prelim.data.assays import get_assay_inventory, CrudeAssay


@dataclass
class BatchResult:
    """
    Result from a single assay calculation in batch mode.
    """
    assay_name: str
    assay_number: Optional[int]
    success: bool
    results: Dict[str, Any]
    error: Optional[str] = None


class BatchProcessor:
    """
    Processes multiple crude assays through the refinery model.
    
    This implements the logic from the Float_all_assays VBA macro,
    which iterates through all assays and collects results.
    """
    
    def __init__(self, refinery_model: Optional[Any] = None):
        """
        Initialize batch processor.
        
        Args:
            refinery_model: Refinery model instance to use for calculations
                          (if None, must be provided to process_all)
        """
        self.inventory = get_assay_inventory()
        self.refinery_model = refinery_model
        self.results: List[BatchResult] = []
    
    def process_all(self, 
                   refinery_model: Optional[Any] = None,
                   assay_filter: Optional[Callable[[CrudeAssay], bool]] = None,
                   max_assays: Optional[int] = None,
                   progress_callback: Optional[Callable[[int, int, str], None]] = None
                   ) -> List[BatchResult]:
        """
        Process all (or filtered) assays through the refinery model.
        
        Args:
            refinery_model: Refinery model instance (overrides constructor)
            assay_filter: Optional function to filter which assays to process
            max_assays: Maximum number of assays to process (for testing)
            progress_callback: Function called with (current, total, assay_name)
                             for progress reporting
        
        Returns:
            List of BatchResult objects
        """
        model = refinery_model or self.refinery_model
        if not model:
            raise ValueError("No refinery model provided")
        
        # Get all assays
        all_assay_names = self.inventory.list_assays()
        
        # Apply filter if provided
        if assay_filter:
            assay_names = [
                name for name in all_assay_names
                if assay_filter(self.inventory.get_assay(name))
            ]
        else:
            assay_names = all_assay_names
        
        # Limit if requested
        if max_assays:
            assay_names = assay_names[:max_assays]
        
        total_assays = len(assay_names)
        self.results = []
        
        # Process each assay
        for idx, assay_name in enumerate(assay_names, 1):
            if progress_callback:
                progress_callback(idx, total_assays, assay_name)
            
            try:
                assay = self.inventory.get_assay(assay_name)
                
                # Set assay in model
                model.set_crude_assay(assay_name)
                
                # Run calculation
                results = model.run()
                
                # Store result
                batch_result = BatchResult(
                    assay_name=assay_name,
                    assay_number=assay.assay_number,
                    success=True,
                    results=results
                )
                
            except Exception as e:
                # Store error
                batch_result = BatchResult(
                    assay_name=assay_name,
                    assay_number=self.inventory.get_assay(assay_name).assay_number,
                    success=False,
                    results={},
                    error=str(e)
                )
            
            self.results.append(batch_result)
        
        return self.results
    
    def process_assay_list(self,
                          assay_names: List[str],
                          refinery_model: Optional[Any] = None,
                          progress_callback: Optional[Callable[[int, int, str], None]] = None
                          ) -> List[BatchResult]:
        """
        Process a specific list of assays.
        
        Args:
            assay_names: List of assay names to process
            refinery_model: Refinery model instance
            progress_callback: Progress reporting function
            
        Returns:
            List of BatchResult objects
        """
        model = refinery_model or self.refinery_model
        if not model:
            raise ValueError("No refinery model provided")
        
        total_assays = len(assay_names)
        self.results = []
        
        for idx, assay_name in enumerate(assay_names, 1):
            if progress_callback:
                progress_callback(idx, total_assays, assay_name)
            
            try:
                # Verify assay exists
                assay = self.inventory.get_assay(assay_name)
                if not assay:
                    raise ValueError(f"Assay not found: {assay_name}")
                
                # Set and run
                model.set_crude_assay(assay_name)
                results = model.run()
                
                batch_result = BatchResult(
                    assay_name=assay_name,
                    assay_number=assay.assay_number,
                    success=True,
                    results=results
                )
                
            except Exception as e:
                batch_result = BatchResult(
                    assay_name=assay_name,
                    assay_number=None,
                    success=False,
                    results={},
                    error=str(e)
                )
            
            self.results.append(batch_result)
        
        return self.results
    
    def get_results_dataframe(self, 
                             result_keys: Optional[List[str]] = None
                             ) -> pd.DataFrame:
        """
        Convert batch results to a pandas DataFrame.
        
        Args:
            result_keys: Specific result keys to extract (None for all)
            
        Returns:
            DataFrame with one row per assay
        """
        if not self.results:
            return pd.DataFrame()
        
        data = []
        for result in self.results:
            row = {
                'assay_name': result.assay_name,
                'assay_number': result.assay_number,
                'success': result.success,
            }
            
            if result.success:
                if result_keys:
                    for key in result_keys:
                        row[key] = result.results.get(key)
                else:
                    row.update(result.results)
            else:
                row['error'] = result.error
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_successful_results(self) -> List[BatchResult]:
        """Get only successful results."""
        return [r for r in self.results if r.success]
    
    def get_failed_results(self) -> List[BatchResult]:
        """Get only failed results."""
        return [r for r in self.results if not r.success]
    
    def get_success_rate(self) -> float:
        """Get the success rate as a fraction (0-1)."""
        if not self.results:
            return 0.0
        successful = len(self.get_successful_results())
        return successful / len(self.results)
    
    def export_results(self, filepath: str, format: str = 'csv'):
        """
        Export results to file.
        
        Args:
            filepath: Path to output file
            format: Output format ('csv', 'excel', 'json')
        """
        df = self.get_results_dataframe()
        
        if format == 'csv':
            df.to_csv(filepath, index=False)
        elif format == 'excel':
            df.to_excel(filepath, index=False)
        elif format == 'json':
            df.to_json(filepath, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


def run_batch_analysis(assay_names: Optional[List[str]] = None,
                      max_assays: Optional[int] = None,
                      verbose: bool = True) -> pd.DataFrame:
    """
    Convenience function to run batch analysis.
    
    Args:
        assay_names: Specific assays to analyze (None for all)
        max_assays: Maximum number of assays to process
        verbose: Print progress messages
        
    Returns:
        DataFrame with results for all assays
        
    Example:
        >>> results = run_batch_analysis(max_assays=10, verbose=True)
        >>> print(results.head())
    """
    from prelim import Refinery
    
    processor = BatchProcessor()
    
    def progress(current, total, name):
        if verbose:
            print(f"Processing {current}/{total}: {name}")
    
    try:
        model = Refinery()
        
        if assay_names:
            results = processor.process_assay_list(
                assay_names,
                refinery_model=model,
                progress_callback=progress if verbose else None
            )
        else:
            results = processor.process_all(
                refinery_model=model,
                max_assays=max_assays,
                progress_callback=progress if verbose else None
            )
        
        if verbose:
            success_rate = processor.get_success_rate()
            print(f"\nCompleted: {len(results)} assays")
            print(f"Success rate: {success_rate*100:.1f}%")
        
        return processor.get_results_dataframe()
        
    except NotImplementedError:
        print("Note: Refinery calculation engine not yet fully implemented.")
        print("Batch processing framework is ready for when calculations are complete.")
        return pd.DataFrame()

