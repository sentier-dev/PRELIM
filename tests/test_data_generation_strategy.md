# Strategy for Generating Known Good Results for Integration Tests

## Overview

To properly validate the Python implementation against the Excel model, we need to generate a set of "known good" reference results. This document outlines the strategy for creating these test fixtures.

## Current Situation Analysis

### What We Can Do Programmatically

✅ **Read Excel data** - We can read:
- Current assay selection
- Input parameters
- Calculated results (with `data_only=True`)
- Formula structure

✅ **Write to Excel** - We can use `openpyxl` to:
- Modify cell values
- Change assay selection (if we know the input mechanism)
- Save the workbook

❌ **Cannot do with openpyxl alone**:
- Trigger Excel's calculation engine
- Execute VBA macros
- Recalculate formulas automatically

### The Challenge

The Excel file uses:
1. Assay selection via dropdown/data validation (linked to 'Assay Inventory' sheet)
2. Complex formulas that reference the selected assay
3. 100K+ interdependent formulas
4. VBA macros for some operations

**openpyxl limitation**: It reads/writes Excel files but doesn't execute calculations. When we open with `data_only=True`, we get the **last calculated values** from when the file was saved in Excel.

## Proposed Strategy

### Option 1: Use Existing Calculated Results (RECOMMENDED FOR NOW)

**Approach**: Extract current results from the Excel file as-is

**Steps**:
1. Open the Excel file and identify which assay is currently selected
2. Read the calculated results from 'Results Single Assay' sheet
3. Document the input state (assay name, configuration, parameters)
4. Save as a test fixture JSON file
5. Repeat for multiple assays by manually opening in Excel, changing assay, saving, then extracting

**Advantages**:
- ✅ No special tools required
- ✅ Can be done entirely in Python
- ✅ Works on any platform
- ✅ Quick to implement

**Disadvantages**:
- ⚠️ Requires manual Excel operations to generate different test cases
- ⚠️ Limited to whatever assays/configs are already calculated in the file

**Implementation**:
```python
def extract_current_test_case(excel_path):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    
    # 1. Identify current assay
    assay_sheet = wb['Assay Inventory']
    current_assay = assay_sheet['C9'].value  # or wherever it's stored
    
    # 2. Extract key inputs
    inputs = {
        'assay_name': current_assay,
        'capacity': ...,  # read from appropriate cell
        'configuration': ...,
    }
    
    # 3. Extract results
    results_sheet = wb['Results Single Assay']
    results = {
        'gasoline_yield': results_sheet['C13'].value,
        'diesel_yield': results_sheet['C15'].value,
        # ... etc
    }
    
    return {'inputs': inputs, 'results': results}
```

### Option 2: Use xlwings for Automation (IF EXCEL AVAILABLE)

**Approach**: Use xlwings to control Excel application directly

**Requirements**:
- Excel must be installed on the machine
- xlwings library (`pip install xlwings`)
- Only works on Windows/Mac with Excel

**Steps**:
```python
import xlwings as xw

def generate_test_case_with_excel(excel_path, assay_name):
    # Open workbook in Excel
    wb = xw.Book(excel_path)
    
    # Set assay (find the input cell and set it)
    assay_input_sheet = wb.sheets['Main Input & Output']
    assay_input_sheet.range('ASSAY_INPUT_CELL').value = assay_name
    
    # Excel automatically recalculates
    
    # Read results
    results_sheet = wb.sheets['Results Single Assay']
    results = {
        'gasoline_yield': results_sheet.range('C13').value,
        'diesel_yield': results_sheet.range('C15').value,
        # ...
    }
    
    # Save test fixture
    wb.close()
    return results
```

**Advantages**:
- ✅ Full automation possible
- ✅ Can generate many test cases programmatically
- ✅ Excel handles all calculations

**Disadvantages**:
- ❌ Requires Excel installation
- ❌ Platform-dependent
- ❌ Slower (opens Excel GUI)
- ❌ May have licensing issues in CI/CD

### Option 3: Manual Extraction with Documentation (BEST PRACTICE)

**Approach**: Create a systematic manual process with clear documentation

**Process**:
1. Create a test case specification document
2. For each test case:
   - Open Excel manually
   - Set inputs (assay, parameters)
   - Wait for calculations
   - Document all inputs
   - Extract and save results
   - Screenshot key results for verification
3. Store in structured JSON format

**Test Case Specification Example**:
```yaml
test_cases:
  - id: tc001_alaska_default
    description: "Alaskan North Slope with default coking refinery config"
    inputs:
      assay: "Alaskan North Slope_Exxon"
      assay_number: 23
      configuration: "Coking Refinery"
      capacity_bpd: 100000
      region: "Default"
    expected_results:
      product_yields:
        gasoline: 0.282259
        jet: 0.158269
        diesel: 0.321884
      energy_consumption:
        total_mj: 1234.56
      emissions:
        co2_kg: 5678.90
```

