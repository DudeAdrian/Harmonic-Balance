"""
harmonic-balance/genesis/typologies.py
Parametric typologies for Harmonic Habitats.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from genesis.geometry import HexagonalTessellation, ResonantCavity, MALTA_RATIOS
from compliance.eurocodes import ComplianceValidator, SeismicZone, SiteClass


@dataclass
class SinglePod:
    """
    Circular pod for 1-2 sleepers.
    - 6-7m diameter
    - Central service core (Type A)
    - Radial layout
    - Honeycomb wall texture
    - 48-55m² area
    """
    diameter: float = 6.5
    wall_thickness: float = 0.30
    height: float = 3.2
    core_diameter: float = 1.2
    
    def __post_init__(self):
        self.radius = self.diameter / 2
        self.area = math.pi * self.radius ** 2
        self.volume = self.area * self.height
        self.core_type = "A"  # Service core designation
        
    def generate(self, compliance_check: bool = True) -> Dict:
        """Generate geometry and compliance report."""
        # Generate circular geometry
        segments = 24
        points = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            points.append((x, y))
        
        # Radial zones from central core
        zones = self._generate_radial_zones()
        
        geometry = {
            'type': 'SinglePod',
            'diameter': self.diameter,
            'radius': self.radius,
            'height': self.height,
            'area_sqm': round(self.area, 2),
            'volume_cubic_m': round(self.volume, 2),
            'wall_thickness_mm': int(self.wall_thickness * 1000),
            'core': {
                'type': self.core_type,
                'diameter': self.core_diameter,
                'position': (0, 0),
                'functions': ['services', 'storage', 'services_riser']
            },
            'perimeter_points': points,
            'radial_zones': zones,
            'layout_type': 'radial',
            'wall_texture': 'honeycomb_high',
            'sleepers': [1, 2]
        }
        
        # Compliance report
        compliance_report = None
        if compliance_check:
            validator = ComplianceValidator()
            compliance_report = validator.validate_typology('single_dwelling', {
                'area_sqm': self.area,
                'volume_cubic_m': self.volume,
                'wall_thickness_min_mm': self.wall_thickness * 1000
            })
        
        return {
            'geometry': geometry,
            'compliance': compliance_report,
            'gcode_preview': self._generate_gcode_preview()
        }
    
    def _generate_radial_zones(self) -> List[Dict]:
        """Generate radial layout zones."""
        zones = []
        # Zone A: Central core (service)
        zones.append({
            'zone': 'A',
            'type': 'service_core',
            'radius': self.core_diameter / 2,
            'area_sqm': round(math.pi * (self.core_diameter/2)**2, 2)
        })
        # Zone B: Living/sleeping ring
        zones.append({
            'zone': 'B',
            'type': 'living_space',
            'inner_radius': self.core_diameter / 2,
            'outer_radius': self.radius * 0.6,
            'area_sqm': round(self.area * 0.5, 2)
        })
        # Zone C: Perimeter buffer
        zones.append({
            'zone': 'C',
            'type': 'perimeter_zone',
            'inner_radius': self.radius * 0.6,
            'outer_radius': self.radius,
            'area_sqm': round(self.area * 0.35, 2)
        })
        return zones
    
    def _generate_gcode_preview(self) -> str:
        """Generate WASP G-code preview."""
        gcode = [
            "; SinglePod WASP G-code",
            f"; Diameter: {self.diameter}m",
            f"; Height: {self.height}m",
            "G28 ; Home"
        ]
        # Circular perimeter print path
        segments = 24
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            gcode.append(f"G1 X{x:.3f} Y{y:.3f} Z0.000 F1500")
        gcode.append("G28")
        return "\n".join(gcode)


@dataclass
class MultiPodCluster:
    """
    4-pod village arrangement.
    - 4 individual pods
    - Circular site plan
    - Shared central gathering space
    - 6 total sleepers
    """
    pod_count: int = 4
    pod_diameter: float = 6.0
    arrangement_radius: float = 12.0
    pod_height: float = 3.0
    central_space_diameter: float = 8.0
    
    def __post_init__(self):
        self.total_sleepers = 6
        self.pod_angle_step = 2 * math.pi / self.pod_count
        self.site_area = math.pi * self.arrangement_radius ** 2
        
    def generate(self, compliance_check: bool = True) -> Dict:
        """Generate cluster geometry and compliance report."""
        pods = []
        for i in range(self.pod_count):
            angle = i * self.pod_angle_step
            x = self.arrangement_radius * math.cos(angle)
            y = self.arrangement_radius * math.sin(angle)
            pods.append({
                'id': f'pod_{i+1}',
                'center': (round(x, 2), round(y, 2)),
                'diameter': self.pod_diameter,
                'height': self.pod_height,
                'sleepers': [1, 2] if i < 2 else [1],
                'angle_deg': round(math.degrees(angle), 1)
            })
        
        geometry = {
            'type': 'MultiPodCluster',
            'pod_count': self.pod_count,
            'arrangement': 'circular',
            'arrangement_radius': self.arrangement_radius,
            'total_sleepers': self.total_sleepers,
            'site_area_sqm': round(self.site_area, 2),
            'central_space': {
                'diameter': self.central_space_diameter,
                'type': 'shared_gathering',
                'area_sqm': round(math.pi * (self.central_space_diameter/2)**2, 2)
            },
            'pods': pods,
            'connections': self._generate_connecting_paths()
        }
        
        # Compliance report
        compliance_report = None
        if compliance_check:
            validator = ComplianceValidator()
            compliance_report = {
                'typology': 'multi_sleeper_cluster',
                'total_units': self.pod_count,
                'total_sleepers': self.total_sleepers,
                'site_compliance': 'pending_land_use_check',
                'individual_pods': validator.validate_typology('single_dwelling', {
                    'area_sqm': math.pi * (self.pod_diameter/2)**2,
                    'volume_cubic_m': math.pi * (self.pod_diameter/2)**2 * self.pod_height,
                    'wall_thickness_min_mm': 300
                })
            }
        
        return {
            'geometry': geometry,
            'compliance': compliance_report,
            'site_plan_gcode': self._generate_site_gcode()
        }
    
    def _generate_connecting_paths(self) -> List[Dict]:
        """Generate connecting paths between pods."""
        paths = []
        for i in range(self.pod_count):
            angle = i * self.pod_angle_step
            next_angle = ((i + 1) % self.pod_count) * self.pod_angle_step
            
            # Path from pod to center
            x1 = self.arrangement_radius * math.cos(angle)
            y1 = self.arrangement_radius * math.sin(angle)
            x2 = 0
            y2 = 0
            
            paths.append({
                'id': f'path_to_center_{i+1}',
                'from': f'pod_{i+1}',
                'to': 'central_space',
                'length': self.arrangement_radius - self.central_space_diameter/2,
                'width': 1.5
            })
        return paths
    
    def _generate_site_gcode(self) -> str:
        """Generate site-wide G-code for WASP."""
        gcode = [
            "; MultiPodCluster Site G-code",
            f"; Pods: {self.pod_count}",
            f"; Arrangement radius: {self.arrangement_radius}m",
            "G28"
        ]
        
        # Print central gathering space base
        gcode.append(f"; Central gathering space")
        segments = 16
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            r = self.central_space_diameter / 2
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            gcode.append(f"G1 X{x:.3f} Y{y:.3f} Z0.000")
        
        return "\n".join(gcode)


@dataclass
class OrganicFamily:
    """
    Large flowing dwelling for extended family.
    - 15m x 5.6m footprint
    - Multi-level (2 levels)
    - Spiral stairs
    - 4 bedrooms
    - Central gathering space
    """
    length: float = 15.0
    width: float = 5.6
    height_per_level: float = 2.8
    levels: int = 2
    bedrooms: int = 4
    
    def __post_init__(self):
        self.footprint_area = self.length * self.width
        self.total_height = self.height_per_level * self.levels
        self.total_volume = self.footprint_area * self.total_height
        
    def generate(self, compliance_check: bool = True) -> Dict:
        """Generate flowing form geometry and compliance report."""
        # Generate flowing organic shape
        levels_data = []
        for level in range(self.levels):
            z = level * self.height_per_level
            
            # Organic flowing shape - varying width along length
            level_shape = self._generate_level_geometry(level)
            levels_data.append({
                'level': level + 1,
                'z_base': z,
                'height': self.height_per_level,
                'shape': level_shape
            })
        
        geometry = {
            'type': 'OrganicFamily',
            'length': self.length,
            'width': self.width,
            'footprint_sqm': round(self.footprint_area, 2),
            'levels': self.levels,
            'total_height': self.total_height,
            'volume_cubic_m': round(self.total_volume, 2),
            'bedrooms': self.bedrooms,
            'features': {
                'stairs': 'spiral',
                'central_gathering': True,
                'flowing_walls': True,
                'organic_form': True
            },
            'levels': levels_data,
            'room_allocation': self._allocate_rooms()
        }
        
        # Compliance report
        compliance_report = None
        if compliance_check:
            validator = ComplianceValidator()
            compliance_report = validator.validate_typology('organic_family', {
                'length': self.length,
                'width': self.width,
                'footprint': self.footprint_area,
                'levels': self.levels,
                'wall_thickness_min_mm': 350
            })
        
        return {
            'geometry': geometry,
            'compliance': compliance_report,
            'construction_sequence': self._generate_construction_sequence()
        }
    
    def _generate_level_geometry(self, level: int) -> Dict:
        """Generate geometry for a single level."""
        # Flowing organic shape with varying width
        segments = 20
        width_variation = 0.2  # 20% width variation
        
        points = []
        for i in range(segments + 1):
            t = i / segments
            x = t * self.length - self.length / 2
            
            # Sinusoidal width variation for organic feel
            width_factor = 1 + width_variation * math.sin(2 * math.pi * t + level)
            y = self.width / 2 * width_factor
            
            points.append((round(x, 2), round(y, 2)))
        
        return {
            'perimeter_points': points,
            'area_sqm': round(self.footprint_area * (1 + width_variation/2), 2)
        }
    
    def _allocate_rooms(self) -> List[Dict]:
        """Allocate rooms across levels."""
        rooms = []
        
        # Level 1: Common areas + 1 bedroom
        rooms.append({
            'level': 1,
            'rooms': [
                {'name': 'central_gathering', 'type': 'common', 'area_sqm': 25},
                {'name': 'kitchen_dining', 'type': 'common', 'area_sqm': 18},
                {'name': 'bedroom_1', 'type': 'sleeping', 'area_sqm': 12},
                {'name': 'bathroom_1', 'type': 'service', 'area_sqm': 6}
            ]
        })
        
        # Level 2: Bedrooms + study
        rooms.append({
            'level': 2,
            'rooms': [
                {'name': 'bedroom_2', 'type': 'sleeping', 'area_sqm': 14},
                {'name': 'bedroom_3', 'type': 'sleeping', 'area_sqm': 12},
                {'name': 'bedroom_4', 'type': 'sleeping', 'area_sqm': 12},
                {'name': 'study', 'type': 'common', 'area_sqm': 10},
                {'name': 'bathroom_2', 'type': 'service', 'area_sqm': 6}
            ]
        })
        
        return rooms
    
    def _generate_construction_sequence(self) -> List[Dict]:
        """Generate construction sequence for WASP printing."""
        sequence = [
            {'phase': 1, 'action': 'site_preparation', 'duration_days': 2},
            {'phase': 2, 'action': 'print_level_1_walls', 'duration_days': 5, 'layers': int(self.height_per_level / 0.05)},
            {'phase': 3, 'action': 'install_level_1_floor', 'duration_days': 2},
            {'phase': 4, 'action': 'print_level_2_walls', 'duration_days': 5, 'layers': int(self.height_per_level / 0.05)},
            {'phase': 5, 'action': 'install_roof', 'duration_days': 3},
            {'phase': 6, 'action': 'finishing', 'duration_days': 5}
        ]
        return sequence


def generate_typology(typology_name: str, **kwargs) -> Dict:
    """Factory function to generate any typology."""
    typologies = {
        'single_pod': SinglePod,
        'multi_pod_cluster': MultiPodCluster,
        'organic_family': OrganicFamily
    }
    
    typology_class = typologies.get(typology_name)
    if not typology_class:
        raise ValueError(f"Unknown typology: {typology_name}. Available: {list(typologies.keys())}")
    
    instance = typology_class(**kwargs)
    return instance.generate()


if __name__ == "__main__":
    print("=== SinglePod ===")
    single = SinglePod(diameter=6.5)
    result = single.generate()
    print(f"Area: {result['geometry']['area_sqm']}m²")
    print(f"Volume: {result['geometry']['volume_cubic_m']}m³")
    print(f"Compliance valid: {result['compliance']['overall_valid']}")
    
    print("\n=== MultiPodCluster ===")
    cluster = MultiPodCluster(pod_count=4)
    result = cluster.generate()
    print(f"Site area: {result['geometry']['site_area_sqm']}m²")
    print(f"Total sleepers: {result['geometry']['total_sleepers']}")
    print(f"Pods: {len(result['geometry']['pods'])}")
    
    print("\n=== OrganicFamily ===")
    family = OrganicFamily()
    result = family.generate()
    print(f"Footprint: {result['geometry']['footprint_sqm']}m²")
    print(f"Levels: {result['geometry']['levels']}")
    print(f"Bedrooms: {result['geometry']['bedrooms']}")
    print(f"Features: {result['geometry']['features']}")
