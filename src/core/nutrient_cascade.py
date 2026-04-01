"""
Nutrient Cascade Module
Three-stage decomposition → conversion → synthesis model
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class CascadeStage:
    """Individual stage in nutrient cascade"""
    name: str
    input_substrates: List[str]
    output_products: List[str]
    conversion_efficiency: float
    rate_constant: float
    temperature_optimum: float
    ph_optimum: float


class NutrientCascadeEngine:
    """Three-stage nutrient cascade model based on MBT55 data"""
    
    def __init__(self):
        self.stages = self._initialize_cascade()
        self.substrate_pools = {}
        self.product_pools = {}
        self._initialize_pools()
    
    def _initialize_cascade(self) -> List[CascadeStage]:
        return [
            CascadeStage(
                name="Decomposition",
                input_substrates=["lignin", "cellulose", "protein", "lipid"],
                output_products=["simple_sugars", "amino_acids", "fatty_acids"],
                conversion_efficiency=0.85,
                rate_constant=0.5,
                temperature_optimum=30.0,
                ph_optimum=6.8
            ),
            CascadeStage(
                name="Conversion",
                input_substrates=["simple_sugars", "amino_acids", "fatty_acids"],
                output_products=["organic_acids", "alcohols", "short_chain"],
                conversion_efficiency=0.75,
                rate_constant=0.4,
                temperature_optimum=32.0,
                ph_optimum=6.5
            ),
            CascadeStage(
                name="Synthesis",
                input_substrates=["organic_acids", "alcohols", "short_chain"],
                output_products=["humic_acids", "fulvic_acids", "bioactive_compounds"],
                conversion_efficiency=0.65,
                rate_constant=0.3,
                temperature_optimum=28.0,
                ph_optimum=7.0
            )
        ]
    
    def _initialize_pools(self):
        self.substrate_pools = {
            'lignin': 100.0, 'cellulose': 100.0, 'protein': 50.0, 'lipid': 30.0
        }
        self.product_pools = {
            'simple_sugars': 0.0, 'amino_acids': 0.0, 'fatty_acids': 0.0,
            'organic_acids': 0.0, 'humic_acids': 0.0, 'fulvic_acids': 0.0
        }
    
    def simulate_cascade(self, duration_hours: float = 24.0, 
                         temperature: float = 25.0,
                         mbt_enhancement: float = 1.0) -> Dict:
        """Simulate nutrient cascade over time"""
        dt = 0.1
        n_steps = int(duration_hours / dt)
        
        history = {'time': [], 'stage1': [], 'stage2': [], 'stage3': [], 'total_conversion': []}
        current_substrates = self.substrate_pools.copy()
        current_products = self.product_pools.copy()
        
        for step in range(n_steps):
            t = step * dt
            
            for stage in self.stages:
                rate = (stage.rate_constant * 
                       np.exp(0.1 * (temperature - stage.temperature_optimum)) *
                       mbt_enhancement)
                
                for substrate in stage.input_substrates:
                    if current_substrates.get(substrate, 0) > 0:
                        conversion = current_substrates[substrate] * rate * dt * 0.1
                        conversion = min(conversion, current_substrates[substrate])
                        current_substrates[substrate] -= conversion
                        
                        for product in stage.output_products:
                            current_products[product] = current_products.get(product, 0) + conversion * 0.7
                
                for product in stage.input_substrates:
                    if current_products.get(product, 0) > 0 and stage.name != "Decomposition":
                        conversion = current_products[product] * rate * dt * 0.15
                        conversion = min(conversion, current_products[product])
                        current_products[product] -= conversion
                        
                        for out_product in stage.output_products:
                            current_products[out_product] = current_products.get(out_product, 0) + conversion * 0.6
            
            if step % 100 == 0:
                history['time'].append(t)
                history['stage1'].append(sum(current_products.get(p, 0) for p in self.stages[0].output_products))
                history['stage2'].append(sum(current_products.get(p, 0) for p in self.stages[1].output_products))
                history['stage3'].append(sum(current_products.get(p, 0) for p in self.stages[2].output_products))
                history['total_conversion'].append(sum(current_products.values()))
        
        final_products = sum(current_products.values())
        initial_total = sum(self.product_pools.values())
        cue = final_products / initial_total if initial_total > 0 else 0
        
        return {
            'history': history,
            'final_substrates': current_substrates,
            'final_products': current_products,
            'total_humus': current_products.get('humic_acids', 0) + current_products.get('fulvic_acids', 0),
            'carbon_use_efficiency': cue
        }