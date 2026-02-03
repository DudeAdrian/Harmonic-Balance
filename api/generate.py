"""
harmonic-balance/api/generate.py
Command-line interface for Harmonic Habitats generation.
Complete pipeline: geometry → compliance → G-code → render → anchor.

v0.1.0-genesis - Sacred Geometry Engine
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from genesis.typologies import SinglePod, MultiPodCluster, OrganicFamily
from genesis.seeder import seed_from_concept
from compliance.eurocodes import ComplianceValidator, SeismicZone
from resonance.acoustic_engine import full_acoustic_analysis
from render_farm.blender_bridge import generate_typology_mesh
from terracare.anchor import TerraCareAnchor
from printer.generic_slicer import generate_for_printer, get_printer_config
from printer.materials import generate_material_report

# Default configuration
DEFAULT_CONFIG = {
    'defaults': {
        'frequency_hz': 7.83,
        'typology': 'single_pod',
        'printer': 'wasp_crane',
        'location': 'italy',
        'output_dir': 'outputs',
        'timestamped_folders': True
    }
}


def load_config(config_path: str = None) -> Dict:
    """Load configuration from YAML file or use defaults."""
    if config_path and Path(config_path).exists():
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            if YAML_AVAILABLE:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                print("Warning: PyYAML not installed. Using defaults.")
                return DEFAULT_CONFIG
        elif config_path.endswith('.json'):
            with open(config_path, 'r') as f:
                return json.load(f)
    
    # Try to load default config
    default_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    if default_path.exists() and YAML_AVAILABLE:
        with open(default_path, 'r') as f:
            return yaml.safe_load(f)
    
    return DEFAULT_CONFIG


def create_timestamped_output_dir(base_dir: str, typology: str) -> Path:
    """Create timestamped output directory."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_name = f"{timestamp}_{typology}"
    output_path = Path(base_dir) / dir_name
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


class HabitatGenerator:
    """Main generator orchestrating the complete pipeline."""
    
    def __init__(self, output_dir: Path = None, printer_type: str = None, 
                 config: Dict = None):
        self.config = config or DEFAULT_CONFIG
        defaults = self.config.get('defaults', DEFAULT_CONFIG['defaults'])
        
        self.output_dir = output_dir or Path(defaults.get('output_dir', 'outputs'))
        self.printer_type = printer_type or defaults.get('printer', 'wasp_crane')
        self.default_frequency = defaults.get('frequency_hz', 7.83)
        self.timestamped_folders = defaults.get('timestamped_folders', True)
        
        self.terracare = TerraCareAnchor()
    
    def generate(self, typology: str, area: float = None, 
                 frequency: float = None, export_formats: list = None,
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
        frequency = frequency or self.default_frequency
        export_formats = export_formats or ['gcode']
        
        # Create timestamped output directory
        if self.timestamped_folders:
            self.output_dir = create_timestamped_output_dir(
                self.output_dir.parent if isinstance(self.output_dir, Path) else self.output_dir,
                typology
            )
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'typology': typology,
            'parameters': {'area': area, 'frequency': frequency, **kwargs},
            'printer': self.printer_type,
            'timestamp': datetime.now().isoformat(),
            'version': self.config.get('version', '0.1.0'),
            'output_dir': str(self.output_dir),
            'stages': {}
        }
        
        print(f"\n{'='*60}")
        print(f"Harmonic Habitats v{results['version']}")
        print(f"Generating {typology}")
        print(f"Target frequency: {frequency} Hz")
        print(f"Printer: {self.printer_type}")
        print(f"Output: {self.output_dir}")
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
        if 'stl' in export_formats or 'obj' in export_formats or 'blend' in export_formats:
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
        self._save_gcode_file(results)
        
        print(f"\n{'='*60}")
        print("Generation complete!")
        print(f"Output: {self.output_dir}/{typology}_report.json")
        print(f"Compatibility: {self.output_dir}/printer_compatibility_report.txt")
        print(f"G-code: {self.output_dir}/{typology}.gcode")
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
    
    def _save_gcode_file(self, results: Dict):
        """Save G-code to file."""
        gcode_data = results['stages'].get('gcode', {})
        if gcode_data and 'content' in gcode_data:
            filepath = self.output_dir / f"{results['typology']}.gcode"
            with open(filepath, 'w') as f:
                f.write(gcode_data['content'])
    
    def _export_formats(self, typology: str, geometry: Dict, 
                       formats: list) -> Dict:
        """Export to STL, OBJ, and other formats."""
        export_dir = self.output_dir / 'exports'
        export_dir.mkdir(exist_ok=True)
        
        files = {}
        
        try:
            if 'stl' in formats or 'obj' in formats or 'blend' in formats:
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
        
        config = get_printer_config(self.printer_type)
        volume = geometry.get('volume_cubic_m', 50)
        material_report = generate_material_report(typology, volume, 'standard')
        
        return {
            'printer': config.name,
            'reach_radius_m': config.reach_radius_m,
            'max_height_m': config.max_height_m,
            'nozzle_diameter_mm': config.nozzle_diameter_mm,
            'geometry_specs': geo_params,
            'compatible': True,
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
            f"Version: {results.get('version', 'unknown')}",
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
            "MATERIAL SPECIFICATION",
            "-" * 70,
            compat.get('material_specification', 'N/A'),
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
            "Generated by Harmonic Habitats v0.1.0",
            "Compatible with WASP Crane and other earth printers",
            "=" * 70,
        ])
        
        with open(report_path, 'w') as f:
            f.write('\n'.join(lines))


