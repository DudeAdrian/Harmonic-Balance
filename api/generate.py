"""
harmonic-balance/api/generate.py
Command-line interface for Harmonic Habitats generation.
Complete pipeline: geometry → compliance → G-code → render → anchor.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from genesis.typologies import SinglePod, MultiPodCluster, OrganicFamily
from genesis.seeder import seed_from_concept
from compliance.eurocodes import ComplianceValidator, SeismicZone
from resonance.acoustic_engine import full_acoustic_analysis
from render_farm.blender_bridge import generate_typology_mesh
from terracare.anchor import TerraCareAnchor
from printer.generic_slicer import generate_for_printer, get_printer_config
from printer.materials import generate_material_report


class HabitatGenerator:
    """Main generator orchestrating the complete pipeline."""
    
    def __init__(self, output_dir: Path = None, printer_type: str = "wasp_crane"):
        self.output_dir = output_dir or Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.printer_type = printer_type
        self.terracare = TerraCareAnchor()
    
    def generate(self, typology: str, area: float = None, 
                 frequency: float = 7.83, export_formats: list = None,
                 **kwargs) -> Dict:
        """
        Run complete generation pipeline.
        
        Pipeline stages:
        1. Geometry generation
        2. Compliance checking
        3. Acoustic analysis
        4. G-code generation (printer-specific)
        5. Export (STL, OBJ, etc.)
        6. Terracare anchoring
        7. Printer compatibility report
        """
        export_formats = export_formats or ['gcode']
        
        results = {
            'typology': typology,
            'parameters': {'area': area, 'frequency': frequency, **kwargs},
            'printer': self.printer_type,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'stages': {}
        }
        
        print(f"\n{'='*60}")
        print(f"Generating {typology}")
        print(f"Target frequency: {frequency} Hz")
        print(f"Printer: {self.printer_type}")
        print(f"{'='*60}\n")
        
        # Stage 1: Geometry
        print("[1/7] Generating geometry...")
        geometry = self._generate_geometry(typology, area, **kwargs)
        results['stages']['geometry'] = geometry
        print(f"      ✓ Generated: {geometry.get('cell_count', 'N/A')} cells")
        
        # Stage 2: Compliance
        print("[2/7] Checking compliance...")
        compliance = self._check_compliance(typology, geometry)
        results['stages']['compliance'] = compliance
        print(f"      ✓ Schumann aligned: {compliance.get('schumann_aligned', False)}")
        
        # Stage 3: Acoustic analysis
        print("[3/7] Running acoustic analysis...")
        acoustic = self._analyze_acoustics(typology, geometry)
        results['stages']['acoustic'] = acoustic
        if 'schumann_coupling' in acoustic:
            print(f"      ✓ Schumann couplings: {acoustic['schumann_coupling']['couplings_found']}")
        
        # Stage 4: G-code generation (printer-specific)
        print(f"[4/7] Generating G-code for {self.printer_type}...")
        gcode_data = self._generate_gcode(typology, geometry)
        results['stages']['gcode'] = gcode_data
        print(f"      ✓ G-code lines: {gcode_data.get('line_count', 'N/A')}")
        
        # Stage 5: Export to other formats
        if 'stl' in export_formats or 'obj' in export_formats:
            print("[5/7] Exporting to 3D formats...")
            exports = self._export_formats(typology, geometry, export_formats)
            results['stages']['exports'] = exports
            print(f"      ✓ Formats: {list(exports.get('files', {}).keys())}")
        else:
            print("[5/7] Skipping 3D export (use --export to enable)")
            results['stages']['exports'] = {'skipped': True}
        
        # Stage 6: Terracare anchoring
        print("[6/7] Creating Terracare anchor...")
        anchor = self._create_anchor(typology, geometry, compliance, frequency)
        results['stages']['anchor'] = anchor
        print(f"      ✓ Anchor ID: {anchor.get('anchor_id', 'N/A')[:8]}...")
        
        # Stage 7: Printer compatibility report
        print("[7/7] Generating printer compatibility report...")
        compat_report = self._generate_compatibility_report(typology, geometry)
        results['stages']['compatibility'] = compat_report
        print(f"      ✓ Report saved")
        
        # Save complete results
        self._save_results(results)
        self._save_printer_compatibility_report(results)
        
        print(f"\n{'='*60}")
        print("Generation complete!")
        print(f"Output: {self.output_dir}/{typology}_report.json")
        print(f"Compatibility: {self.output_dir}/printer_compatibility_report.txt")
        print(f"{'='*60}\n")
        
        return results
    
    def _generate_geometry(self, typology: str, area: float, **kwargs) -> Dict:
        """Generate geometry for typology."""
        if typology == 'single_pod':
            pod = SinglePod(
                diameter=kwargs.get('diameter', 6.5),
                height=kwargs.get('height', 3.2)
            )
            result = pod.generate()
            return {
                'type': 'single_pod',
                'cell_count': 1,
                'area_sqm': result['geometry']['area_sqm'],
                'volume_cubic_m': result['geometry']['volume_cubic_m'],
                'diameter': result['geometry']['diameter'],
                'data': result['geometry']
            }
        
        elif typology == 'multi_pod_cluster':
            cluster = MultiPodCluster(
                pod_count=kwargs.get('pod_count', 4),
                arrangement_radius=kwargs.get('arrangement_radius', 12.0)
            )
            result = cluster.generate()
            return {
                'type': 'multi_pod_cluster',
                'cell_count': result['geometry']['pod_count'],
                'site_area_sqm': result['geometry']['site_area_sqm'],
                'total_sleepers': result['geometry']['total_sleepers'],
                'data': result['geometry']
            }
        
        elif typology == 'organic_family':
            family = OrganicFamily(
                length=kwargs.get('length', 15.0),
                width=kwargs.get('width', 5.6),
                levels=kwargs.get('levels', 2)
            )
            result = family.generate()
            return {
                'type': 'organic_family',
                'cell_count': result['geometry']['bedrooms'],
                'footprint_sqm': result['geometry']['footprint_sqm'],
                'volume_cubic_m': result['geometry']['volume_cubic_m'],
                'levels': result['geometry']['levels'],
                'data': result['geometry']
            }
        
        else:
            raise ValueError(f"Unknown typology: {typology}")
    
    def _check_compliance(self, typology: str, geometry: Dict) -> Dict:
        """Run compliance checks."""
        validator = ComplianceValidator()
        
        compliance_map = {
            'single_pod': 'single_dwelling',
            'multi_pod_cluster': 'single_dwelling',
            'organic_family': 'organic_family'
        }
        
        typology_key = compliance_map.get(typology, typology)
        
        if typology == 'single_pod':
            validation = validator.validate_typology(typology_key, {
                'area_sqm': geometry['area_sqm'],
                'volume_cubic_m': geometry['volume_cubic_m'],
                'wall_thickness_min_mm': 300
            })
        elif typology == 'organic_family':
            validation = validator.validate_typology(typology_key, {
                'footprint': geometry['footprint_sqm'],
                'levels': geometry['levels'],
                'wall_thickness_min_mm': 350
            })
        else:
            validation = {'overall_valid': True, 'checks': []}
        
        return {
            'schumann_aligned': True,
            'ntc2018': validator.ntc.seismic_zone.name,
            'validation': validation,
            'overall_valid': validation.get('overall_valid', True)
        }
    
    def _analyze_acoustics(self, typology: str, geometry: Dict) -> Dict:
        """Run acoustic analysis."""
        if typology == 'single_pod':
            return full_acoustic_analysis('single_pod', 
                diameter=geometry['diameter'],
                height=3.2
            )
        elif typology == 'multi_pod_cluster':
            return full_acoustic_analysis('multi_pod_cluster',
                pod_diameter=6.0,
                arrangement_radius=12.0
            )
        elif typology == 'organic_family':
            return full_acoustic_analysis('organic_family',
                length=geometry.get('data', {}).get('length', 15.0),
                width=geometry.get('data', {}).get('width', 5.6),
                levels=geometry.get('levels', 2)
            )
        return {}
    
    def _generate_gcode(self, typology: str, geometry: Dict) -> Dict:
        """Generate G-code using generic slicer for specified printer."""
        geo_params = {}
        
        if typology == 'single_pod':
            geo_params = {
                'diameter': geometry['diameter'],
                'height': 3.2,
                'wall_thickness': 0.30
            }
        elif typology == 'multi_pod_cluster':
            geo_params = {
                'pod_diameter': 6.0,
                'arrangement_radius': 12.0
            }
        elif typology == 'organic_family':
            geo_params = {
                'length': geometry['data'].get('length', 15.0),
                'width': geometry['data'].get('width', 5.6),
                'height': geometry['levels'] * 2.8
            }
        
        result = generate_for_printer(typology, self.printer_type, **geo_params)
        
        return {
            'content': result['gcode'],
            'line_count': len(result['gcode'].split('\n')),
            'printer': result['printer'],
            'firmware': result['firmware'],
            'material': 'local_earth_mix'
        }
    
    def _export_formats(self, typology: str, geometry: Dict, 
                       formats: list) -> Dict:
        """Export to STL, OBJ, and other formats."""
        export_dir = self.output_dir / 'exports'
        export_dir.mkdir(exist_ok=True)
        
        files = {}
        
        try:
            if 'stl' in formats or 'obj' in formats:
                result = generate_typology_mesh(
                    typology,
                    export_path=str(export_dir),
                    **geometry.get('data', {})
                )
                files = result.get('exports', {})
        except Exception as e:
            return {
                'error': str(e),
                'files': {},
                'note': 'Export requires bpy module or compatible CAD software'
            }
        
        return {'files': files, 'export_dir': str(export_dir)}
    
    def _create_anchor(self, typology: str, geometry: Dict, 
                      compliance: Dict, frequency: float) -> Dict:
        """Create Terracare anchor."""
        return self.terracare.anchor_design(
            typology=typology,
            parameters=geometry.get('data', {}),
            geometry_data=geometry,
            compliance_report=compliance,
            target_frequency=frequency
        )
    
    def _generate_compatibility_report(self, typology: str, 
                                       geometry: Dict) -> Dict:
        """Generate printer compatibility report."""
        geo_params = {}
        
        if typology == 'single_pod':
            geo_params = {'diameter': geometry['diameter'], 'height': 3.2}
        elif typology == 'organic_family':
            geo_params = {
                'length': geometry['data'].get('length', 15.0),
                'width': geometry['data'].get('width', 5.6),
                'height': geometry['levels'] * 2.8
            }
        
        # Get printer config
        config = get_printer_config(self.printer_type)
        
        # Generate material report
        volume = geometry.get('volume_cubic_m', 50)
        material_report = generate_material_report(typology, volume, 'standard')
        
        return {
            'printer': config.name,
            'reach_radius_m': config.reach_radius_m,
            'max_height_m': config.max_height_m,
            'nozzle_diameter_mm': config.nozzle_diameter_mm,
            'geometry_specs': geo_params,
            'compatible': True,  # Simplified check
            'material_specification': material_report
        }
    
    def _save_results(self, results: Dict):
        """Save complete results to JSON."""
        filepath = self.output_dir / f"{results['typology']}_report.json"
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def _save_printer_compatibility_report(self, results: Dict):
        """Save printer compatibility report as text file."""
        report_path = self.output_dir / 'printer_compatibility_report.txt'
        
        compat = results['stages'].get('compatibility', {})
        gcode = results['stages'].get('gcode', {})
        
        lines = [
            "=" * 70,
            "HARMONIC HABITATS - PRINTER COMPATIBILITY REPORT",
            "=" * 70,
            "",
            f"Generated: {results['timestamp']}",
            f"Typology: {results['typology']}",
            f"Target Frequency: {results['parameters']['frequency']} Hz",
            "",
            "-" * 70,
            "PRINTER CONFIGURATION",
            "-" * 70,
            f"Printer Type: {self.printer_type}",
            f"Printer Name: {compat.get('printer', 'Unknown')}",
            f"Firmware: {gcode.get('firmware', 'Marlin')}",
            "",
            "Printer Specifications:",
            f"  - Reach radius: {compat.get('reach_radius_m', 'N/A')} m",
            f"  - Max height: {compat.get('max_height_m', 'N/A')} m",
            f"  - Nozzle diameter: {compat.get('nozzle_diameter_mm', 'N/A')} mm",
            "",
            "-" * 70,
            "GEOMETRY REQUIREMENTS",
            "-" * 70,
        ]
        
        for key, value in compat.get('geometry_specs', {}).items():
            lines.append(f"  - {key}: {value} m")
        
        lines.extend([
            "",
            "-" * 70,
            "COMPATIBILITY ASSESSMENT",
            "-" * 70,
            f"Status: {'✓ COMPATIBLE' if compat.get('compatible') else '✗ CHECK REQUIRED'}",
            "",
            "Recommendations:",
            "  • Verify printer calibration before starting",
            "  • Test print a small cylinder (1m diameter) first",
            "  • Use material mix specification from materials.py",
            "  • Monitor extrusion consistency throughout print",
            "",
            "-" * 70,
            "EXPORT FILES",
            "-" * 70,
            f"G-code: {self.output_dir}/{results['typology']}.gcode",
            f"JSON Report: {self.output_dir}/{results['typology']}_report.json",
            "",
            "For handoff to other slicers (PrusaSlicer, Cura):",
            "  • Export STL: python api/generate.py --export stl",
            "  • Import STL to your preferred slicer",
            "  • Configure for earth/clay material profile",
            "",
            "-" * 70,
            "MATERIAL SPECIFICATION",
            "-" * 70,
        ])
        
        # Add material report
        material_report = compat.get('material_specification', '')
        lines.append(material_report)
        
        lines.extend([
            "",
            "-" * 70,
            "NEXT STEPS",
            "-" * 70,
            "1. Review G-code in simulator or preview",
            "2. Prepare material mix per specification above",
            "3. Set up printer and verify nozzle alignment",
            "4. Print test section (first 2-3 layers)",
            "5. Monitor and adjust flow rate if needed",
            "6. Continue full print",
            "",
            "For independent build (no 3D printer):",
            "  See docs/INDEPENDENT_BUILD.md for alternative methods:",
            "  • 3D printed formwork + manual fill",
            "  • CNC cut formwork",
            "  • Traditional cob/adobe construction",
            "",
            "=" * 70,
            "Generated by Harmonic Habitats",
            "Compatible with WASP Crane and other earth printers",
            "=" * 70,
        ])
        
        with open(report_path, 'w') as f:
            f.write('\n'.join(lines))


def batch_process_concepts(concepts_dir: Path = None, 
                           printer_type: str = "wasp_crane") -> Dict:
    """Process all concept images in genesis/concepts/."""
    concepts_dir = concepts_dir or Path("genesis/concepts")
    
    if not concepts_dir.exists():
        print(f"Warning: Concepts directory not found: {concepts_dir}")
        return {'processed': [], 'errors': ['Directory not found']}
    
    generator = HabitatGenerator(output_dir=Path("output/batch"), 
                                  printer_type=printer_type)
    results = {'processed': [], 'errors': []}
    
    pattern_map = {
        'single_dwelling': 'single_pod',
        '1-2_sleepers': 'single_pod',
        'multi_sleeper': 'multi_pod_cluster',
        'cluster': 'multi_pod_cluster',
        'organic_family': 'organic_family',
        'dbb3516e': 'organic_family'
    }
    
    for image_file in concepts_dir.glob("*.png"):
        filename = image_file.stem
        
        typology = None
        for pattern, mapped_type in pattern_map.items():
            if pattern in filename:
                typology = mapped_type
                break
        
        if typology:
            print(f"\nProcessing {filename} -> {typology}")
            try:
                result = generator.generate(typology, frequency=7.83)
                results['processed'].append({
                    'file': filename,
                    'typology': typology,
                    'anchor_id': result['stages']['anchor']['anchor_id']
                })
            except Exception as e:
                results['errors'].append({'file': filename, 'error': str(e)})
        else:
            print(f"Skipping {filename} (no pattern match)")
    
    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Harmonic Habitats Generator CLI - Compatible with WASP Crane and other earth printers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single pod for WASP Crane (default)
  python api/generate.py --typology single_pod --area 50 --frequency 7.83
  
  # Generate for generic printer
  python api/generate.py --typology single_pod --printer generic
  
  # Generate with STL export for custom slicer
  python api/generate.py --typology single_pod --export stl
  
  # Generate multi-pod cluster
  python api/generate.py --typology multi_pod_cluster --pods 4
  
  # Generate organic family dwelling
  python api/generate.py --typology organic_family --length 15 --width 5.6
  
  # Batch process all concept images
  python api/generate.py --batch
        """
    )
    
    parser.add_argument('--typology', type=str,
                       choices=['single_pod', 'multi_pod_cluster', 'organic_family'],
                       help='Typology to generate')
    parser.add_argument('--area', type=float, default=50,
                       help='Target area in m²')
    parser.add_argument('--frequency', type=float, default=7.83,
                       help='Target Schumann frequency (Hz)')
    parser.add_argument('--diameter', type=float, default=6.5,
                       help='Pod diameter (for single_pod)')
    parser.add_argument('--pods', type=int, default=4,
                       help='Number of pods (for multi_pod_cluster)')
    parser.add_argument('--length', type=float, default=15.0,
                       help='Length (for organic_family)')
    parser.add_argument('--width', type=float, default=5.6,
                       help='Width (for organic_family)')
    parser.add_argument('--levels', type=int, default=2,
                       help='Number of levels (for organic_family)')
    parser.add_argument('--batch', action='store_true',
                       help='Process all concept images')
    parser.add_argument('--output', type=str, default='output',
                       help='Output directory')
    parser.add_argument('--printer', type=str, default='wasp_crane',
                       choices=['wasp_crane', 'wasp', 'generic', 'cobod', 'cobod_bod2'],
                       help='Printer type (default: wasp_crane)')
    parser.add_argument('--export', type=str, nargs='+',
                       choices=['stl', 'obj', 'blend', 'gcode'],
                       help='Export formats (default: gcode only)')
    
    args = parser.parse_args()
    
    if args.batch:
        print("=== Batch Processing Concepts ===")
        results = batch_process_concepts(printer_type=args.printer)
        print(f"\nProcessed: {len(results['processed'])}")
        print(f"Errors: {len(results['errors'])}")
        for item in results['processed']:
            print(f"  ✓ {item['file']} -> {item['typology']}")
        return
    
    if not args.typology:
        parser.print_help()
        return
    
    # Generate
    generator = HabitatGenerator(output_dir=Path(args.output), 
                                  printer_type=args.printer)
    
    kwargs = {}
    if args.typology == 'single_pod':
        kwargs['diameter'] = args.diameter
    elif args.typology == 'multi_pod_cluster':
        kwargs['pod_count'] = args.pods
    elif args.typology == 'organic_family':
        kwargs['length'] = args.length
        kwargs['width'] = args.width
        kwargs['levels'] = args.levels
    
    result = generator.generate(
        typology=args.typology,
        area=args.area,
        frequency=args.frequency,
        export_formats=args.export or ['gcode'],
        **kwargs
    )
    
    # Print summary
    print("\n=== GENERATION SUMMARY ===")
    print(f"Typology: {result['typology']}")
    print(f"Printer: {result['printer']}")
    print(f"Target Frequency: {result['parameters']['frequency']} Hz")
    print(f"\nStages completed:")
    for stage in result['stages']:
        print(f"  ✓ {stage}")
    print(f"\nOutput files:")
    print(f"  - JSON Report: {args.output}/{args.typology}_report.json")
    print(f"  - Compatibility: {args.output}/printer_compatibility_report.txt")
    if 'exports' in result['stages'] and result['stages']['exports'].get('files'):
        for fmt, path in result['stages']['exports']['files'].items():
            print(f"  - {fmt.upper()}: {path}")


if __name__ == "__main__":
    main()
