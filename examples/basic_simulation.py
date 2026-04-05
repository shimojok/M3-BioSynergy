"""
M³-BioSynergy: Extended Basic Simulation
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.microbial_diversity import MicrobialDiversityEngine
from src.core.hypercycle_engine import HypercycleEngine
from src.core.nutrient_cascade import NutrientCascadeEngine
from src.core.carbon_flow import CarbonFlowModel
from src.core.ghg_reduction import GHGReductionCalculator


def main():
    print("=" * 70)
    print("M³-BioSynergy: MBT55 Ecosystem Simulation")
    print("=" * 70)
    
    # 初期化
    micro_engine = MicrobialDiversityEngine(n_species=120)
    hyper_engine = HypercycleEngine(n_nodes=4)
    nutrient_engine = NutrientCascadeEngine()
    carbon_model = CarbonFlowModel(use_mbt55=True, soil_type="loam")
    ghg_calc = GHGReductionCalculator(use_mbt55=True)
    
    # 1. 微生物多様性
    print("\n1. Microbial Diversity:")
    init_pop = np.random.uniform(1, 5, 120)
    micro_result = micro_engine.simulate_dynamics(
        initial_population=init_pop, duration_hours=24,
        temperature=28.0, ph=6.8, moisture=0.65, mbt_intervention=1.0
    )
    print(f"   Diversity: {micro_result['final_diversity']:.3f}")
    print(f"   MEI: {micro_result.get('mei', 0):.3f}")
    
    # 2. 炭素流動
    print("\n2. Carbon Flow:")
    cce = carbon_model.calculate_carbon_cycling_efficiency()
    print(f"   CCE: {cce['carbon_cycling_efficiency']:.3f}")
    
    impact = carbon_model.project_10_year_impact(area_ha=100.0)
    print(f"   10-Year Sequestration: {impact['10_year_sequestration_t_co2e']:.0f} tCO₂e")
    
    # 3. GHG削減
    print("\n3. GHG Reduction:")
    ghg = ghg_calc.calculate_total_ghg_reduction(
        waste_volume_tons=1000, area_ha=100.0
    )
    print(f"   Total Reduction: {ghg['total_reduction_tco2e']:,} tCO₂e")
    
    # 4. 経済分析
    print("\n4. Economic Analysis:")
    credits = carbon_model.calculate_carbon_credits(
        area_ha=100.0, duration_years=10, carbon_price_usd=65.0
    )
    print(f"   Carbon Revenue: ${credits['carbon_revenue_usd']:,.0f}")
    
    print("\n" + "=" * 70)
    print("Simulation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
