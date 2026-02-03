"""
harmonic-balance/docs_engine/pdf_drawings.py
Professional PDF drawing sets using ReportLab.
A1 sheet layout with architectural drafting standards.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from io import BytesIO

# Try to import reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A1, A2, A3, A4, landscape, portrait
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image, PageBreak, KeepTogether, Frame
    )
    from reportlab.graphics.shapes import (
        Drawing, Rect, Circle, Line, String, Polygon,
        Path as RLPath
    )
    from reportlab.graphics import renderPDF
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# Drawing sheet sizes in mm
SHEET_SIZES = {
    'A0': (841, 1189),
    'A1': (594, 841),
    'A2': (420, 594),
    'A3': (297, 420),
    'A4': (210, 297),
}


@dataclass
class DrawingSheet:
    """Drawing sheet configuration."""
    project_name: str
    drawing_title: str
    drawing_number: str
    scale: str
    date: str
    sheet_size: str = "A1"
    orientation: str = "portrait"  # or "landscape"
    revision: str = "A"
    drawn_by: str = "Harmonic Habitats"
    checked_by: str = ""


class PDFDrawingSet:
    """Generate professional PDF drawing sets."""
    
    def __init__(self, output_path: Path, sheet_size: str = "A1"):
        self.output_path = Path(output_path)
        self.sheet_size = sheet_size
        self.width, self.height = SHEET_SIZES[sheet_size]
        self.styles = self._setup_styles()
        
    def _setup_styles(self) -> Dict:
        """Setup paragraph styles for architectural drawings."""
        if not REPORTLAB_AVAILABLE:
            return {}
        
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='DrawingTitle',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Label style
        styles.add(ParagraphStyle(
            name='DrawingLabel',
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            alignment=TA_CENTER
        ))
        
        # Note style
        styles.add(ParagraphStyle(
            name='DrawingNote',
            fontName='Helvetica',
            fontSize=9,
            leading=11,
            alignment=TA_LEFT
        ))
        
        # Title block text
        styles.add(ParagraphStyle(
            name='TitleBlock',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            alignment=TA_LEFT
        ))
        
        return styles
    
    def generate_drawing_set(self, project_name: str, geometry: Dict,
                            output_dir: Path) -> Path:
        """
        Generate complete PDF drawing set.
        
        Includes: Site plan, Floor plan, 4 Elevations, 2 Sections, Detail sheet
        """
        if not REPORTLAB_AVAILABLE:
            return self._create_mock_pdf(output_dir / f"{project_name}_DRAWINGS.pdf")
        
        output_path = output_dir / f"{project_name}_DRAWING_SET.pdf"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=portrait(A3),  # A3 for individual sheets
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=30*mm  # Extra for title block
        )
        
        story = []
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Cover Sheet
        story.extend(self._create_cover_sheet(project_name, date_str))
        story.append(PageBreak())
        
        # Site Plan
        sheet = DrawingSheet(project_name, "SITE PLAN", "A-001", "1:200", date_str)
        story.extend(self._create_site_plan_page(geometry, sheet))
        story.append(PageBreak())
        
        # Floor Plan
        sheet = DrawingSheet(project_name, "FLOOR PLAN", "A-101", "1:50", date_str)
        story.extend(self._create_floor_plan_page(geometry, sheet))
        story.append(PageBreak())
        
        # Sections
        for i, section_name in enumerate(['SECTION A-A', 'SECTION B-B'], 1):
            sheet = DrawingSheet(project_name, section_name, f"A-20{i}", "1:50", date_str)
            story.extend(self._create_section_page(geometry, sheet, section_name))
            story.append(PageBreak())
        
        # Elevations
        for i, elev_name in enumerate(['NORTH', 'SOUTH', 'EAST', 'WEST'], 1):
            sheet = DrawingSheet(project_name, f"ELEVATION - {elev_name}", f"A-30{i}", "1:50", date_str)
            story.extend(self._create_elevation_page(geometry, sheet, elev_name))
            if i < 4:
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _create_cover_sheet(self, project_name: str, date_str: str) -> List:
        """Create cover sheet."""
        elements = []
        
        # Spacer at top
        elements.append(Spacer(1, 50*mm))
        
        # Project title
        elements.append(Paragraph(f"<b>{project_name}</b>", self.styles.get('Title', ParagraphStyle('Title'))))
        elements.append(Spacer(1, 20*mm))
        
        # Subtitle
        elements.append(Paragraph("ARCHITECTURAL DRAWING SET", self.styles.get('DrawingTitle', ParagraphStyle('Title'))))
        elements.append(Spacer(1, 40*mm))
        
        # Drawing list
        drawings = [
            ["Drawing No.", "Title", "Scale"],
            ["A-001", "Site Plan", "1:200"],
            ["A-101", "Floor Plan", "1:50"],
            ["A-201", "Section A-A", "1:50"],
            ["A-202", "Section B-B", "1:50"],
            ["A-301", "Elevation - North", "1:50"],
            ["A-302", "Elevation - South", "1:50"],
            ["A-303", "Elevation - East", "1:50"],
            ["A-304", "Elevation - West", "1:50"],
        ]
        
        table = Table(drawings, colWidths=[40*mm, 80*mm, 30*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(table)
        
        elements.append(Spacer(1, 40*mm))
        
        # Project info
        info = [
            ["Project:", project_name],
            ["Date:", date_str],
            ["Drawn by:", "Harmonic Habitats"],
            ["Software:", "Harmonic Balance v0.1.0"],
        ]
        
        info_table = Table(info, colWidths=[30*mm, 80*mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        
        return elements
    
    def _create_site_plan_page(self, geometry: Dict, sheet: DrawingSheet) -> List:
        """Create site plan page."""
        elements = []
        
        # Title
        elements.append(Paragraph(f"<b>{sheet.drawing_title}</b>", self.styles.get('DrawingTitle', ParagraphStyle('Title'))))
        elements.append(Spacer(1, 10*mm))
        
        # Drawing area with simple graphics
        drawing = Drawing(250*mm, 180*mm)
        
        # Site boundary (circle)
        site_radius = 100*mm
        site_circle = Circle(125*mm, 90*mm, site_radius)
        site_circle.fillColor = colors.Color(0.95, 0.95, 0.9)
        site_circle.strokeColor = colors.black
        site_circle.strokeWidth = 1
        drawing.add(site_circle)
        
        # Building outline based on typology
        if geometry['type'] == 'single_pod':
            # Single circle for pod
            building = Circle(125*mm, 90*mm, 25*mm)
            building.fillColor = colors.Color(0.8, 0.7, 0.6)
            building.strokeColor = colors.Color(0.5, 0.35, 0.17)
            building.strokeWidth = 2
            drawing.add(building)
            
        elif geometry['type'] == 'multi_pod_cluster':
            # Multiple circles
            for i in range(4):
                angle = i * math.pi / 2
                x = 125*mm + 40*mm * math.cos(angle)
                y = 90*mm + 40*mm * math.sin(angle)
                pod = Circle(x, y, 20*mm)
                pod.fillColor = colors.Color(0.8, 0.7, 0.6)
                pod.strokeColor = colors.Color(0.5, 0.35, 0.17)
                pod.strokeWidth = 2
                drawing.add(pod)
        
        # North arrow
        arrow_x, arrow_y = 200*mm, 160*mm
        drawing.add(Line(arrow_x, arrow_y, arrow_x, arrow_y + 15*mm, strokeWidth=2))
        drawing.add(String(arrow_x - 5*mm, arrow_y + 17*mm, 'N', fontName='Helvetica-Bold', fontSize=10))
        
        # Scale bar
        scale_y = 20*mm
        drawing.add(Line(20*mm, scale_y, 70*mm, scale_y, strokeWidth=2))
        drawing.add(Line(20*mm, scale_y - 2*mm, 20*mm, scale_y + 2*mm))
        drawing.add(Line(70*mm, scale_y - 2*mm, 70*mm, scale_y + 2*mm))
        drawing.add(String(40*mm, scale_y - 5*mm, '10m', fontSize=8, textAnchor='middle'))
        
        elements.append(drawing)
        elements.append(Spacer(1, 10*mm))
        
        # Notes
        elements.append(Paragraph("Notes: Site plan showing building location and access.", 
                                 self.styles.get('DrawingNote', ParagraphStyle('Note'))))
        
        # Title block
        elements.extend(self._create_title_block(sheet))
        
        return elements
    
    def _create_floor_plan_page(self, geometry: Dict, sheet: DrawingSheet) -> List:
        """Create floor plan page."""
        elements = []
        
        elements.append(Paragraph(f"<b>{sheet.drawing_title}</b>", self.styles.get('DrawingTitle', ParagraphStyle('Title'))))
        elements.append(Spacer(1, 10*mm))
        
        drawing = Drawing(250*mm, 180*mm)
        
        if geometry['type'] == 'single_pod':
            radius = 35*mm  # Scaled for drawing
            
            # Outer wall
            outer = Circle(125*mm, 90*mm, radius)
            outer.fillColor = None
            outer.strokeColor = colors.black
            outer.strokeWidth = 3
            drawing.add(outer)
            
            # Inner wall
            inner = Circle(125*mm, 90*mm, radius - 8*mm)
            inner.fillColor = None
            inner.strokeColor = colors.black
            inner.strokeWidth = 1
            drawing.add(inner)
            
            # Central core
            core = Circle(125*mm, 90*mm, 12*mm)
            core.fillColor = colors.Color(0.9, 0.9, 0.9)
            core.strokeColor = colors.black
            core.strokeWidth = 1
            drawing.add(core)
            
            # Room labels
            drawing.add(String(125*mm, 90*mm + radius - 15*mm, 'LIVING', 
                             fontSize=8, textAnchor='middle'))
            drawing.add(String(125*mm + radius - 15*mm, 90*mm, 'SLEEPING', 
                             fontSize=8, textAnchor='middle'))
            drawing.add(String(125*mm, 90*mm - radius + 10*mm, 'SERVICES', 
                             fontSize=8, textAnchor='middle'))
            
        elif geometry['type'] == 'organic_family':
            # Rectangular with rounded corners
            rect = Rect(75*mm, 50*mm, 100*mm, 80*mm, 5*mm, 5*mm)
            rect.fillColor = None
            rect.strokeColor = colors.black
            rect.strokeWidth = 3
            drawing.add(rect)
            
            # Room divisions
            drawing.add(Line(108*mm, 50*mm, 108*mm, 130*mm))
            drawing.add(Line(142*mm, 50*mm, 142*mm, 130*mm))
            
            # Labels
            drawing.add(String(91*mm, 90*mm, 'BEDROOM 1', fontSize=7, textAnchor='middle'))
            drawing.add(String(125*mm, 90*mm, 'LIVING', fontSize=7, textAnchor='middle'))
            drawing.add(String(159*mm, 90*mm, 'BEDROOM 2', fontSize=7, textAnchor='middle'))
        
        # Dimensions
        dim_y = 145*mm
        drawing.add(Line(90*mm, dim_y, 160*mm, dim_y))
        drawing.add(Line(90*mm, dim_y - 2*mm, 90*mm, dim_y + 2*mm))
        drawing.add(Line(160*mm, dim_y - 2*mm, 160*mm, dim_y + 2*mm))
        
        if geometry['type'] == 'single_pod':
            dia = geometry.get('diameter', 6.5)
            drawing.add(String(125*mm, dim_y + 5*mm, f'Ø{dia}m', 
                             fontSize=8, textAnchor='middle'))
        
        elements.append(drawing)
        elements.append(Spacer(1, 10*mm))
        
        # Legend
        legend_data = [
            ['Symbol', 'Description'],
            ['━━━', 'Wall (300mm)'],
            ['---', 'Door opening'],
            ['▭', 'Window'],
        ]
        legend = Table(legend_data, colWidths=[20*mm, 60*mm])
        legend.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(legend)
        
        elements.extend(self._create_title_block(sheet))
        
        return elements
    
    def _create_section_page(self, geometry: Dict, sheet: DrawingSheet, 
                            section_name: str) -> List:
        """Create section drawing page."""
        elements = []
        
        elements.append(Paragraph(f"<b>{sheet.drawing_title}</b>", self.styles.get('DrawingTitle', ParagraphStyle('Title'))))
        elements.append(Spacer(1, 10*mm))
        
        drawing = Drawing(250*mm, 180*mm)
        
        # Ground line
        ground_y = 40*mm
        drawing.add(Line(30*mm, ground_y, 220*mm, ground_y, 
                        strokeWidth=1, strokeDashArray=[2, 2]))
        
        if geometry['type'] == 'single_pod':
            width = 70*mm
            height = 64*mm  # 3.2m scaled
            
            # Wall section
            wall = Rect(90*mm, ground_y, width, height)
            wall.fillColor = colors.Color(0.85, 0.75, 0.65)
            wall.strokeColor = colors.black
            wall.strokeWidth = 2
            drawing.add(wall)
            
            # Ceiling line
            drawing.add(Line(85*mm, ground_y + height, 165*mm, ground_y + height, 
                           strokeWidth=2))
            
            # Height dimension
            drawing.add(Line(170*mm, ground_y, 170*mm, ground_y + height))
            drawing.add(Line(168*mm, ground_y, 172*mm, ground_y))
            drawing.add(Line(168*mm, ground_y + height, 172*mm, ground_y + height))
            drawing.add(String(175*mm, ground_y + height/2, '3.2m', 
                             fontSize=8, textAnchor='start'))
            
            # Floor thickness
            drawing.add(Rect(85*mm, ground_y - 8*mm, 80*mm, 8*mm, 
                           fillColor=colors.Color(0.7, 0.7, 0.7)))
        
        elements.append(drawing)
        elements.append(Spacer(1, 10*mm))
        
        # Section notes
        elements.append(Paragraph("Section cut through center of dwelling. Wall construction: 300mm 3D printed earth.",
                                 self.styles.get('DrawingNote', ParagraphStyle('Note'))))
        
        elements.extend(self._create_title_block(sheet))
        
        return elements
    
    def _create_elevation_page(self, geometry: Dict, sheet: DrawingSheet,
                              elev_name: str) -> List:
        """Create elevation drawing page."""
        elements = []
        
        elements.append(Paragraph(f"<b>{sheet.drawing_title}</b>", self.styles.get('DrawingTitle', ParagraphStyle('Title'))))
        elements.append(Spacer(1, 10*mm))
        
        drawing = Drawing(250*mm, 180*mm)
        
        # Ground line
        ground_y = 40*mm
        drawing.add(Line(30*mm, ground_y, 220*mm, ground_y, strokeWidth=1))
        
        if geometry['type'] == 'single_pod':
            width = 70*mm
            height = 64*mm
            x_center = 125*mm
            
            # Building outline (simplified as rect for elevation)
            outline = Rect(x_center - width/2, ground_y, width, height)
            outline.fillColor = None
            outline.strokeColor = colors.black
            outline.strokeWidth = 2
            drawing.add(outline)
            
            # Window
            win_width = 16*mm
            win_height = 24*mm
            win_x = x_center - win_width/2
            win_y = ground_y + 24*mm
            
            window = Rect(win_x, win_y, win_width, win_height)
            window.fillColor = colors.Color(0.9, 0.95, 1.0)
            window.strokeColor = colors.black
            window.strokeWidth = 1
            drawing.add(window)
            
            # Window divisions
            drawing.add(Line(win_x, win_y + win_height/2, win_x + win_width, win_y + win_height/2))
            drawing.add(Line(win_x + win_width/2, win_y, win_x + win_width/2, win_y + win_height))
            
            # Elevation label
            drawing.add(String(x_center, ground_y + height + 10*mm, elev_name, 
                             fontSize=10, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Material legend
        legend_y = 10*mm
        drawing.add(String(30*mm, legend_y, 'Materials:', fontSize=8, fontName='Helvetica-Bold'))
        drawing.add(String(30*mm, legend_y - 5*mm, 'Wall: 3D printed earth', fontSize=7))
        drawing.add(String(30*mm, legend_y - 10*mm, 'Window: Double glazing', fontSize=7))
        
        elements.append(drawing)
        elements.extend(self._create_title_block(sheet))
        
        return elements
    
    def _create_title_block(self, sheet: DrawingSheet) -> List:
        """Create title block at bottom of page."""
        elements = []
        
        # Title block table
        data = [
            [sheet.project_name, f"SCALE: {sheet.scale}", f"DATE: {sheet.date}"],
            [sheet.drawing_title, f"DRAWING: {sheet.drawing_number}", f"REV: {sheet.revision}"],
            [f"Drawn by: {sheet.drawn_by}", '', f"Checked by: {sheet.checked_by}"],
        ]
        
        table = Table(data, colWidths=[80*mm, 60*mm, 60*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 2), (-1, 2), colors.Color(0.95, 0.95, 0.95)),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(Spacer(1, 10*mm))
        elements.append(table)
        
        return elements
    
    def _create_mock_pdf(self, output_path: Path) -> Path:
        """Create placeholder PDF when reportlab not available."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""HARMONIC HABITATS - DRAWING SET
================================

Project: {self.project_name}
Generated: {datetime.now().strftime('%Y-%m-%d')}

This is a placeholder PDF.
Install reportlab for full PDF generation:
    pip install reportlab

Drawing Set Includes:
- A-001: Site Plan (1:200)
- A-101: Floor Plan (1:50)
- A-201: Section A-A (1:50)
- A-202: Section B-B (1:50)
- A-301: Elevation - North (1:50)
- A-302: Elevation - South (1:50)
- A-303: Elevation - East (1:50)
- A-304: Elevation - West (1:50)

Note: Full PDF generation requires ReportLab library.
"""
        with open(output_path.with_suffix('.txt'), 'w') as f:
            f.write(content)
        
        return output_path.with_suffix('.txt')


if __name__ == "__main__":
    print("PDF Drawing Set Generator")
    
    geometry = {
        'type': 'single_pod',
        'diameter': 6.5,
        'height': 3.2
    }
    
    output_dir = Path(__file__).parent / 'outputs'
    pdf_gen = PDFDrawingSet(output_dir / 'test.pdf')
    result = pdf_gen.generate_drawing_set("Test Project", geometry, output_dir)
    
    print(f"Generated: {result}")
