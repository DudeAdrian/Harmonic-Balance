"""
harmonic-balance/printer/materials.py
Earth printing material specifications and mix design.
Compatible with WASP Crane and other large-format earth printers.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class MaterialGrade(Enum):
    """Material performance grades."""
    STANDARD = "standard"
    HIGH_STRENGTH = "high_strength"
    THERMAL = "thermal_optimized"
    RESONANCE = "resonance_enhanced"


@dataclass
class EarthMix:
    """
    Generic earth printing mix specification.
    Calibrated for WASP Crane - adjust for other printers.
    """
    name: str
    clay_percent: float
    sand_percent: float
    silt_percent: float
    water_percent: float
    additives: Dict[str, float]
    
    # Performance specifications
    compression_mpa: Tuple[float, float]
    thermal_conductivity: Tuple[float, float]  # W/mK
    shrinkage_percent: float
    
    # Printing parameters
    optimal_moisture: float  # %
    extrusion_pressure_bar: Tuple[float, float]
    cure_time_days: int
    
    @classmethod
    def standard_mix(cls) -> 'EarthMix':
        """
        Standard earth printing mix.
        Generic formulation suitable for most printers.
        """
        return cls(
            name="Standard Earth Mix",
            clay_percent=30.0,
            sand_percent=50.0,
            silt_percent=20.0,
            water_percent=8.0,
            additives={
                'natural_fibers': 2.0,  # % (straw, hemp)
                'lime': 5.0,  # % for stabilization
            },
            compression_mpa=(2.0, 5.0),
            thermal_conductivity=(0.8, 1.2),
            shrinkage_percent=2.5,
            optimal_moisture=12.0,
            extrusion_pressure_bar=(2.0, 4.0),
            cure_time_days=28
        )
    
    @classmethod
    def high_strength_mix(cls) -> 'EarthMix':
        """Higher strength mix for structural elements."""
        return cls(
            name="High Strength Earth Mix",
            clay_percent=25.0,
            sand_percent=55.0,
            silt_percent=20.0,
            water_percent=7.5,
            additives={
                'cement': 8.0,
                'natural_fibers': 1.5,
            },
            compression_mpa=(5.0, 10.0),
            thermal_conductivity=(1.0, 1.5),
            shrinkage_percent=2.0,
            optimal_moisture=11.0,
            extrusion_pressure_bar=(3.0, 5.0),
            cure_time_days=28
        )
    
    @classmethod
    def thermal_optimized_mix(cls) -> 'EarthMix':
        """Thermally optimized mix for insulation."""
        return cls(
            name="Thermal Optimized Earth Mix",
            clay_percent=35.0,
            sand_percent=35.0,
            silt_percent=30.0,
            water_percent=9.0,
            additives={
                'straw': 8.0,
                'pumice': 10.0,
            },
            compression_mpa=(1.5, 3.0),
            thermal_conductivity=(0.4, 0.7),
            shrinkage_percent=3.0,
            optimal_moisture=14.0,
            extrusion_pressure_bar=(1.5, 3.0),
            cure_time_days=42
        )
    
    @classmethod
    def resonance_enhanced_mix(cls, target_frequency: float = 7.83) -> 'EarthMix':
        """
        Resonance-enhanced mix with quartz additive.
        For frequency-tuned structures (Schumann resonance alignment).
        """
        return cls(
            name=f"Resonance Enhanced Mix ({target_frequency}Hz)",
            clay_percent=28.0,
            sand_percent=47.0,
            silt_percent=20.0,
            water_percent=8.0,
            additives={
                'quartz_powder': 5.0,  # Enhances piezoelectric properties
                'natural_fibers': 2.0,
                'lime': 3.0,
            },
            compression_mpa=(2.5, 5.5),
            thermal_conductivity=(0.9, 1.3),
            shrinkage_percent=2.3,
            optimal_moisture=11.5,
            extrusion_pressure_bar=(2.5, 4.5),
            cure_time_days=35
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'composition': {
                'clay': f"{self.clay_percent}%",
                'sand': f"{self.sand_percent}%",
                'silt': f"{self.silt_percent}%",
                'water': f"{self.water_percent}%",
            },
            'additives': self.additives,
            'performance': {
                'compression_mpa': f"{self.compression_mpa[0]}-{self.compression_mpa[1]} MPa",
                'thermal_conductivity': f"{self.thermal_conductivity[0]}-{self.thermal_conductivity[1]} W/mK",
                'shrinkage': f"{self.shrinkage_percent}%",
            },
            'printing': {
                'optimal_moisture': f"{self.optimal_moisture}%",
                'extrusion_pressure': f"{self.extrusion_pressure_bar[0]}-{self.extrusion_pressure_bar[1]} bar",
                'cure_time': f"{self.cure_time_days} days",
            }
        }
    
    def get_mixing_instructions(self, volume_cubic_m: float) -> Dict:
        """Calculate material quantities for given volume."""
        # Density of compacted earth mix ~1800 kg/m³
        density = 1800  # kg/m³
        total_weight_kg = volume_cubic_m * density
        
        return {
            'total_volume_m3': volume_cubic_m,
            'total_weight_kg': round(total_weight_kg, 0),
            'clay_kg': round(total_weight_kg * self.clay_percent / 100, 0),
            'sand_kg': round(total_weight_kg * self.sand_percent / 100, 0),
            'silt_kg': round(total_weight_kg * self.silt_percent / 100, 0),
            'water_liters': round(total_weight_kg * self.water_percent / 100, 0),
            'additives_kg': {
                name: round(total_weight_kg * percent / 100, 1)
                for name, percent in self.additives.items()
            }
        }


class MaterialDatabase:
    """Database of available material mixes."""
    
    MIXES = {
        'standard': EarthMix.standard_mix(),
        'high_strength': EarthMix.high_strength_mix(),
        'thermal': EarthMix.thermal_optimized_mix(),
        'resonance': EarthMix.resonance_enhanced_mix(),
    }
    
    @classmethod
    def get_mix(cls, name: str) -> Optional[EarthMix]:
        """Get mix by name."""
        return cls.MIXES.get(name.lower())
    
    @classmethod
    def list_mixes(cls) -> List[str]:
        """List available mix names."""
        return list(cls.MIXES.keys())
    
    @classmethod
    def recommend_mix(cls, priority: str = 'balanced') -> EarthMix:
        """
        Recommend mix based on priority.
        
        Args:
            priority: 'balanced', 'strength', 'thermal', 'resonance'
        """
        recommendations = {
            'balanced': 'standard',
            'strength': 'high_strength',
            'structural': 'high_strength',
            'thermal': 'thermal',
            'insulation': 'thermal',
            'resonance': 'resonance',
            'acoustic': 'resonance',
            'schumann': 'resonance',
        }
        mix_name = recommendations.get(priority.lower(), 'standard')
        return cls.MIXES[mix_name]


class QualityControl:
    """Quality control procedures for earth printing."""
    
    @staticmethod
    def moisture_test(target_percent: float) -> Dict:
        """Moisture content test procedure."""
        return {
            'test': 'Moisture Content',
            'target': f"{target_percent}%",
            'method': 'Oven drying at 105°C for 24 hours',
            'frequency': 'Every batch',
            'tolerance': '±1.5%'
        }
    
    @staticmethod
    def compression_test_sample(cure_days: int = 28) -> Dict:
        """Compression test procedure for sample cubes."""
        return {
            'test': 'Compression Strength',
            'sample_size': '150mm cubes',
            'cure_time': f"{cure_days} days",
            'method': 'ASTM C109 or EN 196-1",
            'frequency': '1 per 10m³ or daily',
            'expected_range': '2-10 MPa (mix dependent)'
        }
    
    @staticmethod
    def extrusion_consistency() -> Dict:
        """Extrusion consistency check."""
        return {
            'test': 'Extrusion Consistency',
            'method': 'Visual flow rate check',
            'criteria': 'Continuous flow, no gaps or surges',
            'frequency': 'Every 30 minutes during printing',
            'adjustment': 'Add water if too dry, add binder if too wet'
        }


def generate_material_report(typology: str, volume_m3: float, 
                             mix_type: str = 'standard') -> str:
    """Generate complete material specification report."""
    mix = MaterialDatabase.get_mix(mix_type) or EarthMix.standard_mix()
    quantities = mix.get_mixing_instructions(volume_m3)
    
    report = [
        "=" * 60,
        "EARTH PRINTING MATERIAL SPECIFICATION",
        "=" * 60,
        "",
        f"Project: {typology}",
        f"Mix Type: {mix.name}",
        f"Volume: {volume_m3:.2f} m³",
        "",
        "COMPOSITION",
        "-" * 40,
        f"  Clay:    {mix.clay_percent}% ({quantities['clay_kg']} kg)",
        f"  Sand:    {mix.sand_percent}% ({quantities['sand_kg']} kg)",
        f"  Silt:    {mix.silt_percent}% ({quantities['silt_kg']} kg)",
        f"  Water:   {mix.water_percent}% ({quantities['water_liters']} L)",
        "",
        "ADDITIVES",
        "-" * 40,
    ]
    
    for additive, kg in quantities['additives_kg'].items():
        report.append(f"  {additive.replace('_', ' ').title()}: {kg} kg")
    
    report.extend([
        "",
        "PERFORMANCE SPECIFICATIONS",
        "-" * 40,
        f"  Compression: {mix.compression_mpa[0]}-{mix.compression_mpa[1]} MPa",
        f"  Thermal: {mix.thermal_conductivity[0]}-{mix.thermal_conductivity[1]} W/mK",
        f"  Shrinkage: {mix.shrinkage_percent}%",
        "",
        "PRINTING PARAMETERS",
        "-" * 40,
        f"  Optimal moisture: {mix.optimal_moisture}%",
        f"  Extrusion pressure: {mix.extrusion_pressure_bar[0]}-{mix.extrusion_pressure_bar[1]} bar",
        f"  Cure time: {mix.cure_time_days} days",
        "",
        "NOTES",
        "-" * 40,
        "  - Calibrated for WASP Crane - adjust for other printers",
        "  - Source local materials within 50km when possible",
        "  - Test mix before full production",
        "  - Cover and protect from rain during curing",
        "",
        "=" * 60
    ])
    
    return "\n".join(report)


if __name__ == "__main__":
    print("=== Earth Printing Materials ===")
    
    # List available mixes
    print("\nAvailable mixes:")
    for mix_name in MaterialDatabase.list_mixes():
        mix = MaterialDatabase.get_mix(mix_name)
        print(f"  - {mix.name}")
    
    # Generate material report for SinglePod
    print("\n" + generate_material_report('single_pod', 52.8, 'resonance'))
    
    # Quality control procedures
    print("\n=== Quality Control Procedures ===")
    qc = QualityControl()
    print(f"Moisture test: {qc.moisture_test(12.0)['method']}")
    print(f"Compression test: {qc.compression_test_sample()['sample_size']}")