## Recommended Implementation Plan

### Phase 1: Extract Current State (Immediate)

Create a utility to extract the current test case:

```python
# tests/utils/extract_reference_data.py
def extract_current_excel_state(excel_path: str) -> dict:
    """Extract current state from Excel file as reference data."""
    # Implementation as shown in Option 1
    pass
```

### Phase 2: Define Test Cases (Manual)

Create `tests/fixtures/test_cases.yaml` with specifications for 5-10 representative test cases:
- Light crude (high API)
- Heavy crude (low API)  
- High sulfur
- Low sulfur
- Blend scenario
- Different configurations

### Phase 3: Generate Reference Data

For each test case:
1. Open PRELIM_v1.6.xlsm in Excel
2. Select the specified assay from dropdown
3. Set configuration parameters
4. Wait for calculations (verify no #VALUE errors)
5. Run extraction script
6. Save to `tests/fixtures/reference_data/tc_XXX.json`

### Phase 4: Create Validation Tests

```python
# tests/test_integration.py
@pytest.mark.parametrize("test_case_file", [
    "tc_001_alaska_default.json",
    "tc_002_arab_heavy.json",
    # ...
])
def test_refinery_calculation(test_case_file):
    """Validate Python results against Excel reference data."""
    # Load test case
    ref_data = load_reference_data(test_case_file)
    
    # Run Python model
    refinery = Refinery()
    refinery.set_crude_assay(ref_data['inputs']['assay'])
    refinery.configure(**ref_data['inputs']['config'])
    results = refinery.run()
    
    # Compare results
    for key, expected_value in ref_data['expected_results'].items():
        actual_value = results[key]
        assert_close(actual_value, expected_value, rtol=1e-6)
```

## Minimal Test Fixture Structure

```json
{
  "test_id": "tc_001",
  "description": "Alaskan North Slope - Default Coking Refinery",
  "excel_file": "PRELIM_v1.6.xlsm",
  "extracted_date": "2025-11-15",
  "inputs": {
    "assay_name": "Alaskan North Slope_Exxon",
    "assay_number": 23,
    "refinery_config": "Coking",
    "capacity_bpd": 100000
  },
  "expected_results": {
    "product_yields_vol_pct": {
      "gasoline": 0.282259,
      "jet": 0.158269,
      "diesel": 0.321884,
      "fuel_oil": 0.033801,
      "coke": 0.011632
    },
    "product_flows_bpd": {
      "gasoline": 28688.39,
      "jet": 16086.20,
      "diesel": 32715.80
    },
    "energy_mj_per_bbl": {
      "total": 123.45
    },
    "emissions_kg_per_bbl": {
      "co2": 56.78,
      "nox": 0.12
    }
  },
  "tolerances": {
    "relative": 1e-5,
    "absolute": 1e-8
  }
}
```

## Immediate Action Items

1. **Create extraction utility** (`tests/utils/extract_excel_data.py`)
2. **Extract current state** - Run extraction on PRELIM_v1.6.xlsm as-is
3. **Save as first fixture** - `tests/fixtures/tc_001_current_state.json`
4. **Document test case specs** - Create test_cases.md with 5-10 cases
5. **Manual generation** - For critical test cases, manually set in Excel and extract
6. **Create integration test** - Use fixtures to validate Python implementation

## Answer to Your Questions

**Q: Does this need manual modification of the Excel workbook?**
A: For generating multiple diverse test cases, yes - manual modification in Excel is the most practical approach given openpyxl's limitations. However, we can extract the *current* state programmatically.

**Q: Can you enter the appropriate data yourself?**
A: I can write values to Excel cells using openpyxl, BUT this won't trigger Excel's calculation engine. The formulas won't recalculate until the file is opened in actual Excel.

**Q: Can you retrieve the results yourself?**
A: Yes! I can read all calculated values from the Excel file using `data_only=True`. These are the values that were last calculated when the file was saved in Excel.

## Recommended Path Forward

**Short term** (next 1-2 hours):
1. I'll create an extraction utility
2. Extract the current state from the Excel file
3. Create a test fixture
4. Write an integration test that uses it

**Medium term** (when you have time):
1. You (or someone with Excel) manually create 5-10 test cases
2. For each: open Excel, set inputs, wait for calc, save
3. Run extraction script on each saved version
4. Build up test fixture library

**Long term** (if Excel automation needed):
1. Evaluate xlwings for automated test generation
2. Consider CI/CD implications
3. Balance coverage vs. effort

Would you like me to implement the extraction utility now?

