"""
harmonic-balance/docs_engine/energy_report.py
Energy performance calculations and reports.
Thermal envelope, heating/cooling loads, nZEB compliance, APE format.
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Try to import reportlab for PDF
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@dataclass
class ThermalElement:
    """Thermal building element."""
    name: str
    area_m2: float
    u_value: float  # W/m²K
    orientation: str = ""


@dataclass
class ClimateData:
    """Climate data for location."""
    location: str
    heating_degree_days: int
    design_temp_outdoor: float  # °C
    design_temp_indoor: float  # °C
    solar_radiation_wh_m2: float  # Annual


class EnergyCalculator:
    """
    Energy performance calculator for 3D printed earth buildings.
    Based on EN ISO 6946 (U-values), EN 12831 (heating load), EPBD/nZEB.
    """
    
    # Reference values
    VENTILATION_RATE = 0.5  # ACH (air changes per hour)
    INTERNAL_HEAT_GAIN_W_M2 = 4.0  # W/m²
    SOLAR_GAIN_FACTOR = 0.5
    
    def __init__(self, project_name: str, climate: ClimateData):
        self.project_name = project_name
        self.climate = climate
        self.elements: List[ThermalElement] = []
        self.volume_m3 = 0
        self.floor_area_m2 = 0
        
    def add_envelope_element(self, element: ThermalElement):
        """Add thermal envelope element."""
        self.elements.append(element)
    
    def calculate_u_value_earth_wall(self, thickness_m: float = 0.30,
                                     lambda_earth: float = 0.8) -> float:
        """
        Calculate U-value for earth wall per EN ISO 6946.
        
        U = 1 / (Rsi + d/λ + Rse)
        
        Args:
            thickness_m: Wall thickness in meters
            lambda_earth: Thermal conductivity of earth (W/mK)
        
        Returns:
            U-value in W/m²K
        """
        Rsi = 0.13  # Internal surface resistance (m²K/W)
        Rse = 0.04  # External surface resistance (m²K/W)
        
        R_wall = thickness_m / lambda_earth
        R_total = Rsi + R_wall + Rse
        
        U_value = 1 / R_total
        return U_value
    
    def calculate_thermal_bridges(self, element_area_m2: float) -> float:
        """
        Calculate thermal bridge addition.
        
        Returns psi-value addition for earth construction.
        """
        # Simplified: add 10% for thermal bridges
        return element_area_m2 * 0.10
    
    def calculate_heat_loss_coefficient(self) -> Dict:
        """
        Calculate building heat loss coefficient (H).
        
        H = Ht + Hv + Hu
        Ht = transmission losses
        Hv = ventilation losses
        Hu = thermal bridges
        """
        # Transmission losses through envelope
        Ht = 0
        element_details = []
        
        for elem in self.elements:
            loss = elem.area_m2 * elem.u_value
            Ht += loss
            element_details.append({
                'name': elem.name,
                'area': elem.area_m2,
                'u_value': elem.u_value,
                'loss': loss
            })
        
        # Thermal bridges (10% addition)
        Hu = Ht * 0.10
        
        # Ventilation losses
        # Hv = ρ * cp * n * V / 3600
        rho = 1.2  # kg/m³ (air density)
        cp = 1000  # J/kgK (specific heat)
        n = self.VENTILATION_RATE  # ACH
        V = self.volume_m3
        
        Hv = rho * cp * n * V / 3600  # W/K
        
        H_total = Ht + Hv + Hu
        
        return {
            'transmission_losses_Ht': round(Ht, 2),
            'ventilation_losses_Hv': round(Hv, 2),
            'thermal_bridges_Hu': round(Hu, 2),
            'total_heat_loss_H': round(H_total, 2),
            'elements': element_details
        }
    
    def calculate_heating_load(self) -> Dict:
        """
        Calculate heating load per EN 12831.
        
        Qh = H * (Ti - Te) - gains
        """
        heat_loss = self.calculate_heat_loss_coefficient()
        H = heat_loss['total_heat_loss_H']
        
        # Temperature difference
        delta_T = self.climate.design_temp_indoor - self.climate.design_temp_outdoor
        
        # Heat demand
        Q_heating = H * delta_T
        
        # Internal gains
        Q_internal = self.INTERNAL_HEAT_GAIN_W_M2 * self.floor_area_m2
        
        # Solar gains (simplified)
        window_area = sum(e.area_m2 for e in self.elements if 'window' in e.name.lower())
        Q_solar = (window_area * self.climate.solar_radiation_wh_m2 / 8760 * 
                  self.SOLAR_GAIN_FACTOR)
        
        # Net heating load
        Q_net = Q_heating - Q_internal - Q_solar
        Q_net = max(Q_net, 0)  # Can't be negative
        
        # Specific heat load per m²
        q_spec = Q_net / self.floor_area_m2 if self.floor_area_m2 > 0 else 0
        
        return {
            'heat_loss_coefficient': round(H, 2),
            'temperature_difference_k': delta_T,
            'gross_heat_demand_w': round(Q_heating, 2),
            'internal_gains_w': round(Q_internal, 2),
            'solar_gains_w': round(Q_solar, 2),
            'net_heating_load_w': round(Q_net, 2),
            'specific_heat_load_w_m2': round(q_spec, 2)
        }
    
    def calculate_annual_energy_demand(self) -> Dict:
        """
        Calculate annual primary energy demand.
        
        Q_annual = H * HDD * 24 / 1000 (kWh/a)
        """
        heat_loss = self.calculate_heat_loss_coefficient()
        H = heat_loss['total_heat_loss_H']
        
        # Heating energy
        Q_heating_kwh = H * self.climate.heating_degree_days * 24 / 1000
        
        # Domestic hot water (simplified: 25 kWh/m²a)
        Q_dhw_kwh = 25 * self.floor_area_m2
        
        # Auxiliary energy (pumps, fans): 5% of heating
        Q_aux_kwh = Q_heating_kwh * 0.05
        
        # Total delivered energy
        Q_delivered = Q_heating_kwh + Q_dhw_kwh + Q_aux_kwh
        
        # Primary energy factor (electricity: 2.5, biomass: 0.2)
        primary_energy_factor = 0.5  # Assuming biomass heating
        
        Q_primary = Q_delivered * primary_energy_factor
        
        # Specific primary energy
        q_primary = Q_primary / self.floor_area_m2 if self.floor_area_m2 > 0 else 0
        
        return {
            'space_heating_kwh_a': round(Q_heating_kwh, 2),
            'domestic_hot_water_kwh_a': round(Q_dhw_kwh, 2),
            'auxiliary_kwh_a': round(Q_aux_kwh, 2),
            'total_delivered_kwh_a': round(Q_delivered, 2),
            'primary_energy_factor': primary_energy_factor,
            'primary_energy_kwh_a': round(Q_primary, 2),
            'specific_primary_energy_kwh_m2a': round(q_primary, 2)
        }
    
    def check_nzeb_compliance(self) -> Dict:
        """
        Check Nearly Zero Energy Building compliance.
        
        Italy nZEB requirements (Climate Zone D):
        - Specific primary energy: ≤ 50 kWh/m²a
        """
        energy = self.calculate_annual_energy_demand()
        q_primary = energy['specific_primary_energy_kwh_m2a']
        
        # Italy limits by climate zone
        limits = {
            'A': 35, 'B': 40, 'C': 45, 'D': 50,
            'E': 55, 'F': 60
        }
        
        zone = 'D'  # Default to central Italy
        limit = limits.get(zone, 50)
        
        compliant = q_primary <= limit
        margin = ((limit - q_primary) / limit * 100) if limit > 0 else 0
        
        return {
            'climate_zone': zone,
            'specific_primary_energy': round(q_primary, 2),
            'limit_kwh_m2a': limit,
            'compliant': compliant,
            'margin_percent': round(margin, 1),
            'status': 'PASS' if compliant else 'FAIL'
        }
    
    def generate_ape_document(self, output_path: Path) -> Path:
        """
        Generate Attestato di Prestazione Energetica (APE) for Italy.
        
        APE is the Italian Energy Performance Certificate.
        """
        if not REPORTLAB_AVAILABLE:
            return self._create_mock_ape(output_path)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        title_style = ParagraphStyle(
            'APE_Title',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=1,  # Center
            spaceAfter=12
        )
        
        story.append(Paragraph("ATTESTATO DI PRESTAZIONE ENERGETICA (APE)", title_style))
        story.append(Paragraph(f"<b>{self.project_name}</b>", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Building info
        story.append(Paragraph("<b>Dati dell'edificio</b>", styles['Heading3']))
        info_data = [
            ['Parametro', 'Valore'],
            ['Località', self.climate.location],
            ['Superficie utile', f'{self.floor_area_m2:.1f} m²'],
            ['Volume', f'{self.volume_m3:.1f} m³'],
            ['Zona climatica', 'D'],
        ]
        info_table = Table(info_data, colWidths=[70*mm, 70*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Energy performance
        energy = self.calculate_annual_energy_demand()
        nzeb = self.check_nzeb_compliance()
        
        story.append(Paragraph("<b>Prestazione energetica</b>", styles['Heading3']))
        perf_data = [
            ['Indicatore', 'Valore', 'Unità'],
            ['Energia primaria', f"{energy['specific_primary_energy_kwh_m2a']:.1f}", 'kWh/m² anno'],
            ['Limite nZEB', f"{nzeb['limit_kwh_m2a']}", 'kWh/m² anno'],
            ['Stato', nzeb['status'], ''],
        ]
        perf_table = Table(perf_data, colWidths=[60*mm, 40*mm, 40*mm])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), 
             colors.lightgreen if nzeb['compliant'] else colors.lightcoral),
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 20))
        
        # Thermal envelope
        story.append(Paragraph("<b>Involucro termico</b>", styles['Heading3']))
        env_data = [['Elemento', 'Area (m²)', 'U-value (W/m²K)']]
        for elem in self.elements:
            env_data.append([elem.name, f"{elem.area_m2:.1f}", f"{elem.u_value:.2f}"])
        
        env_table = Table(env_data, colWidths=[70*mm, 40*mm, 50*mm])
        env_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        story.append(env_table)
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _create_mock_ape(self, output_path: Path) -> Path:
        """Create placeholder APE when reportlab not available."""
        mock_path = output_path.with_suffix('.txt')
        
        energy = self.calculate_annual_energy_demand()
        nzeb = self.check_nzeb_compliance()
        
        content = f"""ATTESTATO DI PRESTAZIONE ENERGETICA (APE)
