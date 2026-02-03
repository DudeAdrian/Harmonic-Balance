"""
harmonic-balance/docs_engine/schedules.py
Material, door/window, and room schedules for construction documentation.
Exports to CSV and PDF table format.
"""

import csv
import io
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Try to import reportlab for PDF export
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@dataclass
class MaterialItem:
    """Material schedule item."""
    item_code: str
    description: str
    quantity: float
    unit: str
    specification: str
    supplier: str = ""
    notes: str = ""


@dataclass
class DoorWindowItem:
    """Door or window schedule item."""
    type_code: str
    description: str
    width_mm: int
    height_mm: int
    material: str
    u_value: float
    quantity: int
    location: str = ""


@dataclass
class RoomItem:
    """Room schedule item."""
    room_number: str
    room_name: str
    area_m2: float
    volume_m3: float
    max_occupancy: int
    floor_finish: str
    wall_finish: str
    ceiling_finish: str


class ScheduleGenerator:
    """Generate construction schedules."""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.materials: List[MaterialItem] = []
        self.doors_windows: List[DoorWindowItem] = []
        self.rooms: List[RoomItem] = []
    
    def generate_from_geometry(self, geometry: Dict, typology: str):
        """Generate all schedules from geometry data."""
        self._generate_material_schedule(geometry, typology)
        self._generate_door_window_schedule(geometry, typology)
        self._generate_room_schedule(geometry, typology)
    
    def _generate_material_schedule(self, geometry: Dict, typology: str):
        """Generate material takeoff schedule."""
        self.materials = []
        
        if typology == 'single_pod':
            diameter = geometry.get('diameter', 6.5)
            height = 3.2
            wall_thickness = 0.30
            
            # Calculate volumes
            outer_radius = diameter / 2
            inner_radius = outer_radius - wall_thickness
            wall_area = 3.14159 * (outer_radius**2 - inner_radius**2)
            wall_volume = wall_area * height
            
            # Wall material
            self.materials.append(MaterialItem(
                item_code="M-001",
                description="3D Printed Earth Wall",
                quantity=round(wall_volume, 2),
                unit="m³",
                specification="Clay 30%, Sand 50%, Silt 20%, Water 8%. Lime stabilizer 5%.",
                supplier="Local source + WASP Crane",
                notes="Print in 200mm layers, cure 28 days"
            ))
            
            # Floor
            floor_area = 3.14159 * inner_radius**2
            self.materials.append(MaterialItem(
                item_code="M-002",
                description="Earth Floor Slab",
                quantity=round(floor_area * 0.20, 2),
                unit="m³",
                specification="Rammed earth, 200mm thick",
                notes="Compact in 100mm lifts"
            ))
            
            # Door
            self.materials.append(MaterialItem(
                item_code="M-003",
                description="Timber Door",
                quantity=1,
                unit="nr",
                specification="Solid timber, 44mm thick, hardwood frame",
                supplier="Local timber"
            ))
            
            # Window
            self.materials.append(MaterialItem(
                item_code="M-004",
                description="Double Glazed Window",
                quantity=1,
                unit="nr",
                specification="800x1200mm, Low-E glass, U-value 1.2 W/m²K",
                u_value=1.2
            ))
            
            # Roof
            self.materials.append(MaterialItem(
                item_code="M-005",
                description="Green Roof System",
                quantity=round(floor_area, 2),
                unit="m²",
                specification="ETFE membrane + growing medium + indigenous plants",
                notes="Extensive green roof, 150mm substrate"
            ))
            
        elif typology == 'organic_family':
            length = geometry.get('length', 15.0)
            width = geometry.get('width', 5.6)
            levels = geometry.get('levels', 2)
            footprint = length * width
            
            # Wall material
            wall_length = 2 * (length + width)
            wall_height = 2.8 * levels
            wall_thickness = 0.35
            wall_volume = wall_length * wall_height * wall_thickness
            
            self.materials.append(MaterialItem(
                item_code="M-001",
                description="3D Printed Earth Wall",
                quantity=round(wall_volume, 2),
                unit="m³",
                specification="Enhanced mix with quartz additive for resonance",
                notes="Includes spiral stair walls"
            ))
            
            # Floors
            self.materials.append(MaterialItem(
                item_code="M-002",
                description="Earth Floor Slabs",
                quantity=round(footprint * 0.20 * levels, 2),
                unit="m³",
                specification="Rammed earth, 200mm thick per level"
            ))
            
            # Doors
            self.materials.append(MaterialItem(
                item_code="M-003",
                description="Timber Doors",
                quantity=levels + 1,  # Entry + per level
                unit="nr",
                specification="Solid timber, 44mm thick"
            ))
            
            # Windows
            self.materials.append(MaterialItem(
                item_code="M-004",
                description="Double Glazed Windows",
                quantity=6,  # Multiple for family dwelling
                unit="nr",
                specification="Various sizes, Low-E glass, U-value 1.2 W/m²K"
            ))
            
            # Roof
            self.materials.append(MaterialItem(
                item_code="M-005",
                description="Roof Structure",
                quantity=round(footprint * 1.2, 2),  # Includes overhang
                unit="m²",
                specification="Timber frame + ETFE membrane"
            ))
    
    def _generate_door_window_schedule(self, geometry: Dict, typology: str):
        """Generate door and window schedule."""
        self.doors_windows = []
        
        if typology == 'single_pod':
            self.doors_windows.extend([
                DoorWindowItem(
                    type_code="D-01",
                    description="Main Entry Door",
                    width_mm=1000,
                    height_mm=2100,
                    material="Solid timber, oak",
                    u_value=1.8,
                    quantity=1,
                    location="South elevation"
                ),
                DoorWindowItem(
                    type_code="W-01",
                    description="Living Window",
                    width_mm=800,
                    height_mm=1200,
                    material="Timber frame, double glazing",
                    u_value=1.2,
                    quantity=1,
                    location="North elevation"
                ),
            ])
            
        elif typology == 'organic_family':
            self.doors_windows.extend([
                DoorWindowItem(
                    type_code="D-01",
                    description="Main Entry Door",
                    width_mm=1000,
                    height_mm=2100,
                    material="Solid timber, oak",
                    u_value=1.8,
                    quantity=1,
                    location="South elevation"
                ),
                DoorWindowItem(
                    type_code="D-02",
                    description="Bedroom Door",
                    width_mm=900,
                    height_mm=2100,
                    material="Solid timber, pine",
                    u_value=2.0,
                    quantity=4,
                    location="Internal"
                ),
                DoorWindowItem(
                    type_code="W-01",
                    description="Large Window",
                    width_mm=1500,
                    height_mm=1200,
                    material="Timber frame, double glazing",
                    u_value=1.2,
                    quantity=2,
                    location="East and West"
                ),
                DoorWindowItem(
                    type_code="W-02",
                    description="Standard Window",
                    width_mm=1000,
                    height_mm=1200,
                    material="Timber frame, double glazing",
                    u_value=1.2,
                    quantity=4,
                    location="Various"
                ),
            ])
    
    def _generate_room_schedule(self, geometry: Dict, typology: str):
        """Generate room schedule."""
        self.rooms = []
        
        if typology == 'single_pod':
            diameter = geometry.get('diameter', 6.5)
            radius = diameter / 2
            area = 3.14159 * (radius - 0.3)**2
            volume = area * 3.2
            
            self.rooms.extend([
                RoomItem(
                    room_number="01",
                    room_name="Living Space",
                    area_m2=round(area * 0.4, 2),
                    volume_m3=round(area * 0.4 * 3.2, 2),
                    max_occupancy=4,
                    floor_finish="Rammed earth, natural seal",
                    wall_finish="3D printed earth, natural",
                    ceiling_finish="Timber, exposed"
                ),
                RoomItem(
                    room_number="02",
                    room_name="Sleeping Area",
                    area_m2=round(area * 0.35, 2),
                    volume_m3=round(area * 0.35 * 3.2, 2),
                    max_occupancy=2,
                    floor_finish="Rammed earth, natural seal",
                    wall_finish="3D printed earth, natural",
                    ceiling_finish="Timber, exposed"
                ),
                RoomItem(
                    room_number="03",
                    room_name="Service Core",
                    area_m2=round(area * 0.25, 2),
                    volume_m3=round(area * 0.25 * 3.2, 2),
                    max_occupancy=1,
                    floor_finish="Rammed earth, sealed",
                    wall_finish="3D printed earth, lime plaster",
                    ceiling_finish="Timber, exposed"
                ),
            ])
            
        elif typology == 'organic_family':
            length = geometry.get('length', 15.0)
            width = geometry.get('width', 5.6)
            
            self.rooms.extend([
                RoomItem(
                    room_number="01",
                    room_name="Living / Dining",
                    area_m2=43.0,
                    volume_m3=120.4,
                    max_occupancy=8,
                    floor_finish="Rammed earth",
                    wall_finish="3D printed earth",
                    ceiling_finish="Timber"
                ),
                RoomItem(
                    room_number="02",
                    room_name="Kitchen",
                    area_m2=18.0,
                    volume_m3=50.4,
                    max_occupancy=4,
                    floor_finish="Terracotta tiles",
                    wall_finish="Lime plaster",
                    ceiling_finish="Timber"
                ),
                RoomItem(
                    room_number="03-06",
                    room_name="Bedrooms",
                    area_m2=50.0,
                    volume_m3=140.0,
                    max_occupancy=8,
                    floor_finish="Timber",
                    wall_finish="Lime plaster",
                    ceiling_finish="Timber"
                ),
                RoomItem(
                    room_number="07-08",
                    room_name="Bathrooms",
                    area_m2=12.0,
                    volume_m3=33.6,
                    max_occupancy=2,
                    floor_finish="Stone tiles",
                    wall_finish="Tadelakt",
                    ceiling_finish="Timber"
                ),
            ])
    
    def export_csv(self, output_dir: Path) -> Dict[str, Path]:
        """Export all schedules to CSV files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Material schedule
        material_path = output_dir / 'schedule_materials.csv'
        with open(material_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Item Code', 'Description', 'Quantity', 'Unit', 
                           'Specification', 'Supplier', 'Notes'])
            for item in self.materials:
                writer.writerow([
                    item.item_code, item.description, item.quantity, item.unit,
                    item.specification, item.supplier, item.notes
                ])
        files['materials'] = material_path
        
        # Door/Window schedule
        dw_path = output_dir / 'schedule_doors_windows.csv'
        with open(dw_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Type Code', 'Description', 'Width (mm)', 'Height (mm)',
                           'Material', 'U-Value (W/m²K)', 'Quantity', 'Location'])
            for item in self.doors_windows:
                writer.writerow([
                    item.type_code, item.description, item.width_mm, item.height_mm,
                    item.material, item.u_value, item.quantity, item.location
                ])
        files['doors_windows'] = dw_path
        
        # Room schedule
        room_path = output_dir / 'schedule_rooms.csv'
        with open(room_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Room No.', 'Room Name', 'Area (m²)', 'Volume (m³)',
                           'Max Occupancy', 'Floor Finish', 'Wall Finish', 'Ceiling Finish'])
            for item in self.rooms:
                writer.writerow([
                    item.room_number, item.room_name, item.area_m2, item.volume_m3,
                    item.max_occupancy, item.floor_finish, item.wall_finish, item.ceiling_finish
                ])
        files['rooms'] = room_path
        
        return files
    
    def export_pdf(self, output_path: Path) -> Path:
        """Export all schedules as PDF."""
        if not REPORTLAB_AVAILABLE:
            return self._create_mock_pdf(output_path)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'ScheduleTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph(f"<b>{self.project_name}</b>", title_style))
        story.append(Paragraph("Construction Schedules", title_style))
        story.append(Spacer(1, 20))
        
        # Material Schedule
        story.append(Paragraph("<b>1. MATERIAL SCHEDULE</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        if self.materials:
            mat_data = [['Code', 'Description', 'Qty', 'Unit', 'Specification']]
            for item in self.materials:
                mat_data.append([
                    item.item_code,
                    Paragraph(item.description, styles['Normal']),
                    str(item.quantity),
                    item.unit,
                    Paragraph(item.specification[:100] + '...', styles['Small'])
                ])
            
            mat_table = Table(mat_data, colWidths=[20*mm, 50*mm, 20*mm, 15*mm, 100*mm])
            mat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            story.append(mat_table)
        
        story.append(Spacer(1, 20))
        
        # Door/Window Schedule
        story.append(Paragraph("<b>2. DOOR AND WINDOW SCHEDULE</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        if self.doors_windows:
            dw_data = [['Type', 'Description', 'Size (mm)', 'Material', 'U-Value', 'Qty']]
            for item in self.doors_windows:
                size = f"{item.width_mm} x {item.height_mm}"
                dw_data.append([
                    item.type_code,
                    item.description,
                    size,
                    Paragraph(item.material, styles['Small']),
                    f"{item.u_value:.2f}",
                    str(item.quantity)
                ])
            
            dw_table = Table(dw_data, colWidths=[20*mm, 60*mm, 35*mm, 60*mm, 25*mm, 15*mm])
            dw_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.9, 0.95, 1.0)),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(dw_table)
        
        story.append(Spacer(1, 20))
        
        # Room Schedule
        story.append(Paragraph("<b>3. ROOM SCHEDULE</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        if self.rooms:
            room_data = [['No.', 'Name', 'Area (m²)', 'Volume (m³)', 'Occupancy', 'Floor', 'Walls']]
            for item in self.rooms:
                room_data.append([
                    item.room_number,
                    item.room_name,
                    f"{item.area_m2:.2f}",
                    f"{item.volume_m3:.2f}",
                    str(item.max_occupancy),
                    Paragraph(item.floor_finish, styles['Small']),
                    Paragraph(item.wall_finish, styles['Small'])
                ])
            
            room_table = Table(room_data, colWidths=[15*mm, 50*mm, 25*mm, 30*mm, 25*mm, 45*mm, 45*mm])
            room_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.Color(1.0, 0.95, 0.9)),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(room_table)
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _create_mock_pdf(self, output_path: Path) -> Path:
        """Create placeholder when reportlab not available."""
        mock_path = output_path.with_suffix('.txt')
        content = f"""CONSTRUCTION SCHEDULES - {self.project_name}
{'='*60}

MATERIAL SCHEDULE:
- 3D Printed Earth Wall: {len(self.materials)} items
- Includes walls, floors, roof materials

DOOR/WINDOW SCHEDULE:
- {len(self.doors_windows)} openings specified
- U-values and dimensions included

ROOM SCHEDULE:
- {len(self.rooms)} rooms defined
- Areas, volumes, finishes listed

Note: Install reportlab for full PDF generation.
   pip install reportlab
"""
        with open(mock_path, 'w') as f:
            f.write(content)
        return mock_path


if __name__ == "__main__":
    print("Schedule Generator Test")
    
    geometry = {
        'type': 'single_pod',
        'diameter': 6.5,
        'height': 3.2
    }
    
    generator = ScheduleGenerator("Test Single Pod")
    generator.generate_from_geometry(geometry, 'single_pod')
    
    output_dir = Path(__file__).parent / 'outputs'
    
    csv_files = generator.export_csv(output_dir)
    print(f"CSV files: {csv_files}")
    
    pdf_file = generator.export_pdf(output_dir / 'schedules.pdf')
    print(f"PDF file: {pdf_file}")
