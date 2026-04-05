"""
M³-BioSynergy: Extended Basic Simulation

This comprehensive simulation demonstrates the complete MBT55 ecosystem:
1. Microbial Diversity & Hypercycle Dynamics
2. Carbon Flow & Sequestration
3. GHG Reduction (9 sources)
4. Soil Carbon Stock Projection
5. Economic Analysis (Carbon Credits, Green Premium)

Based on:
- Ecological Hypercycle Theory
- MBT55 Empirical Data (Bionexus Holdings)
- Africa 510Mt CO₂e Reduction Framework

Author: Kaz Shimojo (Bionexus Holdings)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.microbial_diversity import MicrobialDiversityEngine
from src.core.hypercycle_engine import HypercycleEngine
from src.core.nutrient_cascade import NutrientCascadeEngine
from src.core.carbon_flow import CarbonFlowModel
from src.core.ghg_reduction import GHGReductionCalculator


class MBT55Simulator:
    """
    Complete MBT55 Ecosystem Simulator
    
    Integrates all core components:
    - Microbial diversity (120 species)
    - Hypercycle dynamics
    - Nutrient cascade
    - Carbon flow
    - GHG reduction
    """
    
    def __init__(self, use_mbt55: bool = True, soil_type: str = "loam"):
        """
        Initialize MBT55 simulator
        
        Args:
            use_mbt55: If True, use MBT55-enhanced parameters
            soil_type: Soil classification ('clay', 'loam', 'sand')
        """
        self.use_mbt55 = use_mbt55
        self.soil_type = soil_type
        
        # Initialize all components
        self.microbial_engine = MicrobialDiversityEngine(n_species=120)
        self.hypercycle_engine = HypercycleEngine(n_nodes=4)
        self.nutrient_engine = NutrientCascadeEngine()
        self.carbon_model = CarbonFlowModel(use_mbt55=use_mbt55, soil_type=soil_type)
        self.ghg_calculator = GHGReductionCalculator(use_mbt55=use_mbt55, region_scale="local")
        
        # Simulation results storage
        self.results = {}
    
    def run_full_simulation(self, 
                           area_ha: float = 100.0,
                           waste_tons: float = 1000.0,
                           duration_hours: float = 24.0,
                           temperature: float = 28.0,
                           ph: float = 6.8,
                           moisture: float = 0.65) -> Dict:
        """
        Run complete MBT55 ecosystem simulation
        
        Args:
            area_ha: Agricultural area in hectares
            waste_tons: Organic waste volume in tons
            duration_hours: Simulation duration in hours
            temperature: Soil temperature (°C)
            ph: Soil pH
            moisture: Soil moisture (0-1)
            
        Returns:
            Complete simulation results
        """
        print("=" * 70)
        print("M³-BioSynergy: MBT55 Ecosystem Simulation")
        print("=" * 70)
        
        results = {
            'parameters': {
                'area_ha': area_ha,
                'waste_tons': waste_tons,
                'duration_hours': duration_hours,
                'temperature': temperature,
                'ph': ph,
                'moisture': moisture,
                'use_mbt55': self.use_mbt55,
                'soil_type': self.soil_type
            }
        }
        
        # =========================================================
        # 1. Microbial Diversity Simulation
        # =========================================================
        print("\n" + "-" * 50)
        print("1. Microbial Diversity Simulation (120 species)")
        print("-" * 50)
        
        initial_population = np.random.uniform(1, 5, 120)
        microbial_results = self.microbial_engine.simulate_dynamics(
            initial_population=initial_population,
            duration_hours=duration_hours,
            temperature=temperature,
            ph=ph,
            moisture=moisture,
            mbt_intervention=1.0 if self.use_mbt55 else 0.0
        )
        
        results['microbial'] = {
            'final_diversity': microbial_results['final_diversity'],
            'total_biomass': microbial_results['total_biomass'],
            'mei': microbial_results.get('mei', 0),
            'hypercycle_formed': microbial_results.get('hypercycle_formed', False),
            'diversity_trajectory': microbial_results['diversity_trajectory']
        }
        
        print(f"   Final Diversity Index: {results['microbial']['final_diversity']:.3f}")
        print(f"   Total Microbial Biomass: {results['microbial']['total_biomass']:.0f} units")
        print(f"   MEI (Microbial Emergence Index): {results['microbial']['mei']:.3f}")
        print(f"   Hypercycle Formed: {results['microbial']['hypercycle_formed']}")
        
        # =========================================================
        # 2. Hypercycle Dynamics
        # =========================================================
        print("\n" + "-" * 50)
        print("2. Hypercycle Dynamics Simulation")
        print("-" * 50)
        
        initial_hypercycle = np.array([1.0, 0.5, 0.3, 0.2])
        hypercycle_results = self.hypercycle_engine.simulate_cycle(
            initial_state=initial_hypercycle,
            duration_hours=duration_hours,
            external_input=2.0
        )
        
        results['hypercycle'] = {
            'amplification': hypercycle_results['amplification'],
            'self_sustaining': hypercycle_results['self_sustaining'],
            'hypercycle_formed': hypercycle_results['hypercycle_formed'],
            'efficiency': hypercycle_results.get('efficiency', 0),
            'final_state': hypercycle_results['final_state'].tolist()
        }
        
        print(f"   Amplification Factor: {results['hypercycle']['amplification']:.2f}x")
        print(f"   Self-Sustaining: {results['hypercycle']['self_sustaining']}")
        print(f"   Hypercycle Efficiency: {results['hypercycle']['efficiency']:.3f}")
        
        # =========================================================
        # 3. Nutrient Cascade
        # =========================================================
        print("\n" + "-" * 50)
        print("3. Nutrient Cascade Simulation")
        print("-" * 50)
        
        cascade_results = self.nutrient_engine.simulate_cascade(
            duration_hours=duration_hours,
            temperature=temperature,
            mbt_enhancement=2.5 if self.use_mbt55 else 1.0
        )
        
        results['nutrient'] = {
            'total_humus': cascade_results['total_humus'],
            'carbon_use_efficiency': cascade_results['carbon_use_efficiency'],
            'final_products': cascade_results['final_products']
        }
        
        print(f"   Total Humus Formed: {results['nutrient']['total_humus']:.1f} kg")
        print(f"   Carbon Use Efficiency: {results['nutrient']['carbon_use_efficiency']:.3f}")
        
        # =========================================================
        # 4. Carbon Flow & Sequestration
        # =========================================================
        print("\n" + "-" * 50)
        print("4. Carbon Flow & Sequestration")
        print("-" * 50)
        
        # Carbon Cycling Efficiency
        cce_results = self.carbon_model.calculate_carbon_cycling_efficiency()
        results['carbon']['cce'] = cce_results
        
        # 10-year impact projection
        impact = self.carbon_model.project_10_year_impact(area_ha=area_ha)
        results['carbon']['10_year_impact'] = impact
        
        # Soil carbon simulation
        soil_carbon = self.carbon_model.simulate_carbon_stock(duration_years=20)
        results['carbon']['soil_carbon'] = soil_carbon
        
        print(f"   Carbon Cycling Efficiency: {cce_results['carbon_cycling_efficiency']:.3f}")
        print(f"   10-Year Sequestration: {impact['10_year_sequestration_t_co2e']:.0f} tCO₂e")
        print(f"   SOC Increase: {soil_carbon['soc_increase_percent']:.1f}% over 20 years")
        
        # =========================================================
        # 5. GHG Reduction (9 Sources)
        # =========================================================
        print("\n" + "-" * 50)
        print("5. GHG Reduction Calculation (9 Sources)")
        print("-" * 50)
        
        # Calculate compost produced (40% of waste)
        compost_tons = waste_tons * 0.4
        
        ghg_results = self.ghg_calculator.calculate_total_ghg_reduction(
            waste_volume_tons=waste_tons,
            area_ha=area_ha,
            cattle_head=500,
            sheep_head=1000,
            goat_head=500,
            years=10
        )
        
        results['ghg'] = {
            'total_reduction_tco2e': ghg_results['total_reduction_tco2e'],
            'total_reduction_mtco2e': ghg_results['total_reduction_mtco2e'],
            'sources': ghg_results['sources']
        }
        
        print(f"   Total GHG Reduction: {ghg_results['total_reduction_tco2e']:,} tCO₂e")
        print(f"   Number of Sources: {ghg_results['number_of_sources_calculated']}")
        
        # Display source breakdown
        for source in ghg_results['sources']:
            co2e = source.get('co2e_saved_t', source.get('co2e_sequestered_t', 
                             source.get('co2e_reduction_t', source.get('co2e_accumulated_t', 0))))
            if co2e > 0:
                print(f"     - {source['source']}: {co2e:,.0f} tCO₂e")
        
        # =========================================================
        # 6. Economic Analysis
        # =========================================================
        print("\n" + "-" * 50)
        print("6. Economic Analysis")
        print("-" * 50)
        
        # Carbon credits
        carbon_price_usd = 65.0
        credits = self.carbon_model.calculate_carbon_credits(
            area_ha=area_ha,
            duration_years=10,
            carbon_price_usd=carbon_price_usd,
            verification_level='high'
        )
        
        results['economic'] = {
            'carbon_credits_tco2e': credits['total_credits_t_co2e'],
            'carbon_revenue_usd': credits['carbon_revenue_usd'],
            'per_hectare_revenue': credits['carbon_revenue_usd'] / area_ha if area_ha > 0 else 0,
            'co_benefits': credits['co_benefits']
        }
        
        print(f"   Carbon Credits (10 years): {credits['total_credits_t_co2e']:.0f} tCO₂e")
        print(f"   Carbon Revenue: ${credits['carbon_revenue_usd']:,.0f}")
        print(f"   Revenue per Hectare: ${results['economic']['per_hectare_revenue']:,.0f}/ha")
        print(f"   Co-benefits:")
        for benefit, value in credits['co_benefits'].items():
            print(f"     - {benefit}: {value:,.0f}")
        
        # =========================================================
        # 7. Summary Metrics
        # =========================================================
        print("\n" + "-" * 50)
        print("7. Summary Metrics")
        print("-" * 50)
        
        # Overall ecosystem health score
        health_score = self._calculate_ecosystem_health(results)
        results['summary'] = {
            'ecosystem_health_score': health_score,
            'total_carbon_benefit_tco2e': (
                impact['10_year_sequestration_t_co2e'] + 
                ghg_results['total_reduction_tco2e']
            ),
            'total_economic_value_usd': (
                credits['carbon_revenue_usd'] + 
                credits['co_benefits']['yield_increase_percent'] * 1000  # Approximate
            ),
            'technology_used': 'MBT55' if self.use_mbt55 else 'Conventional'
        }
        
        print(f"   Ecosystem Health Score: {health_score:.1f}/100")
        print(f"   Total Carbon Benefit: {results['summary']['total_carbon_benefit_tco2e']:,.0f} tCO₂e")
        print(f"   Total Economic Value: ${results['summary']['total_economic_value_usd']:,.0f}")
        
        self.results = results
        return results
    
    def _calculate_ecosystem_health(self, results: Dict) -> float:
        """Calculate overall ecosystem health score (0-100)"""
        scores = []
        
        # Microbial diversity (30%)
        if 'microbial' in results:
            diversity = results['microbial']['final_diversity']
            diversity_score = min(100, diversity / 4.0 * 100)  # Max diversity ~4.0
            scores.append(diversity_score * 0.30)
        
        # Hypercycle stability (30%)
        if 'hypercycle' in results:
            stability = 100 if results['hypercycle']['hypercycle_formed'] else 50
            scores.append(stability * 0.30)
        
        # Carbon efficiency (20%)
        if 'carbon' in results and 'cce' in results['carbon']:
            cce = results['carbon']['cce']['carbon_cycling_efficiency']
            cce_score = cce * 100  # CCE 0.8 = 80 points
            scores.append(cce_score * 0.20)
        
        # GHG reduction (20%)
        if 'ghg' in results:
            # Compare to Africa 510Mt target (10% adoption ~ 164Mt)
            ghg_mt = results['ghg']['total_reduction_mtco2e']
            ghg_score = min(100, ghg_mt / 164 * 100)  # 164Mt = 100 points
            scores.append(ghg_score * 0.20)
        
        return sum(scores)
    
    def visualize_results(self, results: Dict = None):
        """Create comprehensive visualization of simulation results"""
        if results is None:
            results = self.results
        
        if not results:
            print("No simulation results to visualize. Run simulation first.")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('M³-BioSynergy: MBT55 Ecosystem Simulation Results', fontsize=14, fontweight='bold')
        
        # Plot 1: Microbial Diversity Trajectory
        ax = axes[0, 0]
        if 'microbial' in results and 'diversity_trajectory' in results['microbial']:
            diversity = results['microbial']['diversity_trajectory']
            time = np.linspace(0, 24, len(diversity))
            ax.plot(time, diversity, 'g-', linewidth=2)
            ax.fill_between(time, 0, diversity, alpha=0.3, color='green')
            ax.set_xlabel('Time (hours)')
            ax.set_ylabel('Shannon Diversity Index')
            ax.set_title('Microbial Diversity Evolution')
            ax.grid(True, alpha=0.3)
        
        # Plot 2: Hypercycle Dynamics
        ax = axes[0, 1]
        if 'hypercycle' in results and 'final_state' in results['hypercycle']:
            nodes = ['Decomp', 'Convert', 'Synth', 'Control']
            initial = [1.0, 0.5, 0.3, 0.2]
            final = results['hypercycle']['final_state']
            x = np.arange(len(nodes))
            width = 0.35
            ax.bar(x - width/2, initial, width, label='Initial', alpha=0.7)
            ax.bar(x + width/2, final, width, label='Final', alpha=0.7)
            ax.set_xlabel('Hypercycle Nodes')
            ax.set_ylabel('Concentration')
            ax.set_title(f'Amplification: {results["hypercycle"]["amplification"]:.1f}x')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Plot 3: Carbon Sequestration Projection
        ax = axes[0, 2]
        if 'carbon' in results and 'soil_carbon' in results['carbon']:
            soil_carbon = results['carbon']['soil_carbon']
            years = soil_carbon['time_years']
            co2e = soil_carbon['co2e_stock_tCO2e_ha']
            ax.plot(years, co2e, 'b-', linewidth=2)
            ax.fill_between(years, 0, co2e, alpha=0.3, color='blue')
            ax.set_xlabel('Years')
            ax.set_ylabel('Soil Carbon Stock (tCO₂e/ha)')
            ax.set_title(f'SOC Increase: +{soil_carbon["soc_increase_percent"]:.1f}%')
            ax.grid(True, alpha=0.3)
        
        # Plot 4: GHG Reduction by Source
        ax = axes[1, 0]
        if 'ghg' in results and 'sources' in results['ghg']:
            sources = []
            reductions = []
            for s in results['ghg']['sources']:
                co2e = s.get('co2e_saved_t', s.get('co2e_sequestered_t', 
                         s.get('co2e_reduction_t', s.get('co2e_accumulated_t', 0))))
                if co2e > 0:
                    # Shorten names for display
                    name = s['source'].replace('Reduction', '').replace('Carbon ', '')
                    if len(name) > 15:
                        name = name[:12] + '...'
                    sources.append(name)
                    reductions.append(co2e)
            
            if sources:
                colors = plt.cm.Set3(np.linspace(0, 1, len(sources)))
                ax.barh(sources, reductions, color=colors)
                ax.set_xlabel('GHG Reduction (tCO₂e)')
                ax.set_title('GHG Reduction by Source')
                ax.grid(True, alpha=0.3, axis='x')
        
        # Plot 5: Economic Benefits
        ax = axes[1, 1]
        if 'economic' in results:
            benefits = []
            values = []
            
            carbon_revenue = results['economic']['carbon_revenue_usd']
            benefits.append('Carbon Credits')
            values.append(carbon_revenue)
            
            # Approximate yield increase value
            yield_value = results['economic']['co_benefits'].get('yield_increase_percent', 0) * 100
            benefits.append('Yield Increase')
            values.append(yield_value)
            
            # Approximate water value
            water_value = results['economic']['co_benefits'].get('water_retention_ml_per_year', 0) * 0.01
            benefits.append('Water Savings')
            values.append(water_value)
            
            colors = ['#2ecc71', '#3498db', '#f39c12']
            ax.bar(benefits, values, color=colors)
            ax.set_ylabel('Economic Value (USD)')
            ax.set_title('Economic Benefits')
            ax.grid(True, alpha=0.3, axis='y')
        
        # Plot 6: Performance Comparison
        ax = axes[1, 2]
        metrics = ['CCE', 'Humification', 'Sequestration', 'GHG Reduction']
        if self.use_mbt55:
            # MBT55 vs Conventional comparison
            conv_model = CarbonFlowModel(use_mbt55=False, soil_type=self.soil_type)
            conv_cce = conv_model.calculate_carbon_cycling_efficiency()
            conv_impact = conv_model.project_10_year_impact(area_ha=100)
            
            mbt_values = [
                results['carbon']['cce']['carbon_cycling_efficiency'] * 100,
                2.8,  # 2.8x humification
                results['carbon']['10_year_impact']['10_year_sequestration_t_co2e'] / 100,
                results['ghg']['total_reduction_mtco2e'] * 10
            ]
            conv_values = [
                conv_cce['carbon_cycling_efficiency'] * 100,
                1.0,
                conv_impact['10_year_sequestration_t_co2e'] / 100,
                1.0
            ]
            
            x = np.arange(len(metrics))
            width = 0.35
            ax.bar(x - width/2, mbt_values, width, label='MBT55', alpha=0.8, color='#2ecc71')
            ax.bar(x + width/2, conv_values, width, label='Conventional', alpha=0.8, color='#e74c3c')
            ax.set_xticks(x)
            ax.set_xticklabels(metrics)
            ax.set_ylabel('Relative Performance')
            ax.set_title('MBT55 vs Conventional')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('mbt55_simulation_results.png', dpi=300, bbox_inches='tight')
        print("\n✅ Visualization saved to 'mbt55_simulation_results.png'")
        plt.show()


def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("M³-BioSynergy: Extended MBT55 Simulation")
    print("Ecological Hypercycle Theory Implementation")
    print("=" * 70)
    
    # Initialize simulator
    simulator = MBT55Simulator(use_mbt55=True, soil_type="loam")
    
    # Run full simulation
    results = simulator.run_full_simulation(
        area_ha=100.0,
        waste_tons=1000.0,
        duration_hours=24.0,
        temperature=28.0,
        ph=6.8,
        moisture=0.65
    )
    
    # Visualize results
    simulator.visualize_results()
    
    # Export results to JSON
    import json
    from datetime import datetime
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'simulation': {
            'type': 'MBT55 Ecosystem Simulation',
            'version': '2.0.0'
        },
        'results': {
            'microbial': {
                'final_diversity': results['microbial']['final_diversity'],
                'mei': results['microbial']['mei'],
                'hypercycle_formed': results['microbial']['hypercycle_formed']
            },
            'carbon': {
                'cce': results['carbon']['cce']['carbon_cycling_efficiency'],
                'ten_year_sequestration': results['carbon']['10_year_impact']['10_year_sequestration_t_co2e'],
                'soc_increase_percent': results['carbon']['soil_carbon']['soc_increase_percent']
            },
            'economic': {
                'carbon_revenue_usd': results['economic']['carbon_revenue_usd'],
                'per_hectare_revenue': results['economic']['per_hectare_revenue']
            },
            'summary': results['summary']
        }
    }
    
    with open('simulation_output.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n📁 Detailed results saved to 'simulation_output.json'")
    print("\n" + "=" * 70)
    print("Simulation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
```
