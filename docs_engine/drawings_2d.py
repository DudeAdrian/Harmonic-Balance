"""
harmonic-balance/docs_engine/drawings_2d.py
AutoCAD-compatible DXF generation for architectural drawings.
AIA layer standards, professional drafting conventions.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Try to import ezdxf, provide fallback if not available
try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False


# AIA CAD Layer Guidelines (simplified)
AIA_LAYERS = {
    'A-WALL': {'color': 1, 'linetype': 'CONTINUOUS', 'description': 'Walls'},
    'A-WALL-PATT': {'color': 8, 'linetype': 'CONTINUOUS', 'description': 'Wall patterns'},
    'A-DOOR': {'color': 2, 'linetype': 'CONTINUOUS', 'description': 'Doors'},
    'A-WIND': {'color': 4, 'linetype': 'CONTINUOUS', 'description': 'Windows'},
    'A-FLOR': {'color': 3, 'linetype': 'CONTINUOUS', 'description': 'Floors'},
    'A-ROOF': {'color': 5, 'linetype': 'CONTINUOUS', 'description': 'Roof'},
    'A-DIMS': {'color': 6, 'linetype': 'CONTINUOUS', 'description': 'Dimensions'},
    'A-TEXT': {'color': 7, 'linetype': 'CONTINUOUS', 'description': 'Text/Annotations'},
    'A-TTLB': {'color': 7, 'linetype': 'CONTINUOUS', 'description': 'Title block'},
    'A-SECT': {'color': 9, 'linetype': 'DASHED', 'description': 'Section cuts'},
    'A-ELEV': {'color': 7, 'linetype': 'CONTINUOUS', 'description': 'Elevations'},
    'DEFPOINTS': {'color': 8, 'linetype': 'CONTINUOUS', 'description': 'Definition points'},
}


@dataclass
class DrawingSheet:
    """Drawing sheet configuration."""
    project_name: str
    drawing_title: str
    drawing_number: str
    scale: str
    date: str
    drawn_by: str = "Harmonic Habitats"
    checked_by: str = ""
    sheet_size: str = "A1"  # A0, A1, A2, A3, A4


class DXFGenerator:
    """Generate AutoCAD-compatible DXF drawings."""
    
    def __init__(self, project_name: str = "Harmonic Habitat"):
        self.project_name = project_name
        self.doc = None
        self.msp = None  # Model space
        self.paperspace = None
        
    def _create_document(self) -> Optional['ezdxf.document.Drawing']:
        """Create new DXF document with R2018 format."""
        if not EZDXF_AVAILABLE:
            return None
        
        doc = ezdxf.new('R2018', setup=True)
        
        # Set up AIA layers
        for layer_name, props in AIA_LAYERS.items():
            doc.layers.add(
                name=layer_name,
                color=props['color'],
                linetype=props['linetype']
            )
        
        # Set up text styles
        doc.styles.add('ARCH', font='Arial.ttf')
        doc.styles.add('DIM', font='Arial.ttf')
        
        self.msp = doc.modelspace()
        return doc
    
    def generate_floor_plan(self, geometry: Dict, sheet: DrawingSheet, 
                           output_path: Path) -> Path:
        """
        Generate floor plan DXF.
        
        Includes: walls, doors, windows, room labels, dimensions
        """
        self.doc = self._create_document()
        if not self.doc:
            return self._create_mock_dxf(output_path, "Floor Plan")
        
        # Set up layout
        layout = self.doc.layouts.active_layout()
        
        # Get geometry parameters
        if geometry['type'] == 'single_pod':
            self._draw_single_pod_floor_plan(geometry)
        elif geometry['type'] == 'organic_family':
            self._draw_organic_family_floor_plan(geometry)
        elif geometry['type'] == 'multi_pod_cluster':
            self._draw_multi_pod_floor_plan(geometry)
        
        # Add dimensions
        self._add_dimensions(geometry)
        
        # Add room labels
        self._add_room_labels(geometry)
        
        # Add title block
        self._add_title_block(sheet, layout)
        
        # Save
        self.doc.saveas(output_path)
        return output_path
    
    def _draw_single_pod_floor_plan(self, geometry: Dict):
        """Draw circular single pod floor plan."""
        if not self.msp:
            return
        
        radius = geometry.get('diameter', 6.5) * 1000 / 2  # Convert to mm
        wall_thickness = 300  # mm
        core_radius = 600  # mm
        
        # Outer wall
        self.msp.add_circle(
            center=(0, 0),
            radius=radius,
            dxfattribs={'layer': 'A-WALL'}
        )
        
        # Inner wall line
        self.msp.add_circle(
            center=(0, 0),
            radius=radius - wall_thickness,
            dxfattribs={'layer': 'A-WALL'}
        )
        
        # Central service core
        self.msp.add_circle(
            center=(0, 0),
            radius=core_radius,
            dxfattribs={'layer': 'A-WALL'}
        )
        
        # Door (1m wide)
        door_angle = math.radians(90)
        door_width = 1000
        door_x = (radius - wall_thickness/2) * math.cos(door_angle)
        door_y = (radius - wall_thickness/2) * math.sin(door_angle)
        
        # Draw door swing
        self.msp.add_arc(
            center=(door_x, door_y),
            radius=door_width,
            start_angle=90,
            end_angle=180,
            dxfattribs={'layer': 'A-DOOR'}
        )
        
        # Draw door opening
        door_start = (door_x, door_y + wall_thickness/2)
        door_end = (door_x - door_width, door_y + wall_thickness/2)
        self.msp.add_line(door_start, door_end, dxfattribs={'layer': 'A-DOOR'})
        
        # Window (0.8m wide)
        window_angle = math.radians(270)
        window_width = 800
        win_x = radius * math.cos(window_angle)
        win_y = radius * math.sin(window_angle)
        
        # Window opening
        win_start = (win_x - window_width/2, win_y)
        win_end = (win_x + window_width/2, win_y)
        self.msp.add_line(win_start, win_end, dxfattribs={'layer': 'A-WIND'})
        
        # Radial division lines (zones)
        for angle_deg in [0, 90, 180, 270]:
            angle = math.radians(angle_deg)
            x1 = core_radius * math.cos(angle)
            y1 = core_radius * math.sin(angle)
            x2 = (radius - wall_thickness) * math.cos(angle)
            y2 = (radius - wall_thickness) * math.sin(angle)
            self.msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'A-FLOR'})
    
    def _draw_organic_family_floor_plan(self, geometry: Dict):
        """Draw organic family dwelling floor plan."""
        if not self.msp:
            return
        
        length = geometry.get('length', 15.0) * 1000  # mm
        width = geometry.get('width', 5.6) * 1000  # mm
        wall_thickness = 350  # mm
        
        # Building outline with flowing curves
        points = []
        segments = 20
        for i in range(segments + 1):
            t = i / segments
            x = (t - 0.5) * length
            # Slight curvature for organic feel
            width_var = width + 200 * math.sin(2 * math.pi * t)
            y_top = width_var / 2
            y_bottom = -width_var / 2
            points.append((x, y_top))
        
        for i in range(segments, -1, -1):
            t = i / segments
            x = (t - 0.5) * length
            width_var = width + 200 * math.sin(2 * math.pi * t)
            y_bottom = -width_var / 2
            points.append((x, y_bottom))
        
        # Draw outer wall
        self.msp.add_lwpolyline(points, close=True, dxfattribs={'layer': 'A-WALL'})
        
        # Inner wall (offset)
        inner_points = []
        for x, y in points:
            # Simple offset inward
            if y > 0:
                inner_points.append((x, y - wall_thickness))
            else:
                inner_points.append((x, y + wall_thickness))
        
        self.msp.add_lwpolyline(inner_points, close=True, dxfattribs={'layer': 'A-WALL'})
        
        # Room divisions
        room_lines = [
            ((-length/4, -width/2), (-length/4, width/2)),
            ((0, -width/2), (0, width/2)),
            ((length/4, -width/2), (length/4, width/2)),
        ]
        for start, end in room_lines:
            self.msp.add_line(start, end, dxfattribs={'layer': 'A-FLOR'})
    
    def _draw_multi_pod_floor_plan(self, geometry: Dict):
        """Draw multi-pod cluster site plan."""
        if not self.msp:
            return
        
        arrangement_radius = 12000  # mm (12m)
        pod_radius = 3000  # mm (3m)
        pod_count = geometry.get('pod_count', 4)
        
        # Central gathering space
        self.msp.add_circle(
            center=(0, 0),
            radius=4000,
            dxfattribs={'layer': 'A-FLOR'}
        )
        
        # Pods in circular arrangement
        for i in range(pod_count):
            angle = 2 * math.pi * i / pod_count
            x = arrangement_radius * math.cos(angle)
            y = arrangement_radius * math.sin(angle)
            
            # Pod outline
            self.msp.add_circle(
                center=(x, y),
                radius=pod_radius,
                dxfattribs={'layer': 'A-WALL'}
            )
            
            # Walkway to center
            self.msp.add_line(
                (x * 0.5, y * 0.5),
                (x * 0.7, y * 0.7),
                dxfattribs={'layer': 'A-FLOR'}
            )
        
        # Site boundary
        self.msp.add_circle(
            center=(0, 0),
            radius=arrangement_radius + pod_radius + 2000,
            dxfattribs={'layer': 'DEFPOINTS'}
        )
    
    def _add_dimensions(self, geometry: Dict):
        """Add dimension lines to drawing."""
        if not self.msp:
            return
        
        # Simplified dimensioning - just text labels for now
        dim_style = {
            'layer': 'A-DIMS',
            'height': 100,  # 100mm text height
            'style': 'DIM'
        }
        
        if geometry['type'] == 'single_pod':
            radius = geometry.get('diameter', 6.5) * 1000 / 2
            self.msp.add_text(
                f"Ø{int(radius*2/1000)}m",
                dxfattribs={**dim_style, 'insert': (0, -radius - 500)}
            )
    
    def _add_room_labels(self, geometry: Dict):
        """Add room name labels."""
        if not self.msp:
            return
        
        text_style = {
            'layer': 'A-TEXT',
            'height': 150,  # 150mm text height
            'style': 'ARCH'
        }
        
        if geometry['type'] == 'single_pod':
            labels = [
                ('LIVING', (-1500, 1500)),
                ('SLEEPING', (1500, 1500)),
                ('SERVICES', (1500, -1500)),
                ('ENTRY', (-1500, -1500)),
            ]
            for text, pos in labels:
                self.msp.add_text(text, dxfattribs={**text_style, 'insert': pos})
    
    def _add_title_block(self, sheet: DrawingSheet, layout):
        """Add title block to drawing."""
        if not self.msp:
            return
        
        # Title block position (bottom right of A1 sheet)
        # A1 = 841mm x 594mm
        tb_x = 20000  # Position in model space
        tb_y = 0
        tb_width = 5000
        tb_height = 3000
        
        # Title block border
        self.msp.add_lwpolyline([
            (tb_x, tb_y),
            (tb_x + tb_width, tb_y),
            (tb_x + tb_width, tb_y + tb_height),
            (tb_x, tb_y + tb_height),
        ], close=True, dxfattribs={'layer': 'A-TTLB'})
        
        # Title block text
        title_attribs = {
            'layer': 'A-TTLB',
            'height': 200,
            'style': 'ARCH'
        }
        
        self.msp.add_text(
            f"PROJECT: {sheet.project_name}",
            dxfattribs={**title_attribs, 'insert': (tb_x + 200, tb_y + 2500)}
        )
        self.msp.add_text(
            f"TITLE: {sheet.drawing_title}",
            dxfattribs={**title_attribs, 'insert': (tb_x + 200, tb_y + 2200)}
        )
        self.msp.add_text(
            f"DRAWING NO: {sheet.drawing_number}",
            dxfattribs={**title_attribs, 'insert': (tb_x + 200, tb_y + 1900)}
        )
        self.msp.add_text(
            f"SCALE: {sheet.scale}",
            dxfattribs={**title_attribs, 'insert': (tb_x + 200, tb_y + 1600)}
        )
        self.msp.add_text(
            f"DATE: {sheet.date}",
            dxfattribs={**title_attribs, 'insert': (tb_x + 200, tb_y + 1300)}
        )
        self.msp.add_text(
            f"DRAWN BY: {sheet.drawn_by}",
            dxfattribs={**title_attribs, 'insert': (tb_x + 200, tb_y + 1000)}
        )
    
    def generate_section(self, geometry: Dict, sheet: DrawingSheet,
                        output_path: Path) -> Path:
        """Generate building section DXF."""
        self.doc = self._create_document()
        if not self.doc:
            return self._create_mock_dxf(output_path, "Section")
        
        layout = self.doc.layouts.active_layout()
        
        if geometry['type'] == 'single_pod':
            radius = geometry.get('diameter', 6.5) * 1000 / 2
            height = 3200  # mm
            
            # Ground line
            self.msp.add_line((-radius - 1000, 0), (radius + 1000, 0),
                             dxfattribs={'layer': 'DEFPOINTS'})
            
            # Wall section
            wall_points = [
                (-radius, 0),
                (-radius, height),
                (-radius + 300, height),
                (-radius + 300, 0),
            ]
            self.msp.add_lwpolyline(wall_points, close=True, dxfattribs={'layer': 'A-WALL'})
            
            # Roof
            self.msp.add_line((-radius - 200, height), (radius + 200, height),
                             dxfattribs={'layer': 'A-ROOF'})
            
            # Foundation
            self.msp.add_line((-radius - 500, -500), (radius + 500, -500),
                             dxfattribs={'layer': 'A-WALL'})
        
        self._add_title_block(sheet, layout)
        self.doc.saveas(output_path)
        return output_path
    
    def generate_elevation(self, geometry: Dict, sheet: DrawingSheet,
                          output_path: Path) -> Path:
        """Generate building elevation DXF."""
        self.doc = self._create_document()
        if not self.doc:
            return self._create_mock_dxf(output_path, "Elevation")
        
        layout = self.doc.layouts.active_layout()
        
        if geometry['type'] == 'single_pod':
            width = geometry.get('diameter', 6.5) * 1000
            height = 3200
            
            # Ground line
            self.msp.add_line((-500, 0), (width + 500, 0), dxfattribs={'layer': 'DEFPOINTS'})
            
            # Wall outline
            self.msp.add_line((0, 0), (0, height), dxfattribs={'layer': 'A-WALL'})
            self.msp.add_line((width, 0), (width, height), dxfattribs={'layer': 'A-WALL'})
            self.msp.add_line((0, height), (width, height), dxfattribs={'layer': 'A-WALL'})
            
            # Window
            win_width = 800
            win_height = 1200
            win_x = width / 2 - win_width / 2
            win_y = 1200
            
            window_rect = [
                (win_x, win_y),
                (win_x + win_width, win_y),
                (win_x + win_width, win_y + win_height),
                (win_x, win_y + win_height),
            ]
            self.msp.add_lwpolyline(window_rect, close=True, dxfattribs={'layer': 'A-WIND'})
        
        self._add_title_block(sheet, layout)
        self.doc.saveas(output_path)
        return output_path
    
    def _create_mock_dxf(self, output_path: Path, drawing_type: str) -> Path:
        """Create placeholder DXF when ezdxf not available."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a minimal DXF file
        content = f"""0
SECTION
2
HEADER
9
$ACADVER
1
AC1032
0
ENDSEC
2
CLASSES
0
ENDSEC
2
TABLES
0
ENDSEC
2
BLOCKS
0
ENDSEC
2
ENTITIES
0
TEXT
5
1
8
0
10
0.0
20
0.0
30
0.0
40
100.0
1
{self.project_name} - {drawing_type} (ezdxf not installed)
0
ENDSEC
0
EOF
"""
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path


