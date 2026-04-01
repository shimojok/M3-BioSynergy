"""
Ecological Hypercycle Engine
Implements self-amplifying cyclic metabolic networks
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class HypercycleNode:
    """Node in hypercycle network"""
    id: str
    name: str
    catalytic_activity: float
    production_rate: float
    consumption_rate: float
    coupling_strength: Dict[str, float] = None


class HypercycleEngine:
    """Core engine for ecological hypercycle simulation"""
    
    def __init__(self, n_nodes: int = 4):
        self.n_nodes = n_nodes
        self.nodes: List[HypercycleNode] = []
        self.coupling_matrix: np.ndarray = None
        self._initialize_hypercycle()
    
    def _initialize_hypercycle(self):
        """Initialize MBT55 hypercycle with 4 functional nodes"""
        node_names = ['Decomposition', 'Conversion', 'Synthesis', 'Regulation']
        
        for i, name in enumerate(node_names):
            node = HypercycleNode(
                id=f"H{i+1}",
                name=name,
                catalytic_activity=np.random.uniform(0.5, 1.0),
                production_rate=np.random.uniform(0.3, 0.8),
                consumption_rate=np.random.uniform(0.1, 0.4),
                coupling_strength={}
            )
            self.nodes.append(node)
        
        self._build_coupling_matrix()
    
    def _build_coupling_matrix(self):
        """Build hypercycle coupling matrix γ_ij (cyclic structure)"""
        n = self.n_nodes
        gamma = np.zeros((n, n))
        
        for i in range(n):
            j = (i + 1) % n
            gamma[i, j] = self.nodes[i].catalytic_activity * 0.8
        
        self.coupling_matrix = gamma
    
    def simulate_cycle(self,
                      initial_state: np.ndarray,
                      duration_hours: float = 24.0,
                      external_input: float = 0.0) -> Dict:
        """Simulate hypercycle dynamics"""
        n = self.n_nodes
        dt = 0.1
        n_steps = int(duration_hours / dt)
        
        state = np.zeros((n_steps + 1, n))
        state[0] = initial_state
        
        for step in range(n_steps):
            current = state[step]
            next_state = current.copy()
            
            for i in range(n):
                growth = self.nodes[i].production_rate * current[i]
                coupling = 0.0
                for j in range(n):
                    if self.coupling_matrix[j, i] > 0:
                        coupling += self.coupling_matrix[j, i] * current[j]
                loss = self.nodes[i].consumption_rate * current[i]
                external = external_input if i == 0 else 0
                
                next_state[i] = current[i] + (growth * (1 + coupling) - loss + external) * dt
                next_state[i] = max(next_state[i], 0)
            
            state[step + 1] = next_state
        
        final_state = state[-1]
        amplification = np.sum(final_state) / np.sum(initial_state)
        coupling_activity = np.sum(self.coupling_matrix) / (n * n)
        self_sustaining = all(final_state > initial_state * 0.5)
        
        return {
            'time': np.linspace(0, duration_hours, n_steps + 1),
            'state': state,
            'final_state': final_state,
            'amplification': amplification,
            'coupling_activity': coupling_activity,
            'self_sustaining': self_sustaining,
            'hypercycle_formed': amplification > 1.5 and coupling_activity > 0.3
        }
    
    def get_hypercycle_metrics(self) -> Dict:
        return {
            'n_nodes': self.n_nodes,
            'catalytic_activities': [node.catalytic_activity for node in self.nodes],
            'production_rates': [node.production_rate for node in self.nodes],
            'consumption_rates': [node.consumption_rate for node in self.nodes]
        }