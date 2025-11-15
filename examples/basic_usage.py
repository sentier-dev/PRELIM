"""
Basic usage example for PRELIM Python library.

This script demonstrates the basic workflow for using the PRELIM library
to model refinery processes and calculate environmental impacts.
"""

from prelim import Refinery
from prelim.data.assays import get_assay_inventory

def main():
    print("=" * 70)
    print("PRELIM - Petroleum Refinery Life Cycle Inventory Model")
    print("Basic Usage Example")
    print("=" * 70)
    
    # 1. Explore available crude oil assays
    print("\n1. Loading crude oil assay inventory...")
    inventory = get_assay_inventory()
    print(f"   Total assays available: {inventory.count()}")
    
    # Search for specific crudes
    print("\n2. Searching for Alaska crudes...")
    alaska_crudes = inventory.search_assays('Alaska')
    print(f"   Found {len(alaska_crudes)} Alaska crudes:")
    for name in alaska_crudes[:5]:
        print(f"      - {name}")
    
    # 3. Create a refinery model
    print("\n3. Creating refinery model...")
    refinery = Refinery()
    print("   Refinery model created")
    
    # 4. Set crude assay
    print("\n4. Setting crude oil assay...")
    refinery.set_crude_assay('Alaskan North Slope_Exxon')
    print(f"   Assay set: {refinery.current_assay.name}")
    
    # 5. Configure refinery parameters
    print("\n5. Configuring refinery parameters...")
    refinery.configure(
        capacity_bpd=150000,  # 150,000 barrels per day
        power_source='ng_fired',
        include_upstream=True
    )
    print(f"   Capacity: {refinery.config.capacity_bpd} bbl/day")
    
    # 6. View crude properties
    print("\n6. Crude oil properties:")
    props = refinery.get_assay_properties()
    full_crude_props = {k: v for k, v in props.items() if 'Full Crude' in str(k)}
    for prop_name, prop_data in list(full_crude_props.items())[:5]:
        print(f"   {prop_name}: {prop_data}")
    
    # 7. Run calculation (framework demo)
    print("\n7. Running refinery calculations...")
    try:
        results = refinery.run()
        print("   Calculation completed")
        print(f"   Result keys: {list(results.keys())}")
    except NotImplementedError as e:
        print(f"   Note: {e}")
        print("   Full calculation engine implementation in progress")
    
    print("\n" + "=" * 70)
    print("Basic workflow demonstration complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()

