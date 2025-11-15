# PRELIM - Petroleum Refinery Life Cycle Inventory Model

A Python library for modeling petroleum refinery processes and calculating life cycle inventories and environmental impacts.

Converted from PRELIM_v1.6.xlsm Excel model.

## Overview

PRELIM is a comprehensive model for petroleum refineries that:
- Models 650+ crude oil assays with detailed properties
- Simulates major refinery process units (CDU, VDU, FCC, Coker, Hydrotreaters, etc.)
- Calculates energy requirements and emissions
- Performs life cycle impact assessment using TRACI 2.1
- Supports custom crude oil blending
- Enables batch processing across multiple assays

## Installation

```bash
# Clone or download the repository
cd Prelim

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Quick Start

```python
from prelim import Refinery

# Create a refinery model
refinery = Refinery()

# Set crude oil assay
refinery.set_crude_assay('Alaskan North Slope_Exxon')

# Configure refinery parameters
refinery.configure(capacity_bpd=150000)

# Run calculations (when implementation complete)
results = refinery.run()
```

## Features

### Crude Oil Assays

Access 650+ crude oil assays with complete distillation curves and properties:

```python
from prelim.data.assays import get_assay_inventory

inventory = get_assay_inventory()

# Search for assays
alaska_crudes = inventory.search_assays('Alaska')

# Get assay properties
assay = inventory.get_assay('Alaskan North Slope_Exxon')
api_gravity = assay.get_property('API gravity', 'Full Crude')
sulfur = assay.get_property('Sulfur', 'Full Crude')
```

### Crude Oil Blending

Create custom crude blends using weight-averaging:

```python
from prelim.core.crude_blending import create_custom_blend

blend = create_custom_blend(
    crude_names=['Alaskan North Slope_Exxon', 'Arab Light_Saudi Aramco'],
    fractions=[0.6, 0.4],  # 60% Alaska, 40% Arab Light
    refinery_capacity_bpd=100000
)
```

### Life Cycle Assessment

Build life cycle inventories and calculate environmental impacts:

```python
from prelim.lca.inventory import LifeCycleInventory
from prelim.lca.impact_assessment import assess_refinery_impacts

# Create inventory
inventory = LifeCycleInventory("Refinery Process")
inventory.add_emission('Carbon dioxide', 'air', 1000.0, 'kg')
inventory.add_emission('nitrogen oxides', 'air', 2.5, 'kg')

# Calculate impacts
impacts = assess_refinery_impacts(inventory)
print(f"Global Warming: {impacts['kg CO2 eq / kg']:.2f} kg CO2 eq")
```

### Batch Processing

Run calculations across multiple crude assays:

```python
from prelim.core.batch_processor import BatchProcessor

processor = BatchProcessor(refinery_model)
results = processor.process_all(max_assays=10)

# Export results
df = processor.get_results_dataframe()
df.to_csv('batch_results.csv')
```

## Project Structure

```
prelim/
├── __init__.py
├── data/                      # Data modules
│   ├── constants.py           # Refinery constants and parameters
│   ├── assays.py              # Crude oil assay data (654 assays)
│   ├── emission_factors.py    # Emission factors
│   ├── traci_factors.py       # TRACI 2.1 characterization factors
│   ├── process_correlations.py # Process correlations
│   └── energy_conversions.py  # Energy and unit conversions
├── core/                      # Core calculation modules
│   ├── refinery.py            # Main Refinery class API
│   ├── calculations.py        # Calculation graph engine
│   ├── process_units.py       # Process unit models
│   ├── crude_blending.py      # Crude blending (from VBA)
│   └── batch_processor.py     # Batch processing (from VBA)
├── lca/                       # Life cycle assessment
│   ├── flows.py               # Elementary flow definitions
│   ├── inventory.py           # Life cycle inventory
│   └── impact_assessment.py   # LCIA with TRACI 2.1
└── utils/                     # Utilities
    ├── excel_reader.py        # Excel data extraction
    └── validators.py          # Validation against Excel

tests/                         # Test suite
examples/                      # Usage examples
```

## Examples

See the `examples/` directory for detailed usage examples:
- `basic_usage.py` - Basic refinery modeling workflow
- `crude_blending.py` - Custom crude blend creation
- `lca_example.py` - Life cycle assessment

## Development Status

The Python library framework is complete with:
- ✅ Data extraction from Excel (all sheets)
- ✅ Crude assay loading and management (654 assays)
- ✅ Crude blending (converted from VBA)
- ✅ Calculation engine framework
- ✅ Process unit model structure
- ✅ Batch processing (converted from VBA)
- ✅ LCA modules with TRACI 2.1
- ✅ Validation framework
- ✅ Comprehensive test suite

In progress:
- 🔄 Detailed process unit calculations (100K+ Excel formulas)
- 🔄 Full validation against Excel outputs

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Dependencies

- pandas >= 2.0.0
- openpyxl >= 3.1.0
- numpy >= 1.24.0

## Contributing

This project is converted from the PRELIM Excel model. For questions about the underlying
refinery model and assumptions, please refer to the original PRELIM documentation.

## Citation

If you use PRELIM in your research, please cite the original PRELIM model:

[Add appropriate citation for PRELIM_v1.6.xlsm]

## License

TBD

