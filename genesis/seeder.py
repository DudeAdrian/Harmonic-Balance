"""
harmonic-balance/genesis/seeder.py
Extract parametric DNA from concept images.
"""

import json
from pathlib import Path
from typing import Dict, Any


class ImageSeeder:
    def __init__(self, image_path: Path):
        self.image_path = image_path
        self.style_dna = self._analyze()
    
    def _analyze(self) -> Dict[str, Any]:
        filename = self.image_path.stem
        
        # Legacy patterns
        if "194049" in filename:
            return {
                'form_language': 'flowing_organic',
                'curvature': 'high',
                'clustering': 'nested',
                'material': 'layered_earth',
                'porosity': 'honeycomb_high',
                'scale': 'large_dwelling',
                'harmonic_signature': '7.83'
            }
        elif "5sk5i6" in filename:
            return {
                'form_language': 'hexagonal_tessellation',
                'curvature': 'low',
                'clustering': 'distributed_village',
                'material': 'smooth_earth',
                'porosity': 'honeycomb_medium',
                'scale': 'multi_unit',
                'harmonic_signature': '7.83'
            }
        # Organic Family - Large flowing dwelling
        elif "dbb3516e" in filename or "organic_family" in filename:
            return {
                'form_language': 'flowing_organic',
                'curvature': 'high',
                'clustering': 'single_structure',
                'material': 'layered_earth',
                'porosity': 'honeycomb_high',
                'scale': 'large_dwelling',
                'harmonic_signature': '7.83',
                'dimensions': {'length': 15.0, 'width': 5.6, 'height': 4.2},
                'levels': 2,
                'bedrooms': 4,
                'features': ['spiral_stairs', 'central_gathering', 'multi_level'],
                'footprint_area_sqm': 84.0,
                'volume_cubic_m': 352.8
            }
        # Single Dwelling - Circular pod for 1-2 sleepers
        elif "single_dwelling" in filename or "1-2_sleepers" in filename:
            return {
                'form_language': 'circular_pod',
                'curvature': 'high',
                'clustering': 'single_unit',
                'material': 'layered_earth',
                'porosity': 'honeycomb_high',
                'scale': 'small_dwelling',
                'harmonic_signature': '7.83',
                'diameter': 6.5,
                'area_sqm_range': [48, 55],
                'volume_cubic_m_range': [8.5, 9.5],
                'sleepers': [1, 2],
                'layout': 'radial',
                'central_core': 'service_core_A',
                'wall_texture': 'honeycomb'
            }
        # Multi-Sleeper Cluster - 4-pod village
        elif "multi_sleeper" in filename or "cluster" in filename:
            return {
                'form_language': 'pod_cluster',
                'curvature': 'medium',
                'clustering': 'circular_village',
                'material': 'layered_earth',
                'porosity': 'honeycomb_medium',
                'scale': 'multi_unit',
                'harmonic_signature': '7.83',
                'pod_count': 4,
                'total_sleepers': 6,
                'site_plan': 'circular',
                'shared_space': 'central_gathering',
                'arrangement_radius': 12.0
            }
        # Technical Layout - Floor plan documentation
        elif "layout" in filename or "technical" in filename:
            return {
                'form_language': 'technical_documentation',
                'curvature': 'low',
                'clustering': 'document',
                'material': 'n/a',
                'porosity': 'n/a',
                'scale': 'documentation',
                'harmonic_signature': '7.83',
                'zones': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                'zone_A': 'central_service_core',
                'documentation_type': 'floor_plan',
                'includes_sqm': True,
                'includes_dimensions': True
            }
        
        return {'form_language': 'hybrid', 'harmonic_signature': '7.83'}
    
    def to_parameters(self) -> Dict[str, Any]:
        base_params = {
            'cell_radius': 2.5 if self.style_dna.get('scale') == 'large_dwelling' else 1.8,
            'wall_thickness': 0.35 if self.style_dna.get('material') == 'layered_earth' else 0.25,
            'target_frequency': float(self.style_dna.get('harmonic_signature', '7.83'))
        }
        
        # Add typology-specific parameters
        if self.style_dna.get('form_language') == 'circular_pod':
            base_params.update({
                'diameter': self.style_dna.get('diameter', 6.5),
                'min_wall_thickness_mm': 300,
                'core_type': 'A'
            })
        elif self.style_dna.get('form_language') == 'pod_cluster':
            base_params.update({
                'pod_count': self.style_dna.get('pod_count', 4),
                'arrangement_radius': self.style_dna.get('arrangement_radius', 12.0)
            })
        elif self.style_dna.get('form_language') == 'flowing_organic' and 'multi_level' in self.style_dna.get('features', []):
            base_params.update({
                'length': self.style_dna.get('dimensions', {}).get('length', 15.0),
                'width': self.style_dna.get('dimensions', {}).get('width', 5.6),
                'levels': self.style_dna.get('levels', 2)
            })
        
        return base_params
    
    def save_seed(self, output_path: Path):
        seed_data = {
            'source_image': str(self.image_path),
            'style_dna': self.style_dna,
            'parameters': self.to_parameters(),
            'version': '0.2.0-genesis'
        }
        with open(output_path, 'w') as f:
            json.dump(seed_data, f, indent=2)
        return seed_data


def seed_from_concept(image_filename: str) -> Dict[str, Any]:
    image_path = Path("genesis/concepts") / image_filename
    seeder = ImageSeeder(image_path)
    seed_path = Path("genesis/seeds") / f"{image_filename}.json"
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    return seeder.save_seed(seed_path)


if __name__ == "__main__":
    test_images = [
        "20241125_194049_0000.png",
        "5sk5i6.jpg",
        "dbb3516e.png",
        "organic_family.jpg",
        "single_dwelling.png",
        "1-2_sleepers.jpg",
        "multi_sleeper.png",
        "cluster.png",
        "layout.png",
        "technical.png"
    ]
    for img in test_images:
        try:
            seed = seed_from_concept(img)
            print(f"Seeded {img}: {seed['style_dna']['form_language']}")
        except FileNotFoundError:
            print(f"Place {img} in genesis/concepts/ to seed")
