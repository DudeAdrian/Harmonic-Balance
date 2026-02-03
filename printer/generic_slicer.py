"""
harmonic-balance/printer/generic_slicer.py
Generic earth printer slicer - Marlin firmware compatible.
Works with WASP Crane and other large-format earth printers.
"""

import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PrinterType(Enum):
    """Supported printer types."""
    WASP_CRANE = "wasp_crane"
    GENERIC_EARTH_PRINTER = "generic_earth"
    COBOD_BOD2 = "cobod_bod2"
    PERI_3D = "peri_3d"
    CUSTOM = "custom"


@dataclass
class PrinterConfig:
    """Configuration for earth printer."""
    name: str
    reach_radius_m: float  # Horizontal reach
    max_height_m: float
    nozzle_diameter_mm: float
    default_layer_height_mm: float
    max_print_speed_mm_s: float
    firmware: str = "Marlin"
    
    # Default settings for WASP Crane
    @classmethod
    def wasp_crane(cls) -> 'PrinterConfig':
        return cls(
            name="WASP Crane",
            reach_radius_m=3.0,
            max_height_m=3.5,
            nozzle_diameter_mm=40.0,
            default_layer_height_mm=20.0,
            max_print_speed_mm_s=50.0,
            firmware="Marlin"
        )
    
    @classmethod
    def generic_earth(cls) -> 'PrinterConfig':
        return cls(
            name="Generic Earth Printer",
            reach_radius_m=2.5,
            max_height_m=3.0,
            nozzle_diameter_mm=35.0,
            default_layer_height_mm=15.0,
            max_print_speed_mm_s=40.0,
            firmware="Marlin"
        )
    
    @classmethod
    def cobod_bod2(cls) -> 'PrinterConfig':
        return cls(
            name="COBOD BOD2",
            reach_radius_m=10.0,  # Gantry-based, effectively unlimited
            max_height_m=8.4,
            nozzle_diameter_mm=50.0,
            default_layer_height_mm=25.0,
            max_print_speed_mm_s=60.0,
            firmware="Marlin"
        )


