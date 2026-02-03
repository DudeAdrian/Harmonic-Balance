"""
harmonic-balance/docs_engine/structural_calc.py
Structural engineering calculations for 3D printed earth structures.
Eurocode 1 loads, wall stability, foundation sizing.
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class LoadCase:
    """Load case definition per Eurocode."""
    name: str
    dead_load_kn_m2: float
    live_load_kn_m2: float
    wind_pressure_kn_m2: float = 0.0
    snow_load_kn_m2: float = 0.0
    seismic_coefficient: float = 0.0


@dataclass
class WallSection:
    """Wall section properties."""
    height_m: float
    length_m: float
    thickness_m: float
    material_density_kg_m3: float
    compressive_strength_mpa: float


@dataclass
class FoundationDesign:
    """Foundation design parameters."""
    width_m: float
    depth_m: float
    bearing_capacity_kpa: float
    settlement_mm: float
    safety_factor: float


class StructuralCalculator:
    """
    Structural engineering calculator for 3D printed earth buildings.
    Based on Eurocode 1 (Actions) and Eurocode 6 (Masonry).
    """
    
    # Safety factors per Eurocode
    GAMMA_G = 1.35  # Dead load
    GAMMA_Q = 1.5   # Live load
    GAMMA_M = 2.5   # Material (earth)
    
    # Material properties
    EARTH_DENSITY = 1800  # kg/m³
    EARTH_COMPRESSIVE_STRENGTH = 3.5  # MPa (typical for printed earth)
    SOIL_BEARING_CAPACITY = 150  # kPa (medium soil)
    
    def __init__(self, project_name: str, location: str = "Italy"):
        self.project_name = project_name
        self.location = location
        self.calculations = []
        
    def calculate_wall_loads(self, wall: WallSection, 
                             load_case: LoadCase) -> Dict:
        """
        Calculate loads on wall section.
        
        Returns axial load, moment, and stress.
        """
        # Wall self-weight (dead load)
        wall_volume = wall.height_m * wall.length_m * wall.thickness_m
        wall_weight_kn = wall_volume * self.EARTH_DENSITY * 9.81 / 1000
        wall_pressure_kn_m2 = wall_weight_kn / (wall.length_m * wall.thickness_m)
        
        # Applied loads
        roof_load_kn = load_case.dead_load_kn_m2 * wall.length_m * 0.5  # Half span
        floor_load_kn = load_case.live_load_kn_m2 * wall.length_m * 0.5
        
        # Total vertical load at base
        total_vertical_kn = wall_weight_kn + roof_load_kn + floor_load_kn
        
        # Wind load (horizontal)
        wind_force_kn = load_case.wind_pressure_kn_m2 * wall.height_m * wall.length_m
        wind_moment_knm = wind_force_kn * wall.height_m / 2
        
        # Design loads (factored)
        design_vertical_kn = self.GAMMA_G * wall_weight_kn + self.GAMMA_Q * (roof_load_kn + floor_load_kn)
        design_moment_knm = self.GAMMA_Q * wind_moment_knm
        
        # Stress calculations
        area_m2 = wall.length_m * wall.thickness_m
        section_modulus_m3 = wall.length_m * wall.thickness_m**2 / 6
        
        axial_stress_kpa = design_vertical_kn / area_m2 * 1000
        bending_stress_kpa = design_moment_knm / section_modulus_m3 * 1000
        
        total_stress_kpa = axial_stress_kpa + bending_stress_kpa
        allowable_stress_kpa = wall.compressive_strength_mpa * 1000 / self.GAMMA_M
        
        utilization = total_stress_kpa / allowable_stress_kpa
        
        calc = {
            'element': 'Wall Load Analysis',
            'wall_dimensions': {
                'height': wall.height_m,
                'length': wall.length_m,
                'thickness': wall.thickness_m
            },
            'loads': {
                'self_weight_kn': round(wall_weight_kn, 2),
                'roof_load_kn': round(roof_load_kn, 2),
                'floor_load_kn': round(floor_load_kn, 2),
                'wind_force_kn': round(wind_force_kn, 2),
                'wind_moment_knm': round(wind_moment_knm, 2)
            },
            'design_loads': {
                'vertical_kn': round(design_vertical_kn, 2),
                'moment_knm': round(design_moment_knm, 2)
            },
            'stresses': {
                'axial_kpa': round(axial_stress_kpa, 2),
                'bending_kpa': round(bending_stress_kpa, 2),
                'total_kpa': round(total_stress_kpa, 2),
                'allowable_kpa': round(allowable_stress_kpa, 2)
            },
            'utilization': round(utilization, 3),
            'status': 'PASS' if utilization <= 1.0 else 'FAIL'
        }
        
        self.calculations.append(calc)
        return calc
    
    def check_wall_stability(self, wall: WallSection) -> Dict:
        """
        Check wall stability per Eurocode 6.
        
        Checks:
        - Slenderness ratio
        - Buckling
        - Overturning
        """
        # Slenderness ratio (height/thickness)
        slenderness = wall.height_m / wall.thickness_m
        
        # EC6 limit for unreinforced walls
        slenderness_limit = 27.0
        
        # Buckling check
        effective_height = wall.height_m * 0.75  # End restraints
        radius_of_gyration = wall.thickness_m / math.sqrt(12)
        
        # Elastic critical buckling load
        E_earth = 500  # MPa (modulus of elasticity for earth)
        I = wall.length_m * wall.thickness_m**3 / 12
        
        critical_buckling_kn = (math.pi**2 * E_earth * 1000 * I) / (effective_height**2)
        
        # Overturning check
        wall_weight_kn = (wall.height_m * wall.length_m * wall.thickness_m * 
                         self.EARTH_DENSITY * 9.81 / 1000)
        
        # Assume wind acts at mid-height
        wind_moment_knm = 0.5 * wall.height_m * wall.height_m * wall.length_m * 0.5
        resisting_moment_knm = wall_weight_kn * wall.thickness_m / 2
        
        overturning_factor = resisting_moment_knm / wind_moment_knm if wind_moment_knm > 0 else 999
        
        calc = {
            'element': 'Wall Stability Check',
            'slenderness': {
                'ratio': round(slenderness, 2),
                'limit': slenderness_limit,
                'status': 'PASS' if slenderness <= slenderness_limit else 'FAIL'
            },
            'buckling': {
                'critical_load_kn': round(critical_buckling_kn, 2),
                'status': 'PASS' if critical_buckling_kn > wall_weight_kn else 'FAIL'
            },
            'overturning': {
                'resisting_moment_knm': round(resisting_moment_knm, 2),
                'overturning_moment_knm': round(wind_moment_knm, 2),
                'safety_factor': round(overturning_factor, 2),
                'status': 'PASS' if overturning_factor >= 1.5 else 'FAIL'
            }
        }
        
        self.calculations.append(calc)
        return calc
    
    def design_foundation(self, total_load_kn: float, 
                         soil_bearing_kpa: float = None) -> FoundationDesign:
        """
        Design strip foundation for earth wall.
        
        Args:
            total_load_kn: Total vertical load from walls
            soil_bearing_kpa: Allowable soil bearing capacity
        
        Returns:
            FoundationDesign with dimensions
        """
        if soil_bearing_kpa is None:
            soil_bearing_kpa = self.SOIL_BEARING_CAPACITY
        
        # Required foundation area
        required_area_m2 = total_load_kn * self.GAMMA_G / (soil_bearing_kpa)
        
        # Assume strip foundation under wall
        wall_thickness = 0.3  # m
        foundation_width = max(wall_thickness * 2, required_area_m2 / 1.0)
        
        # Foundation depth (frost protection + bearing)
        foundation_depth = 0.8  # m typical
        
        # Settlement estimate (simplified)
        # Elastic settlement = (q * B * (1 - v²)) / E
        # Assuming medium stiff soil
        settlement_mm = 5.0  # Conservative estimate
        
        # Safety factor against bearing failure
        actual_pressure_kpa = total_load_kn / foundation_width
        safety_factor = soil_bearing_kpa / actual_pressure_kpa
        
        foundation = FoundationDesign(
            width_m=round(foundation_width, 2),
            depth_m=foundation_depth,
            bearing_capacity_kpa=soil_bearing_kpa,
            settlement_mm=settlement_mm,
            safety_factor=round(safety_factor, 2)
        )
        
        calc = {
            'element': 'Foundation Design',
            'loads': {
                'total_vertical_kn': round(total_load_kn, 2)
            },
            'foundation': {
                'type': 'Strip foundation',
                'width_m': foundation.width_m,
                'depth_m': foundation.depth_m,
                'length_m': 'Per wall length'
            },
            'soil': {
                'bearing_capacity_kpa': soil_bearing_kpa,
                'actual_pressure_kpa': round(actual_pressure_kpa, 2),
                'safety_factor': foundation.safety_factor,
                'status': 'PASS' if foundation.safety_factor >= 2.0 else 'REVIEW'
            },
            'settlement': {
                'estimated_mm': foundation.settlement_mm,
                'status': 'PASS' if foundation.settlement_mm <= 25 else 'REVIEW'
            }
        }
        
        self.calculations.append(calc)
        return foundation
    
    def calculate_seismic_loads(self, building_mass_kg: float,
                               seismic_zone: str = "Zone 3") -> Dict:
        """
        Calculate seismic loads per NTC 2018 (Italy).
        
        Args:
            building_mass_kg: Total building mass
            seismic_zone: Italian seismic classification (Zone 1-4)
        """
        # Seismic coefficients (simplified from NTC 2018)
        zone_coefficients = {
            "Zone 1": 0.35,  # High seismicity
            "Zone 2": 0.25,  # Medium seismicity
            "Zone 3": 0.15,  # Low seismicity
            "Zone 4": 0.05   # Very low
        }
        
        ag = zone_coefficients.get(seismic_zone, 0.15)
        
        # Behavior factor for unreinforced earth
        q = 1.5
        
        # Design ground acceleration
        ad = ag / q
        
        # Seismic force (simplified equivalent static analysis)
        seismic_force_kn = building_mass_kg * ad * 9.81 / 1000
        
        calc = {
            'element': 'Seismic Analysis (NTC 2018)',
            'site': {
                'seismic_zone': seismic_zone,
                'ground_acceleration_ag': ag
            },
            'building': {
                'total_mass_kg': building_mass_kg,
                'behavior_factor_q': q
            },
            'design': {
                'design_acceleration_ad': round(ad, 3),
                'seismic_force_kn': round(seismic_force_kn, 2)
            },
            'checks': {
                'note': 'Simplified equivalent static analysis',
                'recommendation': 'Detailed seismic analysis required for Zone 1-2'
            }
        }
        
        self.calculations.append(calc)
        return calc
    
    def generate_report(self, output_path: Path) -> Path:
        """Generate structural calculation report."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = []
        report.append("=" * 70)
        report.append("STRUCTURAL CALCULATION REPORT")
        report.append("=" * 70)
        report.append(f"Project: {self.project_name}")
        report.append(f"Location: {self.location}")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        report.append(f"Standard: Eurocode 1 (Actions), Eurocode 6 (Masonry)")
        report.append("=" * 70)
        report.append("")
        
        report.append("MATERIAL PROPERTIES")
        report.append("-" * 70)
        report.append(f"Material: 3D Printed Earth")
        report.append(f"Density: {self.EARTH_DENSITY} kg/m³")
        report.append(f"Compressive strength: {self.EARTH_COMPRESSIVE_STRENGTH} MPa")
        report.append(f"Safety factor (γM): {self.GAMMA_M}")
        report.append("")
        
        report.append("SAFETY FACTORS (Eurocode)")
        report.append("-" * 70)
        report.append(f"Dead load (γG): {self.GAMMA_G}")
        report.append(f"Live load (γQ): {self.GAMMA_Q}")
        report.append("")
        
        for i, calc in enumerate(self.calculations, 1):
            report.append(f"CALCULATION {i}: {calc['element']}")
            report.append("-" * 70)
            self._format_calculation(calc, report, 0)
            report.append("")
        
        report.append("=" * 70)
        report.append("END OF REPORT")
        report.append("=" * 70)
        report.append("")
        report.append("Notes:")
        report.append("- This report is for preliminary design purposes.")
        report.append("- Detailed engineering review required prior to construction.")
        report.append("- Site-specific geotechnical investigation recommended.")
        
        report_text = "\n".join(report)
        
        with open(output_path, 'w') as f:
            f.write(report_text)
        
        return output_path
    
    def _format_calculation(self, calc: Dict, report: List[str], indent: int):
        """Recursively format calculation results."""
        prefix = "  " * indent
        
        for key, value in calc.items():
            if key == 'element':
                continue
            
            if isinstance(value, dict):
                report.append(f"{prefix}{key.replace('_', ' ').title()}:")
                self._format_calculation(value, report, indent + 1)
            else:
                formatted_key = key.replace('_', ' ').title()
                report.append(f"{prefix}{formatted_key}: {value}")