========================================

Progetto: {self.project_name}
Località: {self.climate.location}
Data: {datetime.now().strftime('%Y-%m-%d')}

DATI EDIFICIO:
- Superficie: {self.floor_area_m2:.1f} m²
- Volume: {self.volume_m3:.1f} m³
- Zona climatica: D

PRESTAZIONE ENERGETICA:
- Energia primaria: {energy['specific_primary_energy_kwh_m2a']:.1f} kWh/m² anno
- Limite nZEB: {nzeb['limit_kwh_m2a']} kWh/m² anno
- Stato: {nzeb['status']}

INVOLUCRO TERMICO:
{chr(10).join(f"- {e.name}: A={e.area_m2:.1f}m², U={e.u_value:.2f}W/m²K" for e in self.elements)}

Note: Per il certificato ufficiale APE, installare ReportLab.
"""
        with open(mock_path, 'w') as f:
            f.write(content)
        
        return mock_path


def generate_energy_report_for_typology(typology: str, geometry: Dict,
                                        output_dir: Path) -> Dict[str, Path]:
    """
    Generate complete energy report for a typology.
    
    Returns dict of generated file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Climate data for Italy (central)
    climate = ClimateData(
        location="Central Italy",
        heating_degree_days=2200,
        design_temp_outdoor=-5.0,
        design_temp_indoor=20.0,
        solar_radiation_wh_m2=1200000
    )
    
    calc = EnergyCalculator(f"{typology.title()} Energy Analysis", climate)
    
    # Add elements based on typology
    if typology == 'single_pod':
        diameter = geometry.get('diameter', 6.5)
        height = 3.2
        radius = diameter / 2
        
        calc.floor_area_m2 = math.pi * (radius - 0.3)**2
        calc.volume_m3 = calc.floor_area_m2 * height
        
        # Wall U-value
        u_wall = calc.calculate_u_value_earth_wall(0.30, 0.8)
        wall_area = 2 * math.pi * radius * height
        
        calc.add_envelope_element(ThermalElement("Wall", wall_area, u_wall, ""))
        calc.add_envelope_element(ThermalElement("Floor", calc.floor_area_m2, 0.35, ""))
        calc.add_envelope_element(ThermalElement("Roof", calc.floor_area_m2, 0.30, ""))
        calc.add_envelope_element(ThermalElement("Window", 2.0, 1.2, "North"))
        
    elif typology == 'organic_family':
        length = geometry.get('length', 15.0)
        width = geometry.get('width', 5.6)
        levels = geometry.get('levels', 2)
        
        calc.floor_area_m2 = length * width * levels
        calc.volume_m3 = length * width * 2.8 * levels
        
        wall_perimeter = 2 * (length + width)
        wall_area = wall_perimeter * 2.8 * levels
        
        u_wall = calc.calculate_u_value_earth_wall(0.35, 0.8)
        
        calc.add_envelope_element(ThermalElement("Wall", wall_area, u_wall, ""))
        calc.add_envelope_element(ThermalElement("Floor", length * width, 0.35, ""))
        calc.add_envelope_element(ThermalElement("Roof", length * width * 1.2, 0.30, ""))
        calc.add_envelope_element(ThermalElement("Window", 12.0, 1.2, "Various"))
    
    # Generate reports
    results = {}
    
    # APE document
    results['ape'] = calc.generate_ape_document(output_dir / 'energy_certificate_ape.pdf')
    
    return results


if __name__ == "__main__":
    print("Energy Report Test")
    
    geometry = {
        'type': 'single_pod',
        'diameter': 6.5,
        'height': 3.2
    }
    
    output_dir = Path(__file__).parent / 'outputs'
    results = generate_energy_report_for_typology('single_pod', geometry, output_dir)
    
    print(f"Generated: {results}")
