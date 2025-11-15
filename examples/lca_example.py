"""
Life cycle assessment example.

Demonstrates how to build life cycle inventories and calculate
environmental impacts using TRACI.
"""

from prelim.lca.inventory import LifeCycleInventory
from prelim.lca.impact_assessment import ImpactAssessment, assess_refinery_impacts


def main():
    print("=" * 70)
    print("Life Cycle Assessment Example")
    print("=" * 70)
    
    # Create a sample inventory for a refinery process
    print("\n1. Creating life cycle inventory...")
    inventory = LifeCycleInventory("Diesel Production")
    
    # Add some typical refinery emissions
    print("   Adding emissions...")
    inventory.add_emission('Carbon dioxide', 'air', 1000.0, 'kg')
    inventory.add_emission('Methane', 'air', 5.0, 'kg')
    inventory.add_emission('nitrogen oxides', 'air', 2.5, 'kg')
    inventory.add_emission('sulfur dioxide', 'air', 1.2, 'kg')
    inventory.add_emission('VOC, volatile organic compounds', 'air', 0.8, 'kg')
    
    # Add resource inputs
    print("   Adding resource inputs...")
    inventory.add_resource('Natural gas', 5000.0, 'm3')
    inventory.add_resource('Electricity', 2000.0, 'kWh')
    
    print(f"   Total inventory entries: {len(inventory)}")
    
    # Calculate impacts
    print("\n2. Calculating environmental impacts (TRACI 2.1)...")
    assessment = ImpactAssessment()
    impacts = assessment.calculate_impacts(inventory)
    
    print("\n   Impact Assessment Results:")
    print("   " + "-" * 60)
    
    # Display non-zero impacts
    for category, score in impacts.items():
        if score > 0:
            print(f"   {category:<35} {score:>15.4e}")
    
    # Get breakdown for Global Warming
    print("\n3. Global Warming impact breakdown:")
    breakdown = assessment.get_impact_breakdown(inventory, 'kg CO2 eq / kg')
    print("   " + "-" * 60)
    for flow, contribution in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        if contribution > 0:
            percent = (contribution / impacts['kg CO2 eq / kg']) * 100
            print(f"   {flow:<40} {contribution:>10.2f} ({percent:>5.1f}%)")
    
    # Normalize to functional unit
    print("\n4. Normalized impacts (per kg diesel):")
    # Assume we produced 1000 kg diesel
    functional_unit = 1000.0  # kg diesel
    normalized = assessment.normalize_impacts(impacts, functional_unit)
    
    print("   " + "-" * 60)
    for category, score in normalized.items():
        if score > 0:
            print(f"   {category:<35} {score:>15.4e}")
    
    print("\n" + "=" * 70)
    print("LCA example complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()

