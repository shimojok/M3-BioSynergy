"""
Greenhouse Gas Reduction Calculator for MBT55 System
Implements 9-source GHG reduction calculation based on MBT Sustainable Cycle

Sources:
1. Waste-to-resource conversion (methane avoidance)
2. Soil carbon sequestration (SOC increase)
3. Fertilizer reduction (production CO₂ avoidance)
4. Livestock methane reduction
5. Food loss reduction
6. Biomass carbon accumulation
7. Transportation reduction
8. Fossil fuel replacement (biogas)
9. N₂O reduction from improved nitrogen cycling

Based on theoretical framework from:
- Africa 510Mt CO₂e Reduction Simulation
- MBT Hypercycle Superiority Documentation
- FAO/IPCC emission factors
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class WasteType(Enum):
    """Types of organic waste for GHG calculation"""
    FOOD_WASTE = "food_waste"
    LIVESTOCK_MANURE = "livestock_manure"
    AGRICULTURAL_RESIDUE = "agricultural_residue"
    SEWAGE_SLUDGE = "sewage_sludge"
    PROCESSING_WASTE = "processing_waste"


class LivestockType(Enum):
    """Livestock types for methane calculation"""
    CATTLE = "cattle"
    SHEEP = "sheep"
    GOAT = "goat"
    POULTRY = "poultry"


@dataclass
class GHGParameters:
    """GHG emission factors and reduction parameters"""
    # GWP (Global Warming Potential) factors
    gwp_ch4: float = 28.0      # Methane GWP over 100 years
    gwp_n2o: float = 298.0     # Nitrous oxide GWP over 100 years
    
    # Waste management
    landfill_methane_factor: float = 0.6      # kg CH₄/kg waste
    compost_methane_factor: float = 0.06      # kg CH₄/kg waste
    mbt_methane_reduction: float = 0.82       # 82% reduction
    
    # Soil carbon
    soc_conversion_factor: float = 3.67       # tC to tCO₂e
    baseline_soc_increase: float = 0.6        # % per year conventional
    mbt_soc_increase: float = 1.3             # % per year MBT55
    
    # Fertilizer
    fertilizer_production_co2: float = 5.0    # kg CO₂/kg N fertilizer
    fertilizer_replacement_rate: float = 0.40 # 40% reduction
    
    # Livestock
    cattle_methane_factor: float = 70.0       # kg CH₄/head/year
    sheep_methane_factor: float = 8.0         # kg CH₄/head/year
    goat_methane_factor: float = 8.0          # kg CH₄/head/year
    mbt_livestock_reduction: float = 0.30     # 30% reduction
    
    # Food loss
    food_loss_emission_factor: float = 2.5    # kg CO₂e/kg food loss
    mbt_food_loss_reduction: float = 0.50     # 50% reduction
    
    # Biomass
    biomass_carbon_factor: float = 0.45       # 45% carbon content
    biomass_increase_rate: float = 0.50       # 50% increase
    
    # Transportation
    transport_emission_factor: float = 0.2    # kg CO₂e/t·km
    transport_distance_reduction: float = 0.50 # 50% reduction
    avg_transport_distance: float = 50.0      # km
    
    # Energy (biogas)
    biogas_emission_offset: float = 0.6       # kg CO₂e/kWh displaced
    biogas_yield: float = 0.10                # 100 m³/ton waste
    
    # N₂O from nitrogen cycling
    n2o_emission_factor: float = 0.01         # 1% of N becomes N₂O
    fertilizer_n_content: float = 0.30        # 30% nitrogen in fertilizer
    mbt_n2o_reduction: float = 0.72           # 72% reduction


@dataclass
class AfricaScaleData:
    """Africa-wide data for scaling calculations"""
    total_population: float = 1.4e9           # 1.4 billion
    cattle_population: float = 350e6          # 350 million
    sheep_population: float = 400e6           # 400 million
    goat_population: float = 400e6            # 400 million
    poultry_population: float = 2e9           # 2 billion
    agricultural_land_ha: float = 1e9         # 1 billion ha
    degraded_land_ha: float = 300e6           # 300 million ha
    urban_population_ratio: float = 0.45
    rural_population_ratio: float = 0.55


class GHGReductionCalculator:
    """
    Greenhouse Gas Reduction Calculator for MBT55 System
    
    Calculates GHG reduction from 9 sources based on:
    - Africa 510Mt CO₂e reduction simulation
    - MBT Hypercycle theoretical framework
    - Empirical data from field trials
    """
    
    def __init__(self, use_mbt55: bool = True, region_scale: str = "local"):
        """
        Initialize GHG reduction calculator
        
        Args:
            use_mbt55: If True, use MBT55 enhancement factors
            region_scale: 'local', 'africa', or 'global'
        """
        self.use_mbt55 = use_mbt55
        self.region_scale = region_scale
        self.params = GHGParameters()
        
        if region_scale == "africa":
            self.africa_data = AfricaScaleData()
    
    # =========================================================
    # Source 1: Waste-to-Resource (Methane Avoidance)
    # =========================================================
    
    def calculate_waste_methane_avoidance(self,
                                         waste_volume_tons: float,
                                         waste_type: WasteType = WasteType.FOOD_WASTE) -> Dict:
        """
        Calculate methane avoidance from waste-to-resource conversion
        
        Formula: CH₄_avoided = waste_volume × (landfill_factor - mbt_factor) × GWP
        
        Args:
            waste_volume_tons: Annual waste volume in tons
            waste_type: Type of organic waste
            
        Returns:
            Methane avoidance in tCO₂e
        """
        if self.use_mbt55:
            mbt_factor = self.params.compost_methane_factor * (1 - self.params.mbt_methane_reduction)
        else:
            mbt_factor = self.params.compost_methane_factor
        
        # Landfill baseline (worst case)
        landfill_factor = self.params.landfill_methane_factor
        
        # Calculate methane avoided
        ch4_avoided = waste_volume_tons * (landfill_factor - mbt_factor)
        co2e_avoided = ch4_avoided * self.params.gwp_ch4
        
        return {
            'source': 'Waste-to-Resource',
            'methane_avoided_kg': round(ch4_avoided, 0),
            'co2e_avoided_t': round(co2e_avoided / 1000, 2),
            'reduction_rate': self.params.mbt_methane_reduction if self.use_mbt55 else 0.0,
            'per_ton_factor': round((landfill_factor - mbt_factor) * self.params.gwp_ch4, 2)
        }
    
    # =========================================================
    # Source 2: Soil Carbon Sequestration
    # =========================================================
    
    def calculate_soil_carbon_sequestration(self,
                                           area_ha: float,
                                           years: int = 10) -> Dict:
        """
        Calculate soil carbon sequestration from MBT55 application
        
        Formula: SOC_increase = area × (mbt_rate - baseline_rate) × years × conversion_factor
        
        Args:
            area_ha: Area in hectares
            years: Project duration in years
            
        Returns:
            Soil carbon sequestration in tCO₂e
        """
        if self.use_mbt55:
            soc_rate = self.params.mbt_soc_increase  # % per year
            enhancement = True
        else:
            soc_rate = self.params.baseline_soc_increase
            enhancement = False
        
        # Assume initial SOC of 50 tC/ha
        initial_soc = 50.0
        soc_increase = initial_soc * (soc_rate / 100) * years * area_ha
        
        # Convert to CO₂e
        co2e_sequestered = soc_increase * self.params.soc_conversion_factor
        
        # Additional MBT55 enhancement (humus formation)
        if self.use_mbt55:
            humus_enhancement = co2e_sequestered * 0.35  # +35% from humus
            co2e_sequestered += humus_enhancement
        
        return {
            'source': 'Soil Carbon Sequestration',
            'soc_increase_tC': round(soc_increase, 0),
            'co2e_sequestered_t': round(co2e_sequestered, 0),
            'per_hectare_rate_t': round(co2e_sequestered / area_ha, 2) if area_ha > 0 else 0,
            'enhanced_by_mbt55': enhancement
        }
    
    # =========================================================
    # Source 3: Fertilizer Reduction
    # =========================================================
    
    def calculate_fertilizer_reduction(self,
                                      compost_produced_tons: float,
                                      conventional_fertilizer_kg_per_ha: float = 200.0,
                                      area_ha: float = None) -> Dict:
        """
        Calculate GHG reduction from reduced fertilizer use
        
        Formula: CO₂_saved = fertilizer_replaced × production_factor
        
        Args:
            compost_produced_tons: Amount of compost produced (tons)
            conventional_fertilizer_kg_per_ha: Baseline fertilizer use
            area_ha: Area where compost is applied
            
        Returns:
            Fertilizer reduction in tCO₂e
        """
        # Compost replaces 5% of its weight in synthetic fertilizer
        fertilizer_replaced_kg = compost_produced_tons * 1000 * self.params.fertilizer_replacement_rate
        
        # CO₂ from fertilizer production
        co2_saved = fertilizer_replaced_kg * self.params.fertilizer_production_co2 / 1000
        
        return {
            'source': 'Fertilizer Reduction',
            'fertilizer_replaced_kg': round(fertilizer_replaced_kg, 0),
            'co2_saved_t': round(co2_saved, 2),
            'reduction_rate': self.params.fertilizer_replacement_rate
        }
    
    # =========================================================
    # Source 4: Livestock Methane Reduction
    # =========================================================
    
    def calculate_livestock_methane_reduction(self,
                                             cattle_head: float = 0,
                                             sheep_head: float = 0,
                                             goat_head: float = 0) -> Dict:
        """
        Calculate methane reduction from livestock (MBT55 feed additive)
        
        Formula: CH₄_reduced = Σ(livestock × emission_factor × reduction_rate) × GWP
        
        Args:
            cattle_head: Number of cattle
            sheep_head: Number of sheep
            goat_head: Number of goats
            
        Returns:
            Livestock methane reduction in tCO₂e
        """
        # Baseline emissions
        cattle_emission = cattle_head * self.params.cattle_methane_factor
        sheep_emission = sheep_head * self.params.sheep_methane_factor
        goat_emission = goat_head * self.params.goat_methane_factor
        total_ch4 = cattle_emission + sheep_emission + goat_emission
        
        if self.use_mbt55:
            reduction = total_ch4 * self.params.mbt_livestock_reduction
        else:
            reduction = 0
        
        co2e_reduction = reduction * self.params.gwp_ch4 / 1000
        
        return {
            'source': 'Livestock Methane Reduction',
            'baseline_ch4_kg': round(total_ch4, 0),
            'reduction_ch4_kg': round(reduction, 0),
            'reduction_rate': self.params.mbt_livestock_reduction if self.use_mbt55 else 0,
            'co2e_reduction_t': round(co2e_reduction, 2)
        }
    
    # =========================================================
    # Source 5: Food Loss Reduction
    # =========================================================
    
    def calculate_food_loss_reduction(self,
                                     food_loss_tons: float) -> Dict:
        """
        Calculate GHG reduction from reduced food loss
        
        Formula: CO₂_saved = food_loss_reduced × emission_factor
        
        Args:
            food_loss_tons: Annual food loss in tons
            
        Returns:
            Food loss reduction in tCO₂e
        """
        if self.use_mbt55:
            reduction_rate = self.params.mbt_food_loss_reduction
        else:
            reduction_rate = 0
        
        food_loss_reduced = food_loss_tons * reduction_rate
        co2e_saved = food_loss_reduced * self.params.food_loss_emission_factor
        
        return {
            'source': 'Food Loss Reduction',
            'food_loss_reduced_t': round(food_loss_reduced, 0),
            'reduction_rate': reduction_rate,
            'co2e_saved_t': round(co2e_saved, 2)
        }
    
    # =========================================================
    # Source 6: Biomass Carbon Accumulation
    # =========================================================
    
    def calculate_biomass_carbon_accumulation(self,
                                             area_ha: float,
                                             biomass_t_per_ha: float = 50.0) -> Dict:
        """
        Calculate carbon accumulation in increased biomass
        
        Formula: C_accumulated = area × biomass_increase × carbon_factor × conversion
        
        Args:
            area_ha: Area in hectares
            biomass_t_per_ha: Baseline biomass (t/ha)
            
        Returns:
            Biomass carbon accumulation in tCO₂e
        """
        if self.use_mbt55:
            increase_rate = self.params.biomass_increase_rate
        else:
            increase_rate = 0
        
        biomass_increase = area_ha * biomass_t_per_ha * increase_rate
        carbon_accumulated = biomass_increase * self.params.biomass_carbon_factor
        co2e_accumulated = carbon_accumulated * self.params.soc_conversion_factor
        
        return {
            'source': 'Biomass Carbon Accumulation',
            'biomass_increase_t': round(biomass_increase, 0),
            'carbon_accumulated_t': round(carbon_accumulated, 0),
            'co2e_accumulated_t': round(co2e_accumulated, 2),
            'increase_rate': increase_rate
        }
    
    # =========================================================
    # Source 7: Transportation Reduction
    # =========================================================
    
    def calculate_transportation_reduction(self,
                                          waste_volume_tons: float) -> Dict:
        """
        Calculate GHG reduction from reduced transportation
        
        Formula: CO₂_saved = waste_volume × distance_reduction × emission_factor
        
        Args:
            waste_volume_tons: Annual waste volume in tons
            
        Returns:
            Transportation reduction in tCO₂e
        """
        if self.use_mbt55:
            distance_reduction = self.params.transport_distance_reduction
        else:
            distance_reduction = 0
        
        # Reduced ton-kilometers
        reduced_tkm = waste_volume_tons * self.params.avg_transport_distance * distance_reduction
        co2e_saved = reduced_tkm * self.params.transport_emission_factor / 1000
        
        return {
            'source': 'Transportation Reduction',
            'reduced_ton_km': round(reduced_tkm, 0),
            'reduction_rate': distance_reduction,
            'co2e_saved_t': round(co2e_saved, 2)
        }
    
    # =========================================================
    # Source 8: Fossil Fuel Replacement (Biogas)
    # =========================================================
    
    def calculate_biogas_replacement(self,
                                    waste_volume_tons: float) -> Dict:
        """
        Calculate GHG reduction from biogas replacing fossil fuels
        
        Formula: CO₂_saved = waste_volume × biogas_yield × emission_offset
        
        Args:
            waste_volume_tons: Annual waste volume in tons
            
        Returns:
            Biogas replacement in tCO₂e
        """
        if self.use_mbt55:
            biogas_volume = waste_volume_tons * self.params.biogas_yield * 100  # m³
            energy_kwh = biogas_volume * 5.5  # 5.5 kWh/m³ biogas
            co2e_saved = energy_kwh * self.params.biogas_emission_offset / 1000
        else:
            biogas_volume = 0
            co2e_saved = 0
        
        return {
            'source': 'Fossil Fuel Replacement (Biogas)',
            'biogas_volume_m3': round(biogas_volume, 0),
            'energy_generated_kwh': round(energy_kwh if self.use_mbt55 else 0, 0),
            'co2e_saved_t': round(co2e_saved, 2),
            'replacement_rate': self.params.biogas_yield if self.use_mbt55 else 0
        }
    
    # =========================================================
    # Source 9: N₂O Reduction
    # =========================================================
    
    def calculate_n2o_reduction(self,
                               fertilizer_replaced_kg: float) -> Dict:
        """
        Calculate N₂O reduction from improved nitrogen cycling
        
        Formula: N₂O_reduced = fertilizer_replaced × n_content × emission_factor × reduction_rate × GWP
        
        Args:
            fertilizer_replaced_kg: Amount of synthetic fertilizer replaced (kg)
            
        Returns:
            N₂O reduction in tCO₂e
        """
        # Nitrogen content in replaced fertilizer
        n_content = fertilizer_replaced_kg * self.params.fertilizer_n_content
        
        # Baseline N₂O emission
        baseline_n2o = n_content * self.params.n2o_emission_factor
        
        if self.use_mbt55:
            reduction_rate = self.params.mbt_n2o_reduction
            n2o_reduced = baseline_n2o * reduction_rate
        else:
            reduction_rate = 0
            n2o_reduced = 0
        
        co2e_reduced = n2o_reduced * self.params.gwp_n2o / 1000
        
        return {
            'source': 'N₂O Reduction',
            'n_content_kg': round(n_content, 0),
            'baseline_n2o_kg': round(baseline_n2o, 2),
            'reduction_rate': reduction_rate,
            'co2e_reduced_t': round(co2e_reduced, 2)
        }
    
    # =========================================================
    # Total GHG Reduction
    # =========================================================
    
    def calculate_total_ghg_reduction(self,
                                     waste_volume_tons: float,
                                     area_ha: float,
                                     cattle_head: float = 0,
                                     sheep_head: float = 0,
                                     goat_head: float = 0,
                                     years: int = 10) -> Dict:
        """
        Calculate total GHG reduction from all 9 sources
        
        Args:
            waste_volume_tons: Annual waste volume in tons
            area_ha: Area for soil carbon and biomass (ha)
            cattle_head: Number of cattle
            sheep_head: Number of sheep
            goat_head: Number of goats
            years: Project duration in years
            
        Returns:
            Complete GHG reduction breakdown
        """
        # Calculate each source
        source1 = self.calculate_waste_methane_avoidance(waste_volume_tons)
        source2 = self.calculate_soil_carbon_sequestration(area_ha, years)
        
        # Compost produced (assume 40% of waste volume)
        compost_produced = waste_volume_tons * 0.4
        source3 = self.calculate_fertilizer_reduction(compost_produced)
        source4 = self.calculate_livestock_methane_reduction(cattle_head, sheep_head, goat_head)
        source5 = self.calculate_food_loss_reduction(waste_volume_tons * 0.5)  # 50% food waste
        source6 = self.calculate_biomass_carbon_accumulation(area_ha)
        source7 = self.calculate_transportation_reduction(waste_volume_tons)
        source8 = self.calculate_biogas_replacement(waste_volume_tons)
        
        # Use fertilizer replaced from source3 for N₂O calculation
        fertilizer_replaced = source3.get('fertilizer_replaced_kg', 0)
        source9 = self.calculate_n2o_reduction(fertilizer_replaced)
        
        # Collect all sources
        sources = [source1, source2, source3, source4, source5, source6, source7, source8, source9]
        
        # Calculate total reduction
        total_reduction = sum(s.get('co2e_saved_t', s.get('co2e_sequestered_t', 
                                 s.get('co2e_reduction_t', s.get('co2e_accumulated_t', 0)))) 
                            for s in sources)
        
        # Africa 510Mt target comparison
        if self.region_scale == "africa":
            target_mt = 510
            achievement_pct = (total_reduction / 1e6) / target_mt * 100 if total_reduction > 0 else 0
        else:
            achievement_pct = 0
        
        return {
            'sources': sources,
            'total_reduction_tco2e': round(total_reduction, 0),
            'total_reduction_mtco2e': round(total_reduction / 1e6, 2),
            'number_of_sources_calculated': len(sources),
            'mbt55_enhanced': self.use_mbt55,
            'region_scale': self.region_scale,
            'africa_510mt_target_achievement_pct': round(achievement_pct, 1) if self.region_scale == "africa" else None
        }
    
    # =========================================================
    # Africa Scale Simulation (510 Mt Target)
    # =========================================================
    
    def calculate_africa_scale_reduction(self, adoption_rate: float = 0.10) -> Dict:
        """
        Calculate Africa-wide GHG reduction at scale
        
        Based on the 510 Mt CO₂e reduction target simulation
        
        Args:
            adoption_rate: Fraction of Africa's population/land adopting MBT55
            
        Returns:
            Africa-scale GHG reduction projection
        """
        if self.region_scale != "africa":
            self.region_scale = "africa"
        
        data = self.africa_data
        
        # Calculate waste volume (kg/person/day)
        urban_waste = data.total_population * data.urban_population_ratio * 0.4 * 365 / 1000
        rural_waste = data.total_population * data.rural_population_ratio * 0.2 * 365 / 1000
        total_waste = (urban_waste + rural_waste) * adoption_rate * 1000  # tons
        
        # Calculate area for soil carbon
        area_adopted = data.agricultural_land_ha * adoption_rate
        
        # Calculate livestock
        cattle_adopted = data.cattle_population * adoption_rate
        sheep_adopted = data.sheep_population * adoption_rate
        goat_adopted = data.goat_population * adoption_rate
        
        # Calculate total reduction
        result = self.calculate_total_ghg_reduction(
            waste_volume_tons=total_waste,
            area_ha=area_adopted,
            cattle_head=cattle_adopted,
            sheep_head=sheep_adopted,
            goat_head=goat_adopted,
            years=10
        )
        
        # Add scaling information
        result['adoption_rate'] = adoption_rate
        result['adopted_area_ha'] = round(area_adopted / 1e6, 2)
        result['waste_processed_tons'] = round(total_waste / 1e6, 2)
        
        return result


# =========================================================
# Example Usage
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MBT55 GHG Reduction Calculator")
    print("9-Source Reduction Model")
    print("=" * 60)
    
    # Initialize calculator
    calc = GHGReductionCalculator(use_mbt55=True, region_scale="local")
    
    # Example: 1000 tons waste, 100 ha farmland
    print("\n1. Local Scale Reduction (1000 tons waste, 100 ha):")
    result = calc.calculate_total_ghg_reduction(
        waste_volume_tons=1000,
        area_ha=100,
        cattle_head=500,
        sheep_head=1000,
        goat_head=500,
        years=10
    )
    
    print(f"\n   Total Reduction: {result['total_reduction_tco2e']:,} tCO₂e")
    print(f"   MBT55 Enhanced: {result['mbt55_enhanced']}")
    
    print("\n   Breakdown by Source:")
    for source in result['sources']:
        co2e = source.get('co2e_saved_t', source.get('co2e_sequestered_t', 
                         source.get('co2e_reduction_t', source.get('co2e_accumulated_t', 0))))
        if co2e > 0:
            print(f"     - {source['source']}: {co2e:,.0f} tCO₂e")
    
    # Africa scale simulation
    print("\n2. Africa Scale Reduction (10% adoption rate):")
    africa_calc = GHGReductionCalculator(use_mbt55=True, region_scale="africa")
    africa_result = africa_calc.calculate_africa_scale_reduction(adoption_rate=0.10)
    
    print(f"\n   Total Reduction: {africa_result['total_reduction_mtco2e']} MtCO₂e")
    print(f"   Adopted Area: {africa_result['adopted_area_ha']} million ha")
    print(f"   Waste Processed: {africa_result['waste_processed_tons']} million tons")
    
    if africa_result['africa_510mt_target_achievement_pct']:
        print(f"   510 Mt Target Achievement: {africa_result['africa_510mt_target_achievement_pct']}%")
    
    print("\n" + "=" * 60)
    print("GHG Reduction Calculation Complete")
    print("=" * 60)
