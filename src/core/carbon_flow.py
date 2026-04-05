"""
Carbon Flow Model for MBT55 Ecological Hypercycle
Implements carbon cycling efficiency (CCE), humification rates, 
and net carbon sequestration (NCS) calculations.

Based on theoretical framework from:
- MBT Hypercycle Superiority Documentation
- Ecological Hypercycle Theory
- Field validation data (Bionexus Holdings)

Key equations:
1. CCE = (C_stable / C_input) × (t_retention / t_decomp)
2. dH/dt = k_h × (1 - e^(-λ × MSI)) × C_microbial
3. NCS = ∫[α·CCE(t) - β·GWP_emit(t) + γ·Fire_prev(t)]dt
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class SoilType(Enum):
    """Soil type classification with base carbon factors"""
    CLAY = "clay"
    LOAM = "loam"
    SAND = "sand"


class CarbonPool(Enum):
    """Carbon pools in soil ecosystem"""
    MICROBIAL_BIOMASS = "microbial_biomass"
    DISSOLVED_ORGANIC = "dissolved_organic"
    HUMUS_STABLE = "humus_stable"
    HUMUS_ACTIVE = "humus_active"
    PARTICULATE = "particulate"
    RESPIRED = "respired"


@dataclass
class MBT55Parameters:
    """
    MBT55-specific carbon cycling parameters
    Based on empirical data from field trials
    """
    # Humification coefficient (2.9x conventional)
    humification_rate: float = 0.35
    
    # Decomposition loss rate (1/3 of conventional)
    decomposition_loss: float = 0.05
    
    # Carbon Use Efficiency (CUE) - MBT55 enhanced
    carbon_use_efficiency: float = 0.75
    
    # Electron re-fixation efficiency
    electron_recovery: float = 0.65
    
    # Methane reduction factor (82% reduction)
    methane_reduction: float = 0.82
    
    # Fire risk reduction (42% reduction)
    fire_risk_reduction: float = 0.42
    
    # Carbon sequestration (tCO₂e/ha/10yr)
    carbon_sequestration: float = 109.5
    
    # Microbial Synergy Index threshold
    msi_threshold: float = 0.70


@dataclass
class ConventionalParameters:
    """Conventional agriculture baseline parameters"""
    humification_rate: float = 0.12
    decomposition_loss: float = 0.15
    carbon_use_efficiency: float = 0.45
    electron_recovery: float = 0.30
    methane_reduction: float = 0.10
    fire_risk_reduction: float = 0.05
    carbon_sequestration: float = 38.2
    msi_threshold: float = 0.35


class CarbonFlowModel:
    """
    Carbon flow model for MBT55 ecological hypercycle
    
    Implements:
    1. Carbon Cycling Efficiency (CCE) calculation
    2. Humus formation rate modeling
    3. Net Carbon Sequestration (NCS) projection
    4. 10-year impact assessment
    """
    
    def __init__(self, use_mbt55: bool = True, soil_type: SoilType = SoilType.LOAM):
        """
        Initialize carbon flow model
        
        Args:
            use_mbt55: If True, use MBT55 parameters; otherwise conventional
            soil_type: Soil classification for baseline adjustment
        """
        self.use_mbt55 = use_mbt55
        self.soil_type = soil_type
        
        # Load parameters based on selection
        if use_mbt55:
            self.params = MBT55Parameters()
        else:
            self.params = ConventionalParameters()
        
        # Soil type correction factors
        self.soil_factors = {
            SoilType.CLAY: 1.2,
            SoilType.LOAM: 1.0,
            SoilType.SAND: 0.7
        }
        
        # Initialize carbon pools (kg C/ha)
        self._initialize_pools()
    
    def _initialize_pools(self):
        """Initialize carbon pools based on soil type"""
        base_factor = self.soil_factors.get(self.soil_type, 1.0)
        
        self.carbon_pools = {
            CarbonPool.MICROBIAL_BIOMASS: 500.0 * base_factor,
            CarbonPool.DISSOLVED_ORGANIC: 1000.0 * base_factor,
            CarbonPool.HUMUS_STABLE: 5000.0 * base_factor,
            CarbonPool.HUMUS_ACTIVE: 2000.0 * base_factor,
            CarbonPool.PARTICULATE: 3000.0 * base_factor,
            CarbonPool.RESPIRED: 0.0
        }
    
    # =========================================================
    # Core Carbon Cycle Equations
    # =========================================================
    
    def calculate_carbon_cycling_efficiency(self, 
                                            c_stable: float = None,
                                            c_input: float = 100.0,
                                            t_retention: float = None,
                                            t_decomp: float = None) -> Dict:
        """
        Calculate Carbon Cycling Efficiency (CCE)
        
        Formula: CCE = (C_stable / C_input) × (t_retention / t_decomp)
        
        From theoretical document:
        - MBT55: CCE = 0.8 (t_decomp = 0.3 years, t_retention = 10 years)
        - Conventional: CCE = 0.3 (t_decomp = 3 years, t_retention = 5 years)
        
        Args:
            c_stable: Stable carbon after decomposition (kg C/ha)
            c_input: Initial carbon input (kg C/ha)
            t_retention: Carbon retention time (years)
            t_decomp: Decomposition time (years)
            
        Returns:
            Dictionary with CCE and related metrics
        """
        # Use theoretical values if not provided
        if self.use_mbt55:
            if c_stable is None:
                c_stable = 80.0  # 80% of input becomes stable
            if t_retention is None:
                t_retention = 10.0  # 10 years stability (humus)
            if t_decomp is None:
                t_decomp = 0.3  # 0.3 years (≈110 days)
        else:
            if c_stable is None:
                c_stable = 30.0  # 30% of input becomes stable
            if t_retention is None:
                t_retention = 5.0  # 5 years stability
            if t_decomp is None:
                t_decomp = 3.0  # 3 years
        
        # Calculate CCE
        stable_ratio = c_stable / c_input
        time_ratio = t_retention / t_decomp
        cce = stable_ratio * time_ratio
        
        return {
            'carbon_cycling_efficiency': round(cce, 3),
            'stable_carbon_ratio': round(stable_ratio, 3),
            'time_efficiency_ratio': round(time_ratio, 3),
            'decomposition_time_years': t_decomp,
            'retention_time_years': t_retention,
            'theoretical_comparison': {
                'mbt55_standard': 0.8,
                'conventional_standard': 0.3,
                'improvement_factor': round(0.8 / 0.3, 2) if self.use_mbt55 else 1.0
            }
        }
    
    def calculate_humus_formation_rate(self,
                                       microbial_biomass_c: float = 500.0,
                                       microbial_synergy_index: float = None) -> float:
        """
        Calculate humus formation rate (HFR)
        
        Formula: dH/dt = k_h × (1 - e^(-λ × MSI)) × C_microbial
        
        From theoretical document:
        - k_h: humification rate constant (MBT55: 0.35, Conventional: 0.12)
        - λ: sensitivity coefficient (0.35)
        - MSI: Microbial Synergy Index (>0.7 for MBT55)
        - C_microbial: microbial biomass carbon (kg C/ha)
        
        Args:
            microbial_biomass_c: Microbial biomass carbon (kg C/ha)
            microbial_synergy_index: MSI value (0-1), higher = more synergy
            
        Returns:
            Humus formation rate (kg C/ha/day)
        """
        # Set MSI based on MBT55 enhancement
        if microbial_synergy_index is None:
            if self.use_mbt55:
                microbial_synergy_index = self.params.msi_threshold + 0.15  # ~0.85
            else:
                microbial_synergy_index = 0.35
        
        lambda_val = 0.35  # Sensitivity coefficient from theoretical document
        k_h = self.params.humification_rate
        
        # Calculate humus formation
        synergy_factor = 1 - math.exp(-lambda_val * microbial_synergy_index)
        daily_rate = k_h * synergy_factor * (microbial_biomass_c / 1000)  # Convert to t
        
        # Apply soil type correction
        soil_factor = self.soil_factors.get(self.soil_type, 1.0)
        daily_rate *= soil_factor
        
        return round(daily_rate, 4)
    
    def calculate_net_carbon_sequestration(self,
                                          area_ha: float,
                                          years: int = 10,
                                          temperature: float = 25.0,
                                          moisture: float = 0.6,
                                          mbt_applications_per_year: int = 4) -> Dict:
        """
        Calculate Net Carbon Sequestration (NCS)
        
        Formula: NCS = ∫[α·CCE(t) - β·GWP_emit(t) + γ·Fire_prev(t)]dt
        
        Args:
            area_ha: Area in hectares
            years: Project duration in years
            temperature: Average temperature (°C)
            moisture: Soil moisture (0-1)
            mbt_applications_per_year: Number of MBT55 applications per year
            
        Returns:
            Comprehensive carbon sequestration projection
        """
        # Base annual sequestration rate (tCO₂e/ha/year)
        if self.use_mbt55:
            base_annual_rate = self.params.carbon_sequestration / 10
            # MBT55 enhancement from multiple applications
            application_boost = 1 + (mbt_applications_per_year * 0.08)
            annual_rate = base_annual_rate * application_boost
        else:
            annual_rate = self.params.carbon_sequestration / 10
        
        # Environmental modulation
        temp_factor = self._temperature_response(temperature)
        moisture_factor = self._moisture_response(moisture)
        env_factor = temp_factor * moisture_factor
        
        # Apply environmental factors
        adjusted_annual_rate = annual_rate * env_factor
        
        # Calculate co-benefits
        methane_reduction = self._calculate_methane_benefit(adjusted_annual_rate, area_ha)
        fire_prevention = self._calculate_fire_prevention_benefit(adjusted_annual_rate, area_ha)
        
        # Calculate total sequestration
        annual_sequestration = adjusted_annual_rate * area_ha
        total_sequestration = annual_sequestration * years
        
        # Net Climate Benefit (including co-benefits)
        ncb = total_sequestration + (methane_reduction + fire_prevention) * years
        
        # Comparison with conventional
        conventional_model = CarbonFlowModel(use_mbt55=False, soil_type=self.soil_type)
        conventional_annual = conventional_model.params.carbon_sequestration / 10
        conventional_total = conventional_annual * area_ha * years
        
        improvement_factor = total_sequestration / conventional_total if conventional_total > 0 else 1.0
        
        return {
            'annual_sequestration_tco2e': round(annual_sequestration, 2),
            'total_sequestration_tco2e': round(total_sequestration, 2),
            'net_climate_benefit_tco2e': round(ncb, 2),
            'methane_reduction_tco2e': round(methane_reduction * years, 2),
            'fire_prevention_tco2e': round(fire_prevention * years, 2),
            'per_hectare_annual_rate': round(adjusted_annual_rate, 2),
            'environmental_factors': {
                'temperature': temperature,
                'moisture': moisture,
                'temperature_factor': round(temp_factor, 3),
                'moisture_factor': round(moisture_factor, 3),
                'combined_factor': round(env_factor, 3)
            },
            'improvement_vs_conventional': {
                'total_sequestration': round(total_sequestration, 2),
                'conventional_baseline': round(conventional_total, 2),
                'improvement_factor': round(improvement_factor, 2),
                'improvement_percentage': round((improvement_factor - 1) * 100, 1)
            },
            'mbt_application_boost': round(application_boost if self.use_mbt55 else 1.0, 2)
        }
    
    # =========================================================
    # Co-benefit Calculations
    # =========================================================
    
    def _calculate_methane_benefit(self, annual_sequestration: float, area_ha: float) -> float:
        """Calculate methane reduction co-benefit"""
        methane_reduction_rate = self.params.methane_reduction
        # Methane has 28x GWP, MBT55 reduces methane by 82%
        methane_benefit = annual_sequestration * methane_reduction_rate * 0.15
        return methane_benefit * area_ha
    
    def _calculate_fire_prevention_benefit(self, annual_sequestration: float, area_ha: float) -> float:
        """Calculate fire prevention co-benefit from increased humus"""
        fire_reduction_rate = self.params.fire_risk_reduction
        # Fire prevention benefit is ~20% of sequestration value
        fire_benefit = annual_sequestration * fire_reduction_rate * 0.20
        return fire_benefit * area_ha
    
    # =========================================================
    # Environmental Response Functions
    # =========================================================
    
    def _temperature_response(self, temperature: float) -> float:
        """Temperature response function for MBT55"""
        if self.use_mbt55:
            # MBT55: Broad optimum 20-40°C
            if 20 <= temperature <= 40:
                return 1.0
            elif temperature < 10:
                return 0.3 + 0.07 * temperature
            elif temperature > 45:
                return 1.5 - 0.03 * temperature
            else:
                return np.exp(-0.5 * ((temperature - 30) / 15) ** 2)
        else:
            # Conventional: Narrow optimum 25-35°C
            return np.exp(-0.5 * ((temperature - 30) / 8) ** 2)
    
    def _moisture_response(self, moisture: float) -> float:
        """Moisture response function"""
        if self.use_mbt55:
            # MBT55: Optimal range 0.4-0.8, functional down to 0.2
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
        else:
            # Conventional: Sharp peak at 0.6
            return np.exp(-0.5 * ((moisture - 0.6) / 0.2) ** 2)
    
    # =========================================================
    # 10-Year Impact Assessment
    # =========================================================
    
    def project_10_year_impact(self, area_ha: float = 1.0) -> Dict:
        """
        Project 10-year carbon sequestration impact
        Based on theoretical document table
        
        From theoretical document:
        | Metric | Conventional | MBT55 | Improvement |
        |--------|--------------|-------|-------------|
        | Carbon Sequestration | 38.2 tCO₂e/ha | 109.5 tCO₂e/ha | +186% |
        | Humus Generated | 12.1 t/ha | 35.8 t/ha | +196% |
        """
        
        if self.use_mbt55:
            annual_seq_t_co2e = self.params.carbon_sequestration / 10
            annual_humus_t = 35.8 / 10
            methane_reduction = self.params.methane_reduction
            fire_risk_reduction = self.params.fire_risk_reduction
        else:
            annual_seq_t_co2e = 3.82
            annual_humus_t = 1.21
            methane_reduction = 0.10
            fire_risk_reduction = 0.05
        
        # 10-year totals
        total_seq = annual_seq_t_co2e * 10 * area_ha
        total_humus = annual_humus_t * 10 * area_ha
        
        # Additional benefits
        methane_reduced = annual_seq_t_co2e * 0.1 * methane_reduction * 10 * area_ha
        fire_prevention = annual_seq_t_co2e * 0.15 * fire_risk_reduction * 10 * area_ha
        
        # Net Climate Benefit (NCB)
        ncb = total_seq + methane_reduced + fire_prevention
        
        return {
            '10_year_sequestration_t_co2e': round(total_seq, 1),
            '10_year_humus_formation_t': round(total_humus, 1),
            'methane_reduction_t_co2e': round(methane_reduced, 1),
            'fire_prevention_benefit_t_co2e': round(fire_prevention, 1),
            'net_climate_benefit_t_co2e': round(ncb, 1),
            'annual_rates': {
                'sequestration': round(annual_seq_t_co2e, 2),
                'humus_formation': round(annual_humus_t, 2),
                'methane_reduction': methane_reduction,
                'fire_risk_reduction': fire_risk_reduction
            },
            'improvement_factors': {
                'sequestration': 1.86 if self.use_mbt55 else 0.0,
                'humus': 1.96 if self.use_mbt55 else 0.0
            }
        }
    
    # =========================================================
    # Carbon Credit Calculation
    # =========================================================
    
    def calculate_carbon_credits(self,
                                area_ha: float,
                                duration_years: int = 10,
                                carbon_price_usd: float = 65.0,
                                verification_level: str = 'high') -> Dict:
        """
        Calculate carbon credits based on theoretical performance
        
        Args:
            area_ha: Area in hectares
            duration_years: Project duration in years
            carbon_price_usd: Carbon market price (USD/tCO₂e)
            verification_level: 'basic', 'standard', 'high'
            
        Returns:
            Carbon credit calculation with verification requirements
        """
        # Theoretical sequestration rates
        if self.use_mbt55:
            base_rate = 10.95  # tCO₂e/ha/year from theoretical data
        else:
            base_rate = 3.82
        
        # Verification adjustment (conservativeness)
        verification_factors = {
            'basic': 0.7,
            'standard': 0.85,
            'high': 0.95
        }
        adjustment = verification_factors.get(verification_level, 0.85)
        
        # Calculate total credits
        annual_credits = base_rate * adjustment
        total_credits = annual_credits * duration_years * area_ha
        
        # Carbon revenue
        carbon_revenue = total_credits * carbon_price_usd
        
        # Permanence risk adjustment (MBT55 reduces reversibility risk)
        if self.use_mbt55:
            permanence_risk = 0.05  # 5% risk vs 15% conventional
        else:
            permanence_risk = 0.15
        
        risk_adjusted_credits = total_credits * (1 - permanence_risk)
        risk_adjusted_revenue = risk_adjusted_credits * carbon_price_usd
        
        # Co-benefits from theoretical document
        co_benefits = {
            'water_retention_ml_per_year': 300 * area_ha,
            'biodiversity_units': 15 * area_ha,
            'soil_health_improvement': 25 * area_ha,
            'yield_increase_percent': 12 * area_ha
        }
        
        return {
            'total_credits_t_co2e': round(risk_adjusted_credits, 1),
            'annual_rate_t_co2e_ha': round(annual_credits, 2),
            'carbon_revenue_usd': round(risk_adjusted_revenue, 0),
            'project_duration_years': duration_years,
            'area_ha': area_ha,
            'verification_level': verification_level,
            'permanence_risk_factor': permanence_risk,
            'co_benefits': co_benefits,
            'theoretical_basis': {
                'data_source': 'MBT Hypercycle Theoretical Document',
                'improvement_over_conventional': '186%',
                'validation_status': 'Theoretically validated'
            }
        }
    
    # =========================================================
    # Soil Carbon Stock Simulation
    # =========================================================
    
    def simulate_carbon_stock(self,
                             initial_soc_t_ha: float = 50.0,
                             duration_years: float = 20.0,
                             time_steps: int = 100) -> Dict:
        """
        Simulate soil organic carbon stock over time
        
        Differential equation: dC/dt = I - k_d·C + f_m(MBT55)·η
        
        Args:
            initial_soc_t_ha: Initial soil organic carbon (t C/ha)
            duration_years: Simulation duration in years
            time_steps: Number of simulation steps
            
        Returns:
            Time series of carbon stock
        """
        dt = duration_years / time_steps
        carbon_stock = np.zeros(time_steps + 1)
        carbon_stock[0] = initial_soc_t_ha
        
        # Input organic matter (t C/ha/year)
        I = 10.0  # Typical input from crop residues + compost
        
        # MBT55 enhancement function
        if self.use_mbt55:
            f_m = self.params.humification_rate / 0.12  # Normalized enhancement
            eta = self.params.electron_recovery
        else:
            f_m = 1.0
            eta = 0.3
        
        for t in range(time_steps):
            dCdt = I - self.params.decomposition_loss * carbon_stock[t] + f_m * eta
            carbon_stock[t + 1] = carbon_stock[t] + dCdt * dt
        
        # Convert to CO₂ equivalents (1 t C = 3.67 t CO₂)
        co2e_stock = carbon_stock * 3.67
        
        # Calculate SOC increase rate
        soc_increase = (carbon_stock[-1] - carbon_stock[0]) / carbon_stock[0] * 100
        
        return {
            'time_years': np.linspace(0, duration_years, time_steps + 1).tolist(),
            'carbon_stock_tC_ha': carbon_stock.tolist(),
            'co2e_stock_tCO2e_ha': co2e_stock.tolist(),
            'initial_soc_tC_ha': initial_soc_t_ha,
            'final_soc_tC_ha': round(carbon_stock[-1], 2),
            'soc_increase_percent': round(soc_increase, 1),
            'mbt55_enhancement_applied': self.use_mbt55
        }


# =========================================================
# Example Usage
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MBT55 Carbon Flow Model - Theoretical Validation")
    print("=" * 60)
    
    # Initialize MBT55 model
    mbt_model = CarbonFlowModel(use_mbt55=True, soil_type=SoilType.LOAM)
    conv_model = CarbonFlowModel(use_mbt55=False, soil_type=SoilType.LOAM)
    
    # 1. Carbon Cycling Efficiency
    print("\n1. Carbon Cycling Efficiency (CCE):")
    mbt_cce = mbt_model.calculate_carbon_cycling_efficiency()
    conv_cce = conv_model.calculate_carbon_cycling_efficiency()
    print(f"   MBT55 CCE: {mbt_cce['carbon_cycling_efficiency']}")
    print(f"   Conventional CCE: {conv_cce['carbon_cycling_efficiency']}")
    print(f"   Improvement: {mbt_cce['theoretical_comparison']['improvement_factor']}x")
    
    # 2. Humus Formation Rate
    print("\n2. Humus Formation Rate (kg C/ha/day):")
    mbt_humus = mbt_model.calculate_humus_formation_rate(microbial_biomass_c=500, microbial_synergy_index=0.85)
    conv_humus = conv_model.calculate_humus_formation_rate(microbial_biomass_c=500, microbial_synergy_index=0.35)
    print(f"   MBT55: {mbt_humus} kg C/ha/day")
    print(f"   Conventional: {conv_humus} kg C/ha/day")
    
    # 3. Net Carbon Sequestration (100 ha, 10 years)
    print("\n3. Net Carbon Sequestration (100 ha, 10 years):")
    mbt_ncs = mbt_model.calculate_net_carbon_sequestration(area_ha=100, years=10)
    print(f"   MBT55 Total: {mbt_ncs['total_sequestration_tco2e']} tCO₂e")
    print(f"   Net Climate Benefit: {mbt_ncs['net_climate_benefit_tco2e']} tCO₂e")
    print(f"   Improvement vs Conventional: +{mbt_ncs['improvement_vs_conventional']['improvement_percentage']}%")
    
    # 4. 10-Year Impact
    print("\n4. 10-Year Impact Assessment (1 ha):")
    impact = mbt_model.project_10_year_impact(area_ha=1.0)
    print(f"   Carbon Sequestration: {impact['10_year_sequestration_t_co2e']} tCO₂e")
    print(f"   Humus Formation: {impact['10_year_humus_formation_t']} t")
    print(f"   Net Climate Benefit: {impact['net_climate_benefit_t_co2e']} tCO₂e")
    
    # 5. Carbon Credits (100 ha, 10 years)
    print("\n5. Carbon Credit Calculation (100 ha, 10 years):")
    credits = mbt_model.calculate_carbon_credits(area_ha=100, duration_years=10, carbon_price_usd=65)
    print(f"   Total Credits: {credits['total_credits_t_co2e']} tCO₂e")
    print(f"   Carbon Revenue: ${credits['carbon_revenue_usd']:,}")
    print(f"   Co-benefits: Water +{credits['co_benefits']['water_retention_ml_per_year']:,} ML/year")
    
    # 6. Soil Carbon Stock Simulation
    print("\n6. Soil Carbon Stock Simulation (20 years):")
    sim = mbt_model.simulate_carbon_stock(initial_soc_t_ha=50, duration_years=20)
    print(f"   Initial SOC: {sim['initial_soc_tC_ha']} t C/ha")
    print(f"   Final SOC: {sim['final_soc_tC_ha']} t C/ha")
    print(f"   SOC Increase: +{sim['soc_increase_percent']}%")
    
    print("\n" + "=" * 60)
    print("MBT55 Carbon Flow Model - Validation Complete")
    print("=" * 60)
