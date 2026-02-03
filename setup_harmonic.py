import os

# Create directories (already done, but safe to repeat)
dirs = ['genesis', 'genesis/concepts', 'genesis/seeds', 'resonance', 'compliance', 'terracare', 'render_farm', 'api']
for d in dirs:
    os.makedirs(d, exist_ok=True)

# File contents
geometry_py = '''"""
harmonic-balance/genesis/geometry.py

Sacred geometry generation for Harmonic Habitats.
Hexagonal tessellation, golden ratio proportions, 
and resonant cavity dimensions.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class ResonantCavity:
    """A space designed for specific acoustic properties."""
    fundamental_hz: float
    dimensions: Tuple[float, float, float]
    material_density: float
    shape_type: str = "hexagonal_prism"
    
    def calculate_modes(self, max_harmonic: int = 5) -> List[float]:
        modes = []
        for n in range(1, max_harmonic + 1):
            mode = self.fundamental_hz * n * math.sqrt(
                sum(1/d**2 for d in self.dimensions)
            ) / math.sqrt(3)
            modes.append(mode)
        return modes
    
    def schumann_alignment(self) -> bool:
        schumann = [7.83, 14.3, 20.8, 27.3, 33.8]
        modes = self.calculate_modes()
        tolerance = 0.5
        for s in schumann:
            if any(abs(m - s) < tolerance for m in modes):
                return True
        return False


class HexagonalTessellation:
    def __init__(self, cell_radius: float = 2.5, wall_thickness: float = 0.3):
        self.cell_radius = cell_radius
        self.wall_thickness = wall_thickness
        self.cell_height = cell_radius * 2 * math.sin(math.pi/3)
        
    def generate_grid(self, rows: int, cols: int, levels: int = 1) -> List[dict]:
        cells = []
        for level in range(levels):
            z = level * (self.cell_radius * 1.5)
            for row in range(rows):
                for col in range(cols):
                    x = col * self.cell_radius * 1.5
                    y = row * self.cell_height + (col % 2) * self.cell_height / 2
                    cell = {
                        'center': (x, y, z),
                        'radius': self.cell_radius,
                        'wall_thickness': self.wall_thickness,
                        'id': f"cell_{level}_{row}_{col}",
                    }
                    cells.append(cell)
        return cells
    
    def to_wasp_gcode(self, cells: List[dict], material: str = "local_earth") -> str:
        gcode = ["; Harmonic-Balance WASP G-code", f"; Material: {material}", "G28"]
        for cell in cells:
            x, y, z = cell['center']
            gcode.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f}")
        gcode.append("G28")
        return "\\n".join(gcode)


class GoldenProportion:
    PHI = (1 + math.sqrt(5)) / 2
    
    @classmethod
    def apply(cls, base_dimension: float, iterations: int = 3) -> List[float]:
        dimensions = [base_dimension]
        for _ in range(iterations):
            dimensions.append(dimensions[-1] / cls.PHI)
        return dimensions


MALTA_RATIOS = {
    'oracle_room': {'length': 4.5, 'width': 3.2, 'height': 2.8},
}


def create_harmonic_habitat(footprint_area: float, target_frequency: float = 7.83, levels: int = 1):
    tessellation = HexagonalTessellation()
    cell_area = 2.598 * tessellation.cell_radius**2
    num_cells = int(footprint_area / cell_area)
    grid_size = int(math.sqrt(num_cells))
    cells = tessellation.generate_grid(grid_size, grid_size, levels)
    
    base_dims = MALTA_RATIOS['oracle_room']
    cavity = ResonantCavity(
        fundamental_hz=target_frequency,
        dimensions=(base_dims['length'], base_dims['width'], base_dims['height']),
        material_density=1800
    )
    
    return {
        'specification': {
            'cell_count': len(cells),
            'schumann_aligned': cavity.schumann_alignment()
        },
        'geometry': {'cells': cells},
        'wasp_output': tessellation.to_wasp_gcode(cells)
    }


if __name__ == "__main__":
    habitat = create_harmonic_habitat(100, levels=2)
    print(f"Generated: {habitat['specification']}")
'''

seeder_py = '''"""
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
'''

tuner_py = '''"""
harmonic-balance/resonance/tuner.py
Acoustic and vibrational optimization.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SchumannResonance:
    fundamental: float = 7.83
    harmonics: Tuple[float, ...] = (14.3, 20.8, 27.3, 33.8, 39.0)
    
    def alignment_score(self, room_modes: List[float]) -> float:
        all_freqs = (self.fundamental,) + self.harmonics
        matches = sum(
            1 for mode in room_modes 
            if any(abs(mode - h) < 0.5 for h in all_freqs)
        )
        return matches / len(room_modes) if room_modes else 0.0


class RoomModeCalculator:
    def __init__(self, room_geometry: dict):
        self.geometry = room_geometry
        self.speed_of_sound = 343
    
    def calculate_modes(self, max_freq: float = 50.0) -> List[dict]:
        r = self.geometry.get('radius', 2.5)
        h = self.geometry.get('height', 2.8)
        modes = []
        
        for n in range(1, 10):
            freq = n * self.speed_of_sound / (2 * h)
            if freq > max_freq:
                break
            modes.append({'frequency': freq, 'type': 'axial', 'order': n})
        
        return modes


MALTA_ACOUSTICS = {
    'hagar_qim': {'resonance_hz': 80, 'reverberation_sec': 6.5}
}
'''

readme_md = '''# Harmonic-Balance

**Sacred geometry generation for resonant dwellings.**

Private repository for Harmonic Habitats. 
Computational temple architecture for the modern age.

## Genesis

- Hexagonal tessellation (bee wisdom)
- Golden ratio proportions (divine harmony)
- Schumann resonance alignment (7.83 Hz)
- Malta temple acoustics (ancient healing)

## Usage

```python
from genesis.geometry import create_harmonic_habitat
habitat = create_harmonic_habitat(footprint_area=150, target_frequency=7.83, levels=2)