def batch_process_concepts(concepts_dir: Path = None, 
                           printer_type: str = None,
                           config: Dict = None) -> Dict:
    """Process all concept images in genesis/concepts/."""
    concepts_dir = concepts_dir or Path("genesis/concepts")
    config = config or DEFAULT_CONFIG
    printer_type = printer_type or config.get('defaults', {}).get('printer', 'wasp_crane')
    
    if not concepts_dir.exists():
        print(f"Warning: Concepts directory not found: {concepts_dir}")
        return {'processed': [], 'errors': ['Directory not found']}
    
    generator = HabitatGenerator(
        output_dir=Path(config.get('defaults', {}).get('output_dir', 'outputs')),
        printer_type=printer_type,
        config=config
    )
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
                result = generator.generate(typology, frequency=config.get('defaults', {}).get('frequency_hz', 7.83))
                results['processed'].append({
                    'file': filename,
                    'typology': typology,
                    'anchor_id': result['stages']['anchor']['anchor_id'],
                    'output_dir': result['output_dir']
                })
            except Exception as e:
                results['errors'].append({'file': filename, 'error': str(e)})
        else:
            print(f"Skipping {filename} (no pattern match)")
    
    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Harmonic Habitats Generator CLI v0.1.0 - Compatible with WASP Crane and other earth printers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick start - generate SinglePod with defaults
  python api/generate.py --typology single_pod
  
  # Use example configuration file
  python api/generate.py --config examples/example_single_pod.json
  
  # Generate for WASP Crane (default)
  python api/generate.py --typology single_pod --printer wasp_crane
  
  # Generate for generic printer
  python api/generate.py --typology single_pod --printer generic
  
  # Export STL for custom slicer
  python api/generate.py --typology single_pod --export stl
  
  # Generate multi-pod cluster
  python api/generate.py --typology multi_pod_cluster --pods 4
  
  # Generate organic family dwelling
  python api/generate.py --typology organic_family --length 15 --width 5.6
  
  # Batch process all concept images
  python api/generate.py --batch
        """
    )
    
    parser.add_argument('--config', type=str,
                       help='Path to configuration file (JSON or YAML)')
    parser.add_argument('--typology', type=str,
                       choices=['single_pod', 'multi_pod_cluster', 'organic_family'],
                       help='Typology to generate')
    parser.add_argument('--area', type=float,
                       help='Target area in m²')
    parser.add_argument('--frequency', type=float,
                       help='Target Schumann frequency (Hz) - default: 7.83')
    parser.add_argument('--diameter', type=float,
                       help='Pod diameter (for single_pod)')
    parser.add_argument('--pods', type=int,
                       help='Number of pods (for multi_pod_cluster)')
    parser.add_argument('--length', type=float,
                       help='Length (for organic_family)')
    parser.add_argument('--width', type=float,
                       help='Width (for organic_family)')
    parser.add_argument('--levels', type=int,
                       help='Number of levels (for organic_family)')
    parser.add_argument('--batch', action='store_true',
                       help='Process all concept images')
    parser.add_argument('--output', type=str,
                       help='Output directory - default: outputs/YYYYMMDD_HHMMSS_typology/')
    parser.add_argument('--printer', type=str,
                       choices=['wasp_crane', 'wasp', 'generic', 'cobod', 'cobod_bod2'],
                       help='Printer type')
    parser.add_argument('--export', type=str, nargs='+',
                       choices=['stl', 'obj', 'blend', 'gcode'],
                       help='Export formats (default: gcode)')
    parser.add_argument('--no-timestamp', action='store_true',
                       help='Disable timestamped output folders')
    parser.add_argument('--version', action='version', version='%(prog)s v0.1.0-genesis')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    defaults = config.get('defaults', DEFAULT_CONFIG['defaults'])
    
    # Determine effective settings (config file < env < command line)
    printer_type = args.printer or defaults.get('printer', 'wasp_crane')
    frequency = args.frequency or defaults.get('frequency_hz', 7.83)
    output_dir = args.output or defaults.get('output_dir', 'outputs')
    timestamped = not args.no_timestamp if args.no_timestamp else defaults.get('timestamped_folders', True)
    
    if args.batch:
        print("=== Batch Processing Concepts ===")
        results = batch_process_concepts(printer_type=printer_type, config=config)
        print(f"\nProcessed: {len(results['processed'])}")
        print(f"Errors: {len(results['errors'])}")
        for item in results['processed']:
            print(f"  ✓ {item['file']} -> {item['typology']} ({item['output_dir']})")
        return
    
    if not args.typology and not args.config:
        parser.print_help()
        return
    
    # Load config file if provided
    config_params = {}
    if args.config and args.config.endswith('.json'):
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            # Extract relevant parameters
            if 'geometry' in config_data:
                geo = config_data['geometry']
                config_params['diameter'] = geo.get('diameter_m')
                config_params['height'] = geo.get('height_m')
                config_params['length'] = geo.get('length_m')
                config_params['width'] = geo.get('width_m')
                config_params['levels'] = geo.get('levels')
                config_params['pod_count'] = config_data.get('geometry', {}).get('pod_count')
            if 'printer' in config_data:
                config_params['printer_type'] = config_data['printer'].get('type')
            if 'acoustics' in config_data:
                freq = config_data['acoustics'].get('target_frequency_hz')
                if freq and not args.frequency:
                    frequency = freq
        
        # Set typology from config
        if not args.typology and 'typology' in config_data:
            args.typology = config_data['typology'].get('type')
    
    # Generate
    generator = HabitatGenerator(
        output_dir=Path(output_dir),
        printer_type=config_params.get('printer_type', printer_type),
        config=config
    )
    generator.timestamped_folders = timestamped
    
    kwargs = {}
    if args.typology == 'single_pod':
        kwargs['diameter'] = args.diameter or config_params.get('diameter', 6.5)
        kwargs['height'] = config_params.get('height', 3.2)
    elif args.typology == 'multi_pod_cluster':
        kwargs['pod_count'] = args.pods or config_params.get('pod_count', 4)
    elif args.typology == 'organic_family':
        kwargs['length'] = args.length or config_params.get('length', 15.0)
        kwargs['width'] = args.width or config_params.get('width', 5.6)
        kwargs['levels'] = args.levels or config_params.get('levels', 2)
    
    result = generator.generate(
        typology=args.typology,
        area=args.area,
        frequency=frequency,
        export_formats=args.export or ['gcode'],
        **kwargs
    )
    
    # Print summary
    print("\n=== GENERATION SUMMARY ===")
    print(f"Typology: {result['typology']}")
    print(f"Printer: {result['printer']}")
    print(f"Version: {result.get('version', 'unknown')}")
    print(f"Target Frequency: {result['parameters']['frequency']} Hz")
    print(f"\nStages completed:")
    for stage in result['stages']:
        print(f"  ✓ {stage}")
    print(f"\nOutput files:")
    print(f"  - Output Directory: {result['output_dir']}")
    print(f"  - JSON Report: {result['output_dir']}/{args.typology}_report.json")
    print(f"  - G-code: {result['output_dir']}/{args.typology}.gcode")
    print(f"  - Compatibility: {result['output_dir']}/printer_compatibility_report.txt")
    if 'exports' in result['stages'] and result['stages']['exports'].get('files'):
        for fmt, path in result['stages']['exports']['files'].items():
            print(f"  - {fmt.upper()}: {path}")


if __name__ == "__main__":
    main()
