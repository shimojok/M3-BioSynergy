"""
Core microbial dynamics modeling for MBT55 symbiotic network.
Implements Ecological Hypercycle Theory through differential equations.
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, List, Optional


class MicrobialEcosystem:
    """Models the 120-species MBT55 consortium as a dynamic system."""
    
    def __init__(self, n_species: int = 120):
        self.n_species = n_species
        self.interaction_matrix = self._create_interaction_matrix()
        self.growth_rates = np.random.uniform(0.1, 0.8, n_species)
        
    def _create_interaction_matrix(self) -> np.ndarray:
        """Create symbiotic interaction matrix."""
        matrix = np.zeros((self.n_species, self.n_species))
        for i in range(self.n_species):
            for j in range(self.n_species):
                if i == j:
                    matrix[i, j] = -0.05  # Self-competition
                elif np.random.random() > 0.7:  # 30% symbiotic
                    matrix[i, j] = np.random.uniform(0.01, 0.1)
        return matrix
    
    def simulate(self, 
                 initial_population: np.ndarray,
                 duration_hours: float = 24.0,
                 temperature: float = 25.0,
                 mbt_intervention: float = 1.0) -> Dict:
        """
        Simulate microbial ecosystem dynamics.
        
        Args:
            initial_population: Initial population of each species
            duration_hours: Simulation duration in hours
            temperature: Environmental temperature (°C)
            mbt_intervention: MBT55 application level (0.0 to 1.0)
            
        Returns:
            Simulation results including population dynamics
        """
        def system(t, y):
            # Lotka-Volterra extended model
            growth = self.growth_rates * y * (1 - y / 1000)
            interactions = self.interaction_matrix @ y
            temperature_factor = np.exp(-((temperature - 30) / 15) ** 2)
            
            return (growth + interactions * mbt_intervention) * temperature_factor
        
        solution = solve_ivp(
            system,
            [0, duration_hours],
            initial_population,
            method='RK45',
            dense_output=True
        )
        
        return {
            'time': solution.t,
            'populations': solution.y,
            'total_biomass': np.sum(solution.y, axis=0),
            'diversity': self._calculate_diversity(solution.y[:, -1])
        }
    
    def _calculate_diversity(self, population: np.ndarray) -> float:
        """Calculate Shannon diversity index."""
        proportions = population / np.sum(population)
        proportions = proportions[proportions > 0]
        return -np.sum(proportions * np.log(proportions))
