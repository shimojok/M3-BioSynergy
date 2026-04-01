"""
M³-BioSynergy Core Module
Microbial-Metabolic-Modular Theory Implementation
"""

from .microbial_diversity import MicrobialDiversityEngine, MicrobialSpecies
from .hypercycle_engine import HypercycleEngine, HypercycleNode
from .nutrient_cascade import NutrientCascadeEngine, CascadeStage

__all__ = [
    'MicrobialDiversityEngine',
    'MicrobialSpecies',
    'HypercycleEngine',
    'HypercycleNode',
    'NutrientCascadeEngine',
    'CascadeStage'
]

__version__ = '1.0.0'