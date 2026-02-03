"""
harmonic-balance/genesis/geometry.py
Sacred geometry generation for Harmonic Habitats.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ResonantCavity:
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
        return "\n".join(gcode)


class WASPPrinter:
    """
    WASP 3D printer G-code generator for earth construction.
    Supports curved walls with G2/G3 arcs.
    """
    
    # WASP specifications for earth printing
    DEFAULT_LAYER_HEIGHT = 0.020  # 20mm
    DEFAULT_NOZZLE_DIAMETER = 0.040  # 40mm
    DEFAULT_PRINT_SPEED = 50  # 50mm/s
    DEFAULT_FLOW_RATE = 100  # %
    
    def __init__(self, layer_height: float = 0.020, 
                 nozzle_diameter: float = 0.040,
                 print_speed: float = 50):
        self.layer_height = layer_height
        self.nozzle_diameter = nozzle_diameter
        self.print_speed = print_speed
        self.flow_rate = 100
        
    def generate_header(self, material: str = "local_earth") -> List[str]:
        """Generate G-code header."""
        return [
            "; Harmonic-Balance WASP G-code",
            f"; Material: {material}",
            f"; Layer height: {self.layer_height*1000:.0f}mm",
            f"; Nozzle diameter: {self.nozzle_diameter*1000:.0f}mm",
            f"; Print speed: {self.print_speed}mm/s",
            "G28 ; Home all axes",
            "G21 ; Set units to mm",
            "G90 ; Absolute positioning",
            "M104 S0 ; Extruder temp (not used for earth)",
            "M140 S0 ; Bed temp (not used for earth)",
            f"M221 S{self.flow_rate} ; Flow rate",
            ""
        ]
    
    def generate_curved_wall_gcode(self, diameter: float, height: float,
                                   wall_thickness: float = 0.30,
                                   infill: bool = True) -> str:
        """
        Generate G-code for curved circular wall using G2/G3 arcs.
        
        Args:
            diameter: Outer diameter of wall
            height: Wall height
            wall_thickness: Thickness of wall
            infill: Add hexagonal honeycomb infill
        """
        lines = self.generate_header()
        
        radius = diameter / 2
        inner_radius = radius - wall_thickness
        layers = int(height / self.layer_height)
        
        # Perimeter print speed (slower for quality)
        perimeter_speed = min(self.print_speed, 30)
        infill_speed = self.print_speed
        
        lines.append(f"; Circular wall: D={diameter}m, H={height}m")
        lines.append(f"; Layers: {layers}, Layer height: {self.layer_height*1000:.0f}mm")
        lines.append("")
        
        for layer in range(layers):
            z = (layer + 1) * self.layer_height
            
            lines.append(f"; Layer {layer + 1}/{layers} - Z{z:.3f}")
            
            # Outer wall (clockwise, G2)
            lines.append(f"G1 X{radius:.3f} Y0 Z{z:.3f} F{perimeter_speed*60:.0f}")
            lines.append(f"G2 X{radius:.3f} Y0 I{-radius:.3f} J0 ; Outer perimeter")
            
            # Inner wall (counter-clockwise, G3)
            lines.append(f"G1 X{inner_radius:.3f} Y0 Z{z:.3f}")
            lines.append(f"G3 X{inner_radius:.3f} Y0 I{-inner_radius:.3f} J0 ; Inner perimeter")
            
            # Honeycomb infill on specific layers
            if infill and layer % 3 == 0 and layer > 0:
                lines.append("; Honeycomb infill")
                lines.extend(self._generate_honeycomb_infill(
                    inner_radius, radius, z, infill_speed
                ))
            
            lines.append("")
        
        lines.append("G28 ; Return home")
        return "\n".join(lines)
    
    def _generate_honeycomb_infill(self, inner_r: float, outer_r: float, 
                                    z: float, speed: float) -> List[str]:
        """Generate hexagonal honeycomb infill pattern."""
        lines = []
        hex_size = 0.15  # 150mm hexagons
        
        # Simple honeycomb pattern - concentric hexagons
        r = inner_r + hex_size
        while r < outer_r - hex_size:
            lines.append(f"G1 X{r:.3f} Y0 Z{z:.3f} F{speed*60:.0f}")
            # Generate hexagon
            for i in range(6):
                angle = i * math.pi / 3
                next_angle = (i + 1) * math.pi / 3
                x1 = r * math.cos(angle)
                y1 = r * math.sin(angle)
                x2 = r * math.cos(next_angle)
                y2 = r * math.sin(next_angle)
                lines.append(f"G1 X{x2:.3f} Y{y2:.3f}")
            r += hex_size * 1.5
        
        return lines
    
    def generate_spiral_wall_gcode(self, diameter: float, height: float,
                                   pitch: float = None) -> str:
        """
        Generate continuous spiral/vase mode G-code.
        More efficient for circular walls.
        """
        pitch = pitch or self.layer_height
        lines = self.generate_header()
        
        radius = diameter / 2
        layers = int(height / pitch)
        
        lines.append(f"; Spiral vase mode: D={diameter}m, H={height}m")
        lines.append("G1 X{:.3f} Y0 Z{:.3f} F{:.0f}".format(
            radius, pitch, self.print_speed * 60
        ))
        
        # Continuous spiral
        z_step = pitch
        for layer in range(layers):
            z = (layer + 1) * z_step
            # Full circle with Z increment
            lines.append(
                f"G2 X{radius:.3f} Y0 Z{z:.3f} I{-radius:.3f} J0 "
                f"E{layer * 0.1:.2f} ; Spiral layer {layer+1}"
            )
        
        lines.append("G28")
        return "\n".join(lines)
    
    def generate_floor_gcode(self, diameter: float, thickness: float = 0.20) -> str:
        """Generate G-code for printed earth floor."""
        lines = self.generate_header()
        radius = diameter / 2
        layers = int(thickness / self.layer_height)
        
        lines.append(f"; Floor: D={diameter}m, T={thickness}m")
        
        for layer in range(layers):
            z = (layer + 1) * self.layer_height
            lines.append(f"G1 X0 Y0 Z{z:.3f}")
            # Spiral fill from center
            r = 0
            while r < radius:
                r = min(r + self.nozzle_diameter * 0.8, radius)
                lines.append(f"G2 X{r:.3f} Y0 I{-r/2:.3f} J0")
        
        lines.append("G28")
        return "\n".join(lines)


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
