"""
Basic simulation example for M³-BioSynergy.
Demonstrates microbial ecosystem dynamics and carbon sequestration.
"""

import numpy as np
import matplotlib.pyplot as plt
from src.core.microbial_dynamics import MicrobialEcosystem


def run_basic_simulation():
    """Run and visualize basic simulation."""
    
    print("=" * 60)
    print("M³-BioSynergy: Basic Simulation")
    print("=" * 60)
    
    # 1. Initialize ecosystem
    ecosystem = MicrobialEcosystem(n_species=120)
    
    # 2. Set initial conditions
    initial_population = np.random.uniform(1, 5, 120)
    
    print("\n1. Microbial Ecosystem Initialized")
    print(f"   - Number of species: {ecosystem.n_species}")
    print(f"   - Initial total biomass: {np.sum(initial_population):.2f}")
    
    # 3. Run simulation
    print("\n2. Running 24-hour simulation...")
    results = ecosystem.simulate(
        initial_population=initial_population,
        duration_hours=24.0,
        temperature=28.0,
        mbt_intervention=1.0
    )
    
    # 4. Display results
    print("\n3. Simulation Results:")
    print(f"   - Final total biomass: {results['total_biomass'][-1]:.2f}")
    print(f"   - Shannon diversity: {results['diversity']:.3f}")
    print(f"   - Biomass increase: {(results['total_biomass'][-1]/np.sum(initial_population)-1):.1%}")
    
    # 5. Visualization
    print("\n4. Generating visualization...")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot 1: Total biomass over time
    axes[0].plot(results['time'], results['total_biomass'], 'b-', linewidth=2)
    axes[0].set_xlabel('Time (hours)')
    axes[0].set_ylabel('Total Microbial Biomass')
    axes[0].set_title('Microbial Growth Dynamics')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Species distribution
    final_population = results['populations'][:, -1]
    top_10_indices = np.argsort(final_population)[-10:]
    top_10_values = final_population[top_10_indices]
    
    axes[1].bar(range(10), top_10_values, color='green', alpha=0.7)
    axes[1].set_xlabel('Species (Top 10)')
    axes[1].set_ylabel('Population')
    axes[1].set_title('Dominant Species Distribution')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('simulation_results.png', dpi=300, bbox_inches='tight')
    
    print(f"\n✅ Simulation completed!")
    print(f"📊 Results saved to 'simulation_results.png'")
    
    return results


if __name__ == "__main__":
    # Run the simulation
    results = run_basic_simulation()
    
    # Save detailed results
    import json
    with open('simulation_output.json', 'w') as f:
        json.dump({
            'time': results['time'].tolist(),
            'total_biomass': results['total_biomass'].tolist(),
            'diversity': results['diversity']
        }, f, indent=2)
    
    print("📁 Detailed results saved to 'simulation_output.json'")
