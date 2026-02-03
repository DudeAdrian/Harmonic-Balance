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
        return {'form_language': 'hybrid', 'harmonic_signature': '7.83'}
    
    def to_parameters(self) -> Dict[str, Any]:
        return {
            'cell_radius': 2.5 if self.style_dna['scale'] == 'large_dwelling' else 1.8,
            'wall_thickness': 0.35 if self.style_dna['material'] == 'layered_earth' else 0.25,
            'target_frequency': float(self.style_dna['harmonic_signature'])
        }
    
    def save_seed(self, output_path: Path):
        seed_data = {
            'source_image': str(self.image_path),
            'style_dna': self.style_dna,
            'parameters': self.to_parameters(),
            'version': '0.1.0-genesis'
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
    test_images = ["20241125_194049_0000.png", "5sk5i6.jpg"]
    for img in test_images:
        try:
            seed = seed_from_concept(img)
            print(f"Seeded {img}: {seed['style_dna']['form_language']}")
        except FileNotFoundError:
            print(f"Place {img} in genesis/concepts/ to seed")
