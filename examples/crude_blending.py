"""
Crude oil blending example.

Demonstrates how to create custom crude blends using the blending module.
"""

from prelim.core.crude_blending import create_custom_blend
from prelim.data.assays import get_assay_inventory


def main():
    print("=" * 70)
    print("Crude Oil Blending Example")
    print("=" * 70)
    
    inventory = get_assay_inventory()
    
    # Example 1: Blend two crudes
    print("\n1. Creating a 60/40 blend of two crudes...")
    
    # Find some available assays
    all_assays = inventory.list_assays()
    crude1_name = 'Alaskan North Slope_Exxon'
    crude2_name = all_assays[10] if len(all_assays) > 10 else all_assays[1]
    
    print(f"   Crude 1 (60%): {crude1_name}")
    print(f"   Crude 2 (40%): {crude2_name}")
    
    try:
        blend = create_custom_blend(
            [crude1_name, crude2_name],
            [0.6, 0.4],
            refinery_capacity_bpd=100000
        )
        
        print(f"\n   Blend created: {blend.name}")
        print(f"   Fractions: {', '.join(blend.fractions)}")
        
        # Compare properties
        crude1 = inventory.get_assay(crude1_name)
        crude2 = inventory.get_assay(crude2_name)
        
        print("\n   API Gravity comparison:")
        print(f"      Crude 1: {crude1.get_property('API gravity', 'Full Crude'):.2f}")
        print(f"      Crude 2: {crude2.get_property('API gravity', 'Full Crude'):.2f}")
        print(f"      Blend:   {blend.get_property('API gravity', 'Full Crude'):.2f}")
        
        print("\n   Sulfur content comparison:")
        print(f"      Crude 1: {crude1.get_property('Sulfur', 'Full Crude'):.4f} wt%")
        print(f"      Crude 2: {crude2.get_property('Sulfur', 'Full Crude'):.4f} wt%")
        print(f"      Blend:   {blend.get_property('Sulfur', 'Full Crude'):.4f} wt%")
        
    except Exception as e:
        print(f"   Error creating blend: {e}")
    
    # Example 2: Three-crude blend
    print("\n\n2. Creating a three-crude blend (50/30/20)...")
    
    if len(all_assays) >= 3:
        crude3_name = all_assays[20] if len(all_assays) > 20 else all_assays[2]
        
        print(f"   Crude 1 (50%): {crude1_name}")
        print(f"   Crude 2 (30%): {crude2_name}")
        print(f"   Crude 3 (20%): {crude3_name}")
        
        try:
            blend2 = create_custom_blend(
                [crude1_name, crude2_name, crude3_name],
                [0.5, 0.3, 0.2]
            )
            
            print(f"\n   Blend created: {blend2.name}")
            print(f"   Density: {blend2.get_property('Density', 'Full Crude'):.2f} kg/m³")
            
        except Exception as e:
            print(f"   Error creating blend: {e}")
    
    print("\n" + "=" * 70)
    print("Blending example complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()