class GenericSlicer:
    """
    Generic G-code slicer for earth construction.
    Compatible with WASP Crane and other Marlin-based earth printers.
    """
    
    def __init__(self, config: PrinterConfig = None):
        self.config = config or PrinterConfig.wasp_crane()
        self.layer_height = self.config.default_layer_height_mm / 1000  # Convert to meters
        self.nozzle = self.config.nozzle_diameter_mm / 1000
        self.speed = min(50, self.config.max_print_speed_mm_s)  # mm/s
        
    def generate_header(self, material: str = "local_earth_mix") -> List[str]:
        """Generate Marlin-compatible G-code header."""
        lines = [
            "; ============================================",
            "; Harmonic Habitats - Earth Construction G-code",
            f"; Generated for {self.config.name} or compatible earth printer",
            "; Firmware: Marlin (standard earth printing profile)",
            "; ============================================",
            "",
            "; Printer Specifications:",
            f";   Reach radius: {self.config.reach_radius_m}m",
            f";   Max height: {self.config.max_height_m}m",
            f";   Nozzle diameter: {self.config.nozzle_diameter_mm}mm",
            f";   Layer height: {self.config.default_layer_height_mm}mm",
            f";   Print speed: {self.speed}mm/s",
            "",
            f"; Material: {material}",
            "",
            "; Startup sequence",
            "G21 ; Set units to millimeters",
            "G90 ; Absolute positioning",
            "M82 ; Absolute extrusion (for paste extruders)",
            "G28 ; Home all axes",
            "G1 Z50 F3000 ; Move to safe height",
            "M400 ; Wait for moves to complete",
            "",
            "; Material preparation (manual)",
            "; 1. Load earth mix into hopper",
            "; 2. Prime extruder until consistent flow",
            "; 3. Verify nozzle clearance (paper test)",
            "M0 Click to begin printing... ; Pause for operator",
            ""
        ]
        return lines
    
    def generate_footer(self) -> List[str]:
        """Generate G-code footer."""
        return [
            "",
            "; Print complete",
            "M400 ; Wait for moves to complete",
            "G28 ; Home all axes",
            "M0 Print complete - clean nozzle and power down ; Final pause",
            "M84 ; Disable motors"
        ]
    
    def generate_circular_wall(self, diameter_m: float, height_m: float,
                               wall_thickness_m: float = 0.30,
                               infill: bool = True) -> str:
        """
        Generate G-code for circular wall using G2/G3 arcs.
        Compatible with all Marlin-based printers.
        """
        lines = self.generate_header()
        
        radius = diameter_m / 2
        inner_radius = radius - wall_thickness_m
        layers = int(height_m / self.layer_height)
        
        # Validate against printer limits
        if radius > self.config.reach_radius_m:
            lines.append(f"; WARNING: Radius {radius}m exceeds printer reach {self.config.reach_radius_m}m")
        if height_m > self.config.max_height_m:
            lines.append(f"; WARNING: Height {height_m}m exceeds printer limit {self.config.max_height_m}m")
        
        lines.append(f"; Circular wall: D={diameter_m}m, H={height_m}m, T={wall_thickness_m}m")
        lines.append(f"; Total layers: {layers}")
        lines.append("")
        
        # Perimeter speeds
        outer_speed = min(30, self.speed)  # Slower for outer wall quality
        inner_speed = self.speed
        
        for layer in range(layers):
            z = (layer + 1) * self.layer_height
            z_mm = z * 1000
            
            lines.append(f"; --- Layer {layer + 1}/{layers} (Z={z:.3f}m) ---")
            
            # Outer wall - clockwise arc (G2)
            lines.append(f"G1 X{radius:.3f} Y0 Z{z:.3f} F{outer_speed*60:.0f} ; Move to start")
            lines.append(f"G2 X{radius:.3f} Y0 I{-radius:.3f} J0 E{layer*0.5:.2f} ; Outer wall CW")
            
            # Inner wall - counter-clockwise arc (G3)
            lines.append(f"G1 X{inner_radius:.3f} Y0 Z{z:.3f} F{inner_speed*60:.0f}")
            lines.append(f"G3 X{inner_radius:.3f} Y0 I{-inner_radius:.3f} J0 ; Inner wall CCW")
            
            # Honeycomb infill every 3rd layer
            if infill and layer > 0 and layer % 3 == 0:
                lines.extend(self._generate_honeycomb_layer(
                    inner_radius, radius, z
                ))
            
            lines.append("")
        
        lines.extend(self.generate_footer())
        return "\n".join(lines)
    
    def _generate_honeycomb_layer(self, inner_r: float, outer_r: float, 
                                   z: float) -> List[str]:
        """Generate hexagonal honeycomb infill pattern."""
        lines = ["; Honeycomb infill layer"]
        hex_size = 0.15  # 150mm hexagons
        
        # Concentric hexagonal rings
        r = inner_r + hex_size
        ring = 0
        while r < outer_r - hex_size / 2:
            ring += 1
            lines.append(f"; Hex ring {ring} at r={r:.3f}m")
            
            # Generate hexagon vertices
            for i in range(7):  # 6 vertices + return to start
                angle = i * math.pi / 3
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                
                if i == 0:
                    lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f}")
                else:
                    lines.append(f"G1 X{x:.3f} Y{y:.3f}")
            
            r += hex_size * 1.5  # Step to next ring
        
        return lines
    
    def generate_straight_wall(self, length_m: float, height_m: float,
                               wall_thickness_m: float = 0.30) -> str:
        """Generate G-code for straight wall section."""
        lines = self.generate_header()
        
        layers = int(height_m / self.layer_height)
        
        lines.append(f"; Straight wall: L={length_m}m, H={height_m}m, T={wall_thickness_m}m")
        lines.append("")
        
        for layer in range(layers):
            z = (layer + 1) * self.layer_height
            
            lines.append(f"; Layer {layer + 1}")
            
            # Two perimeter lines for wall thickness
            y_outer = wall_thickness_m / 2
            y_inner = -wall_thickness_m / 2
            
            # Outer line
            lines.append(f"G1 X0 Y{y_outer:.3f} Z{z:.3f}")
            lines.append(f"G1 X{length_m:.3f} Y{y_outer:.3f} E{layer*0.3:.2f}")
            
            # Return inner line
            lines.append(f"G1 X{length_m:.3f} Y{y_inner:.3f}")
            lines.append(f"G1 X0 Y{y_inner:.3f}")
        
        lines.extend(self.generate_footer())
        return "\n".join(lines)
    
    def generate_spiral_vase(self, diameter_m: float, height_m: float) -> str:
        """
        Generate continuous spiral vase mode G-code.
        Most efficient for single-wall circular structures.
        """
        lines = self.generate_header()
        
        radius = diameter_m / 2
        layers = int(height_m / self.layer_height)
        
        lines.append(f"; Spiral vase mode: D={diameter_m}m, H={height_m}m")
        lines.append("; Continuous spiral - no Z-seams")
        lines.append("")
        
        # Start position
        lines.append(f"G1 X{radius:.3f} Y0 Z{self.layer_height:.3f} F{self.speed*60:.0f}")
        
        # Continuous spiral - each circle increments Z
        for layer in range(layers):
            z = (layer + 1) * self.layer_height
            # G2 with Z increment creates spiral
            lines.append(
                f"G2 X{radius:.3f} Y0 Z{z:.3f} I{-radius:.3f} J0 "
                f"E{layer*0.1:.2f} ; Spiral layer {layer+1}"
            )
        
        lines.extend(self.generate_footer())
        return "\n".join(lines)
    
    def generate_printer_compatibility_report(self, geometry_specs: Dict) -> str:
        """Generate compatibility report for current printer config."""
        report = [
            "=" * 60,
            "PRINTER COMPATIBILITY REPORT",
            "=" * 60,
            "",
            f"Printer: {self.config.name}",
            f"Firmware: {self.config.firmware}",
            "",
            "Printer Specifications:",
            f"  - Reach radius: {self.config.reach_radius_m}m",
            f"  - Maximum height: {self.config.max_height_m}m",
            f"  - Nozzle diameter: {self.config.nozzle_diameter_mm}mm",
            f"  - Default layer height: {self.config.default_layer_height_mm}mm",
            f"  - Max print speed: {self.config.max_print_speed_mm_s}mm/s",
            "",
            "Geometry Requirements:",
        ]
        
        if 'diameter' in geometry_specs:
            d = geometry_specs['diameter']
            r = d / 2
            fits = r <= self.config.reach_radius_m
            report.append(f"  - Diameter: {d}m (radius {r}m) {'✓' if fits else '✗ EXCEEDS REACH'}")
        
        if 'height' in geometry_specs:
            h = geometry_specs['height']
            fits = h <= self.config.max_height_m
            report.append(f"  - Height: {h}m {'✓' if fits else '✗ EXCEEDS LIMIT'}")
        
        if 'length' in geometry_specs:
            l = geometry_specs['length']
            report.append(f"  - Length: {l}m (check against build volume)")
        
        report.extend([
            "",
            "Recommendations:",
            f"  - Use layer height: {self.config.default_layer_height_mm}mm",
            f"  - Recommended speed: {min(30, self.config.max_print_speed_mm_s)}mm/s perimeters",
            "  - Material: Local earth mix (see materials.py)",
            "",
            "Notes:",
            "  - This G-code is compatible with any Marlin firmware printer",
            "  - Calibrated for WASP Crane - adjust speeds for other printers",
            "  - Always verify nozzle clearance before printing",
            "",
            "Generated by Harmonic Habitats Generic Slicer",
            "=" * 60
        ])
        
        return "\n".join(report)


