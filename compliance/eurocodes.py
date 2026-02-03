"""
harmonic-balance/compliance/eurocodes.py
Italy NTC 2018 and Eurocode compliance for 3D printed earth structures.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import math


class SeismicZone(Enum):
    """Italian seismic classification zones (NTC 2018)."""
    ZONE_1 = 1  # High seismicity (PGA >= 0.25g)
    ZONE_2 = 2  # Medium seismicity (0.15g <= PGA < 0.25g)
    ZONE_3 = 3  # Low seismicity (0.05g <= PGA < 0.15g)
    ZONE_4 = 4  # Very low seismicity (PGA < 0.05g)


class SiteClass(Enum):
    """Soil/site classification per NTC 2018."""
    A = "A"  # Hard rock
    B = "B"  # Medium rock
    C = "C"  # Medium-dense soil
    D = "D"  # Soft soil
    E = "E"  # Very soft soil


@dataclass
class NTC2018Compliance:
    """Italy NTC 2018 (Norme Tecniche per le Costruzioni) compliance data."""
    seismic_zone: SeismicZone
    site_class: SiteClass
    importance_class: int = 2  # Residential buildings
    structural_class: str = "A"
    
    def seismic_action(self, reference_pga: float = 0.15) -> float:
        """Calculate design seismic acceleration."""
        zone_multipliers = {
            SeismicZone.ZONE_1: 1.67,
            SeismicZone.ZONE_2: 1.0,
            SeismicZone.ZONE_3: 0.5,
            SeismicZone.ZONE_4: 0.25
        }
        return reference_pga * zone_multipliers[self.seismic_zone]
    
    def behavior_factor(self, structural_type: str = "unreinforced_masonry") -> float:
        """Structural behavior factor q for seismic design."""
        q_values = {
            "unreinforced_masonry": 1.5,
            "reinforced_masonry": 2.0,
            "confined_masonry": 2.5,
            "rammed_earth": 1.5,
            "3d_printed_earth": 1.8
        }
        return q_values.get(structural_type, 1.5)


@dataclass
class Eurocode6Checks:
    """Eurocode 6: Design of masonry structures (applies to 3D printed earth)."""
    material_category: str = "earth_blocks"
    
    def compressive_strength_check(self, applied_stress: float, 
                                   characteristic_strength: float = 2.5) -> bool:
        """Verify compressive strength per EC6 Eq. 2.14."""
        gamma_m = 2.5  # Partial factor for masonry
        design_strength = characteristic_strength / gamma_m
        safety_factor = 1.5
        return applied_stress <= design_strength / safety_factor
    
    def slenderness_check(self, wall_height: float, wall_thickness: float,
                         effective_length: float) -> Tuple[bool, float]:
        """Check wall slenderness per EC6 Section 5.5."""
        # Effective thickness for double-leaf or honeycomb walls
        t_ef = wall_thickness * 0.7 if self.material_category == "honeycomb_earth" else wall_thickness
        
        # Slenderness ratio
        lambda_h = wall_height / t_ef
        lambda_l = effective_length / t_ef
        lambda_max = max(lambda_h, lambda_l)
        
        # EC6 limit for unreinforced walls (typically 27)
        limit = 27.0
        return lambda_max <= limit, lambda_max
    
    def minimum_wall_thickness(self, wall_height: float, 
                               seismic_zone: SeismicZone) -> float:
        """Calculate minimum wall thickness per EC6/NTC."""
        base_thickness = 0.30  # 300mm minimum for printed earth
        
        # Seismic adjustments
        if seismic_zone == SeismicZone.ZONE_1:
            base_thickness = 0.40
        elif seismic_zone == SeismicZone.ZONE_2:
            base_thickness = 0.35
        
        # Height-based adjustments
        if wall_height > 3.0:
            base_thickness = max(base_thickness, wall_height / 10)
        
        return base_thickness


@dataclass
class Eurocode1Loads:
    """Eurocode 1: Actions on structures for 3D printed earth walls."""
    
    def self_weight_earth_wall(self, thickness: float, height: float, 
                               length: float, density: float = 1800) -> float:
        """Calculate self-weight of earth wall (kN/m² surface)."""
        volume = thickness * height * length
        weight_kn = volume * density * 9.81 / 1000
        return weight_kn / (height * length)  # kN/m²
    
    def wind_load(self, basic_wind_speed: float = 25.0,  # m/s for Italy
                  terrain_category: int = 2,
                  height_above_ground: float = 5.0) -> float:
        """Calculate wind pressure per EC1-1-4."""
        # Simplified for 3D printed earth structures
        qb = 0.5 * 1.225 * (basic_wind_speed ** 2) / 1000  # kN/m²
        
        # Roughness factor (simplified)
        cr = 0.85 if terrain_category == 2 else 0.75
        
        # Exposure factor
        ce = cr ** 2 * (height_above_ground / 10) ** 0.2
        
        return qb * ce  # kN/m²
    
    def snow_load(self, altitude: float = 500, zone: str = "II") -> float:
        """Calculate snow load per EC1-1-3 (Italian zones)."""
        # Zone-based characteristic snow load at 0m
        sk_0 = {"I": 1.5, "II": 1.0, "III": 0.6}.get(zone, 1.0)
        
        # Altitude adjustment
        if altitude <= 200:
            sk = sk_0
        else:
            sk = sk_0 + (altitude - 200) * 0.0035
        
        return sk  # kN/m²


@dataclass
class NZEBCompliance:
    """Nearly Zero Energy Building (nZEB) standards per EU Directive 2010/31/EU."""
    climate_zone: str = "D"  # Italy central/north
    building_type: str = "residential"
    
    def energy_performance_index(self, delivered_energy: float, 
                                  floor_area: float) -> float:
        """Calculate EPh (kWh/m²/year)."""
        return delivered_energy / floor_area if floor_area > 0 else float('inf')
    
    def compliance_check(self, eph: float) -> Tuple[bool, str]:
        """Check against Italy nZEB limits."""
        # Italy nZEB limits (varies by climate zone)
        limits = {
            "A": 35, "B": 40, "C": 45, "D": 50, "E": 55, "F": 60
        }
        limit = limits.get(self.climate_zone, 50)
        
        if eph <= limit:
            return True, f"EPh={eph:.1f} ≤ {limit} kWh/m²/y - COMPLIANT"
        return False, f"EPh={eph:.1f} > {limit} kWh/m²/y - NON-COMPLIANT"
    
    def thermal_transmittance_wall(self, thickness: float, 
                                    lambda_earth: float = 0.8) -> float:
        """Calculate U-value for earth wall (W/m²K)."""
        r_si = 0.13  # Internal surface resistance
        r_se = 0.04  # External surface resistance
        r_wall = thickness / lambda_earth
        u_value = 1 / (r_si + r_wall + r_se)
        return u_value


class ComplianceValidator:
    """Main validator for Harmonic Habitats compliance."""
    
    # Specific dimensions from concept images
    TYPOLOGY_SPECS = {
        'single_dwelling': {
            'area_sqm': [48, 55],  # 48-55m²
            'volume_cubic_m': [8.5, 9.5],  # 8.5-9.5m³ RMDC
            'diameter': 6.5,
            'wall_thickness_min_mm': 300
        },
        'dual_dwelling': {
            'area_sqm': 44.5,  # Corrected from typo "44-5m²"
            'volume_cubic_m': None,
            'wall_thickness_min_mm': 300
        },
        'organic_family': {
            'length': 15.0,
            'width': 5.6,
            'footprint': 84.0,
            'levels': 2,
            'wall_thickness_min_mm': 350
        }
    }
    
    def __init__(self, seismic_zone: SeismicZone = SeismicZone.ZONE_3,
                 site_class: SiteClass = SiteClass.C):
        self.ntc = NTC2018Compliance(seismic_zone=seismic_zone, site_class=site_class)
        self.ec6 = Eurocode6Checks()
        self.ec1 = Eurocode1Loads()
        self.nzeb = NZEBCompliance()
    
    def validate_typology(self, typology: str, dimensions: Dict) -> Dict:
        """Validate specific typology against specs."""
        spec = self.TYPOLOGY_SPECS.get(typology, {})
        results = {'typology': typology, 'checks': []}
        
        if 'area_sqm' in spec and 'area_sqm' in dimensions:
            area = dimensions['area_sqm']
            if isinstance(spec['area_sqm'], list):
                min_a, max_a = spec['area_sqm']
                valid = min_a <= area <= max_a
                results['checks'].append({
                    'check': 'area_sqm',
                    'value': area,
                    'required': f"{min_a}-{max_a}",
                    'valid': valid
                })
            else:
                valid = area == spec['area_sqm']
                results['checks'].append({
                    'check': 'area_sqm',
                    'value': area,
                    'required': spec['area_sqm'],
                    'valid': valid
                })
        
        if 'volume_cubic_m' in spec and 'volume_cubic_m' in dimensions:
            vol = dimensions['volume_cubic_m']
            vol_spec = spec['volume_cubic_m']
            if isinstance(vol_spec, list):
                valid = vol_spec[0] <= vol <= vol_spec[1]
                results['checks'].append({
                    'check': 'volume_cubic_m',
                    'value': vol,
                    'required': f"{vol_spec[0]}-{vol_spec[1]}",
                    'valid': valid
                })
        
        if 'wall_thickness_min_mm' in dimensions:
            thickness = dimensions['wall_thickness_min_mm']
            min_req = spec.get('wall_thickness_min_mm', 300)
            valid = thickness >= min_req
            results['checks'].append({
                'check': 'wall_thickness',
                'value': thickness,
                'required': f">= {min_req}mm",
                'valid': valid
            })
        
        results['overall_valid'] = all(c['valid'] for c in results['checks'])
        return results
    
    def full_compliance_report(self, building_specs: Dict) -> Dict:
        """Generate complete compliance report."""
        return {
            'ntc2018': {
                'seismic_zone': self.ntc.seismic_zone.name,
                'design_acceleration_g': round(self.ntc.seismic_action(), 3),
                'behavior_factor': self.ntc.behavior_factor('3d_printed_earth')
            },
            'eurocode6': {
                'wall_thickness_check': 'pending_geometry',
                'slenderness_check': 'pending_geometry'
            },
            'eurocode1': {
                'loads_calculated': 'pending_dimensions'
            },
            'nzeb': {
                'climate_zone': self.nzeb.climate_zone,
                'target_eph': {'A': 35, 'B': 40, 'C': 45, 'D': 50}.get(self.nzeb.climate_zone, 50)
            }
        }


# Convenience functions
def validate_single_dwelling(area_sqm: float, volume_cubic_m: float) -> Dict:
    """Validate single pod dwelling (48-55m², 8.5-9.5m³)."""
    validator = ComplianceValidator()
    return validator.validate_typology('single_dwelling', {
        'area_sqm': area_sqm,
        'volume_cubic_m': volume_cubic_m,
        'wall_thickness_min_mm': 300
    })


def validate_dual_dwelling(area_sqm: float) -> Dict:
    """Validate dual dwelling (44.5m² corrected)."""
    validator = ComplianceValidator()
    return validator.validate_typology('dual_dwelling', {
        'area_sqm': area_sqm,
        'wall_thickness_min_mm': 300
    })


if __name__ == "__main__":
    # Test validation
    validator = ComplianceValidator(seismic_zone=SeismicZone.ZONE_2)
    
    print("=== Single Dwelling Validation ===")
    result = validate_single_dwelling(area_sqm=52, volume_cubic_m=9.0)
    print(f"Valid: {result['overall_valid']}")
    for check in result['checks']:
        print(f"  {check['check']}: {check['value']} (required: {check['required']}) -> {check['valid']}")
    
    print("\n=== Compliance Report ===")
    report = validator.full_compliance_report({})
    print(f"Seismic zone: {report['ntc2018']['seismic_zone']}")
    print(f"Design acceleration: {report['ntc2018']['design_acceleration_g']}g")
    print(f"NZEB target EPh: {report['nzeb']['target_eph']} kWh/m²/y")