def calculate_single_pod_structure(diameter_m: float = 6.5,
                                   height_m: float = 3.2,
                                   wall_thickness_m: float = 0.30) -> Path:
    """
    Complete structural calculation for SinglePod.
    
    Returns path to calculation report.
    """
    calc = StructuralCalculator("Single Pod Dwelling", "Italy")
    
    # Define wall
    wall = WallSection(
        height_m=height_m,
        length_m=math.pi * diameter_m,  # Circumference
        thickness_m=wall_thickness_m,
        material_density_kg_m3=1800,
        compressive_strength_mpa=3.5
    )
    
    # Load case (typical residential)
    load_case = LoadCase(
        name="Ultimate Limit State",
        dead_load_kn_m2=2.0,  # Roof
        live_load_kn_m2=2.0,  # Floor
        wind_pressure_kn_m2=0.5,  # Wind
        snow_load_kn_m2=1.5
    )
    
    # Calculate
    calc.calculate_wall_loads(wall, load_case)
    calc.check_wall_stability(wall)
    
    # Foundation
    total_load_kn = (math.pi * diameter_m * height_m * wall_thickness_m * 
                    1800 * 9.81 / 1000)
    calc.design_foundation(total_load_kn)
    
    # Seismic
    building_mass = math.pi * (diameter_m/2)**2 * height_m * 1800
    calc.calculate_seismic_loads(building_mass, "Zone 3")
    
    # Generate report
    output_dir = Path(__file__).parent / 'outputs'
    return calc.generate_report(output_dir / 'structural_report.txt')


if __name__ == "__main__":
    print("Structural Calculation Test")
    report_path = calculate_single_pod_structure()
    print(f"Report generated: {report_path}")