def get_printer_config(printer_type: str) -> PrinterConfig:
    """Get configuration for named printer type."""
    configs = {
        'wasp_crane': PrinterConfig.wasp_crane(),
        'wasp': PrinterConfig.wasp_crane(),
        'generic': PrinterConfig.generic_earth(),
        'cobod': PrinterConfig.cobod_bod2(),
        'cobod_bod2': PrinterConfig.cobod_bod2()
    }
    return configs.get(printer_type.lower(), PrinterConfig.wasp_crane())


def generate_for_printer(typology: str, printer_type: str = "wasp_crane",
                         **geometry_params) -> Dict:
    """
    Generate G-code for specific printer.
    
    Args:
        typology: 'single_pod', 'straight_wall', etc.
        printer_type: 'wasp_crane', 'generic', 'cobod', etc.
        **geometry_params: Geometry specifications
    
    Returns:
        Dict with G-code and compatibility report
    """
    config = get_printer_config(printer_type)
    slicer = GenericSlicer(config)
    
    if typology == 'single_pod':
        gcode = slicer.generate_circular_wall(
            diameter_m=geometry_params.get('diameter', 6.5),
            height_m=geometry_params.get('height', 3.2),
            wall_thickness_m=geometry_params.get('wall_thickness', 0.30)
        )
    elif typology == 'straight_wall':
        gcode = slicer.generate_straight_wall(
            length_m=geometry_params.get('length', 10.0),
            height_m=geometry_params.get('height', 3.0),
            wall_thickness_m=geometry_params.get('wall_thickness', 0.30)
        )
    elif typology == 'spiral_vase':
        gcode = slicer.generate_spiral_vase(
            diameter_m=geometry_params.get('diameter', 6.0),
            height_m=geometry_params.get('height', 3.0)
        )
    else:
        raise ValueError(f"Unknown typology: {typology}")
    
    report = slicer.generate_printer_compatibility_report(geometry_params)
    
    return {
        'gcode': gcode,
        'compatibility_report': report,
        'printer': config.name,
        'firmware': config.firmware
    }


if __name__ == "__main__":
    print("=== Generic Earth Printer Slicer ===")
    
    # Test with WASP Crane (default)
    print("\n--- WASP Crane ---")
    result = generate_for_printer('single_pod', 'wasp_crane', diameter=6.5, height=3.2)
    print(f"Printer: {result['printer']}")
    print(f"G-code lines: {len(result['gcode'].split(chr(10)))}")
    print("\nCompatibility Report:")
    print(result['compatibility_report'])
    
    # Test with generic printer
    print("\n--- Generic Earth Printer ---")
    result = generate_for_printer('single_pod', 'generic', diameter=6.5, height=3.2)
    print(f"Printer: {result['printer']}")
    print(f"G-code lines: {len(result['gcode'].split(chr(10)))}")