def create_drawing_set(project_name: str, geometry: Dict, 
                       output_dir: Path) -> Dict[str, Path]:
    """
    Create complete drawing set for a project.
    
    Returns dict mapping drawing names to file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    generator = DXFGenerator(project_name)
    
    drawings = {}
    
    # Floor Plan
    floor_sheet = DrawingSheet(
        project_name=project_name,
        drawing_title="FLOOR PLAN",
        drawing_number="A-101",
        scale="1:50",
        date=date_str
    )
    drawings['floor_plan'] = generator.generate_floor_plan(
        geometry, floor_sheet, output_dir / 'A-101_FLOOR_PLAN.dxf'
    )
    
    # Section
    section_sheet = DrawingSheet(
        project_name=project_name,
        drawing_title="SECTION A-A",
        drawing_number="A-201",
        scale="1:50",
        date=date_str
    )
    drawings['section'] = generator.generate_section(
        geometry, section_sheet, output_dir / 'A-201_SECTION.dxf'
    )
    
    # Elevations
    for i, elev_name in enumerate(['NORTH', 'SOUTH', 'EAST', 'WEST'], 1):
        elev_sheet = DrawingSheet(
            project_name=project_name,
            drawing_title=f"ELEVATION - {elev_name}",
            drawing_number=f"A-30{i}",
            scale="1:50",
            date=date_str
        )
        drawings[f'elevation_{elev_name.lower()}'] = generator.generate_elevation(
            geometry, elev_sheet, output_dir / f'A-30{i}_ELEVATION_{elev_name}.dxf'
        )
    
    return drawings


if __name__ == "__main__":
    print("DXF Generator Test")
    
    # Test with single pod
    geometry = {
        'type': 'single_pod',
        'diameter': 6.5,
        'height': 3.2
    }
    
    output_dir = Path(__file__).parent / 'outputs' / 'test_dxf'
    drawings = create_drawing_set("Test Single Pod", geometry, output_dir)
    
    print(f"Created {len(drawings)} drawings:")
    for name, path in drawings.items():
        print(f"  {name}: {path}")
