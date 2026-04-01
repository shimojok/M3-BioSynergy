"""
Microbial Diversity Model for MBT55 Consortium
Implements 120-species symbiotic network based on Ecological Hypercycle Theory
"""

import numpy as np
from scipy.integrate import odeint
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MicrobialSpecies:
    """Individual microbial species in MBT55 consortium"""
    id: int
    name: str
    functional_group: str
    metabolic_type: str
    growth_rate: float
    substrate_affinity: float
    temperature_optimum: float
    ph_optimum: float
    synergy_potential: float = 0.0
    redundancy_index: float = 0.0


class MicrobialDiversityEngine:
    """Core engine for 120-species microbial diversity modeling"""
    
    def __init__(self, n_species: int = 120):
        self.n_species = n_species
        self.species: List[MicrobialSpecies] = []
        self.interaction_matrix: np.ndarray = None
        self._initialize_mbt55_consortium()
    
    def _initialize_mbt55_consortium(self):
        """Initialize MBT55-specific 120-species consortium"""
        functional_groups = {
            'decomposer': 0.40,
            'converter': 0.25,
            'synthesizer': 0.20,
            'controller': 0.15
        }
        
        species_id = 0
        species_list = []
        
        for group, proportion in functional_groups.items():
            n_in_group = int(self.n_species * proportion)
            
            for i in range(n_in_group):
                if group == 'decomposer':
                    growth_rate = np.random.uniform(0.6, 0.9)
                    temp_opt = np.random.uniform(25, 35)
                    metabolic = np.random.choice(['aerobic', 'facultative'], p=[0.7, 0.3])
                elif group == 'converter':
                    growth_rate = np.random.uniform(0.4, 0.7)
                    temp_opt = np.random.uniform(30, 40)
                    metabolic = np.random.choice(['facultative', 'anaerobic'], p=[0.6, 0.4])
                elif group == 'synthesizer':
                    growth_rate = np.random.uniform(0.3, 0.5)
                    temp_opt = np.random.uniform(20, 30)
                    metabolic = np.random.choice(['aerobic', 'facultative'], p=[0.5, 0.5])
                else:
                    growth_rate = np.random.uniform(0.2, 0.4)
                    temp_opt = np.random.uniform(25, 35)
                    metabolic = np.random.choice(['facultative', 'anaerobic'], p=[0.4, 0.6])
                
                species = MicrobialSpecies(
                    id=species_id,
                    name=f"MBT55_{group}_{i:03d}",
                    functional_group=group,
                    metabolic_type=metabolic,
                    growth_rate=growth_rate,
                    substrate_affinity=np.random.uniform(0.1, 2.0),
                    temperature_optimum=temp_opt,
                    ph_optimum=np.random.uniform(6.0, 7.5),
                    synergy_potential=np.random.uniform(0.1, 0.5),
                    redundancy_index=np.random.uniform(0.3, 0.8)
                )
                species_list.append(species)
                species_id += 1
        
        self.species = species_list
        self._generate_interaction_matrix()
    
    def _generate_interaction_matrix(self):
        """Generate symbiotic interaction matrix γ_ij"""
        n = self.n_species
        gamma = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    gamma[i, j] = -0.05
                else:
                    if self._should_interact(self.species[i], self.species[j]):
                        strength = np.random.uniform(0.02, 0.15)
                        gamma[i, j] = strength
                        if self.species[j].functional_group == 'controller':
                            gamma[i, j] *= 1.5
        
        self.interaction_matrix = gamma
        self._calculate_mei()
    
    def _should_interact(self, sp1: MicrobialSpecies, sp2: MicrobialSpecies) -> bool:
        """Determine if two species should have symbiotic interaction"""
        base_prob = 0.75
        
        complementary_pairs = [
            ('decomposer', 'converter'),
            ('converter', 'synthesizer'),
            ('synthesizer', 'controller'),
            ('controller', 'decomposer')
        ]
        
        if (sp1.functional_group, sp2.functional_group) in complementary_pairs:
            base_prob += 0.15
            
        return np.random.random() < base_prob
    
    def _calculate_mei(self):
        """Calculate Microbial Emergence Index (MEI) = Σγ_ij / √n"""
        n = self.n_species
        total_gamma = np.sum(np.abs(self.interaction_matrix))
        self.mei = total_gamma / np.sqrt(n)
        self.hypercycle_threshold = 0.85
        self.hypercycle_formed = self.mei > self.hypercycle_threshold
    
    def simulate_dynamics(self,
                         initial_population: np.ndarray,
                         duration_hours: float = 24.0,
                         temperature: float = 25.0,
                         ph: float = 6.8,
                         moisture: float = 0.6,
                         mbt_intervention: float = 1.0) -> Dict:
        """Simulate microbial population dynamics over time"""
        
        def system(state, t):
            env_factor = self._environmental_stress_factor(temperature, ph, moisture)
            growth_rates = np.array([sp.growth_rate for sp in self.species])
            growth = growth_rates * state * (1 - state / 10000) * env_factor
            interactions = self.interaction_matrix @ state * mbt_intervention
            
            controller_indices = [i for i, sp in enumerate(self.species) 
                                 if sp.functional_group == 'controller']
            if controller_indices:
                controller_activity = np.mean(state[controller_indices]) / 1000
                interactions *= (1 + controller_activity * 0.5)
            
            return growth + interactions
        
        t = np.linspace(0, duration_hours, 100)
        solution = odeint(system, initial_population, t)
        
        final_population = solution[-1]
        total_biomass = np.sum(final_population)
        
        diversity_time = []
        for pop in solution:
            proportions = pop / np.sum(pop)
            proportions = proportions[proportions > 0]
            diversity_time.append(-np.sum(proportions * np.log(proportions)))
        
        return {
            'time': t,
            'population': solution,
            'final_population': final_population,
            'total_biomass': total_biomass,
            'diversity_trajectory': np.array(diversity_time),
            'final_diversity': diversity_time[-1],
            'mei': self.mei,
            'hypercycle_formed': self.hypercycle_formed
        }
    
    def _environmental_stress_factor(self, temp: float, ph: float, moisture: float) -> float:
        """Calculate environmental stress factor"""
        temp_factor = self._temperature_response(temp)
        ph_factor = self._ph_response(ph)
        moisture_factor = self._moisture_response(moisture)
        return 0.5 * temp_factor + 0.3 * ph_factor + 0.2 * moisture_factor
    
    def _temperature_response(self, temp: float) -> float:
        if 20 <= temp <= 40:
            return 1.0
        elif temp < 10:
            return 0.3 + 0.07 * temp
        elif temp > 45:
            return 1.5 - 0.03 * temp
        else:
            return np.exp(-0.5 * ((temp - 30) / 15) ** 2)
    
    def _ph_response(self, ph: float) -> float:
        if 6.0 <= ph <= 7.5:
            return 1.0
        elif ph < 5.0:
            return 0.4
        elif ph > 8.5:
            return 0.5
        else:
            return np.exp(-0.5 * ((ph - 6.8) / 1.2) ** 2)
    
    def _moisture_response(self, moisture: float) -> float:
        if 0.4 <= moisture <= 0.8:
            return 1.0
        elif moisture < 0.2:
            return 0.2
        elif moisture > 0.9:
            return 0.7
        else:
            if moisture < 0.4:
                return 0.2 + 2.0 * moisture
            else:
                return 2.6 - 2.0 * moisture
    
    def get_emergent_metrics(self) -> Dict:
        return {
            'species_count': self.n_species,
            'mei': self.mei,
            'hypercycle_threshold': self.hypercycle_threshold,
            'hypercycle_formed': self.hypercycle_formed
        }