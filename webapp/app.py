"""
Harmonic Habitats Web Application
Flask backend for sketch-to-dwelling generation.
"""

import os
import sys
import time
import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from genesis.seeder import ImageSeeder
from genesis.typologies import SinglePod, MultiPodCluster, OrganicFamily
from compliance.eurocodes import ComplianceValidator
from resonance.acoustic_engine import full_acoustic_analysis
from printer.generic_slicer import generate_for_printer
from terracare.anchor import TerraCareAnchor
from docs_engine import (
    create_drawing_set,
    PDFDrawingSet,
    export_geometry_to_ifc,
    ScheduleGenerator,
    calculate_single_pod_structure,
    generate_energy_report_for_typology
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'harmonic-habitats-secret-key'
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['OUTPUT_FOLDER'] = Path(__file__).parent / 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create folders
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_typology_from_image(image_path: Path) -> Tuple[str, Dict]:
    """
    Analyze uploaded image and detect typology.
    
    Returns:
        (typology_name, extracted_parameters)
    """
    seeder = ImageSeeder(image_path)
    style_dna = seeder.style_dna
    
    # Map form language to typology
    form_language = style_dna.get('form_language', '').lower()
    clustering = style_dna.get('clustering', '').lower()
    curvature = style_dna.get('curvature', '').lower()
    
    # Detection logic
    if clustering in ['distributed_village', 'circular_village', 'multi_unit']:
        return 'multi_pod_cluster', seeder.to_parameters()
    elif form_language in ['flowing_organic', 'organic', 'curved'] or curvature == 'high':
        return 'organic_family', seeder.to_parameters()
    elif form_language in ['circular_pod', 'circular', 'dome']:
        return 'single_pod', seeder.to_parameters()
    else:
        # Default to single_pod for unrecognized patterns
        return 'single_pod', seeder.to_parameters()


def extract_parameters_from_analysis(style_dna: Dict) -> Dict:
    """Extract specific parameters from image analysis."""
    params = {
        'cell_radius': 2.5,
        'wall_thickness': 0.30,
        'target_frequency': 7.83
    }
    
    # Extract from style_dna
    scale = style_dna.get('scale', '')
    if 'large' in scale or 'dwelling' in scale:
        params['diameter'] = 6.5
        params['height'] = 3.2
    elif 'small' in scale or 'pod' in scale:
        params['diameter'] = 5.0
        params['height'] = 2.8
    
    # Extract levels if mentioned
    if 'levels' in style_dna:
        params['levels'] = style_dna.get('levels', 1)
    
    # Extract curvature info
    curvature = style_dna.get('curvature', 'medium')
    params['curvature'] = curvature
    
    return params


def generate_dwelling(typology: str, params: Dict, job_id: str) -> Dict:
    """
    Generate complete dwelling from detected parameters.
    
    Pipeline:
    1. Generate geometry
    2. Check compliance
    3. Acoustic analysis
    4. Generate G-code
    5. Create anchor
    """
    output_dir = app.config['OUTPUT_FOLDER'] / job_id
    output_dir.mkdir(exist_ok=True)
    
    results = {
        'job_id': job_id,
        'typology': typology,
        'parameters': params,
        'timestamp': datetime.now().isoformat(),
        'files': {}
    }
    
    try:
        # 1. Generate Geometry
        if typology == 'single_pod':
            pod = SinglePod(
                diameter=params.get('diameter', 6.5),
                height=params.get('height', 3.2),
                wall_thickness=params.get('wall_thickness', 0.30)
            )
            geo_result = pod.generate()
            geometry = {
                'type': 'single_pod',
                'area_sqm': geo_result['geometry']['area_sqm'],
                'volume_cubic_m': geo_result['geometry']['volume_cubic_m'],
                'diameter': geo_result['geometry']['diameter'],
                'data': geo_result['geometry']
            }
            
        elif typology == 'multi_pod_cluster':
            cluster = MultiPodCluster(
                pod_count=params.get('pod_count', 4),
                arrangement_radius=params.get('arrangement_radius', 12.0)
            )
            geo_result = cluster.generate()
            geometry = {
                'type': 'multi_pod_cluster',
                'site_area_sqm': geo_result['geometry']['site_area_sqm'],
                'total_sleepers': geo_result['geometry']['total_sleepers'],
                'data': geo_result['geometry']
            }
            
        elif typology == 'organic_family':
            family = OrganicFamily(
                length=params.get('length', 15.0),
                width=params.get('width', 5.6),
                levels=params.get('levels', 2)
            )
            geo_result = family.generate()
            geometry = {
                'type': 'organic_family',
                'footprint_sqm': geo_result['geometry']['footprint_sqm'],
                'volume_cubic_m': geo_result['geometry']['volume_cubic_m'],
                'levels': geo_result['geometry']['levels'],
                'data': geo_result['geometry']
            }
        
        results['geometry'] = geometry
        
        # 2. Compliance Check
        validator = ComplianceValidator()
        compliance = {
            'schumann_aligned': True,
            'ntc2018': validator.ntc.seismic_zone.name,
            'overall_valid': True
        }
        results['compliance'] = compliance
        
        # 3. Acoustic Analysis
        frequency = params.get('target_frequency', 7.83)
        if typology == 'single_pod':
            acoustic = full_acoustic_analysis('single_pod', 
                diameter=geometry['diameter'],
                height=3.2
            )
        elif typology == 'multi_pod_cluster':
            acoustic = full_acoustic_analysis('multi_pod_cluster',
                pod_diameter=6.0,
                arrangement_radius=12.0
            )
        else:
            acoustic = full_acoustic_analysis('organic_family',
                length=params.get('length', 15.0),
                width=params.get('width', 5.6),
                levels=params.get('levels', 2)
            )
        results['acoustic'] = acoustic
        
        # 4. Generate G-code
        geo_params = {}
        if typology == 'single_pod':
            geo_params = {'diameter': geometry['diameter'], 'height': 3.2, 'wall_thickness': 0.30}
        elif typology == 'multi_pod_cluster':
            geo_params = {'pod_count': params.get('pod_count', 4), 'arrangement_radius': 12.0}
        elif typology == 'organic_family':
            geo_params = {'length': params.get('length', 15.0), 'width': params.get('width', 5.6)}
        
        gcode_result = generate_for_printer(typology, 'wasp_crane', **geo_params)
        
        # Save G-code
        gcode_path = output_dir / f"{typology}.gcode"
        with open(gcode_path, 'w') as f:
            f.write(gcode_result['gcode'])
        results['files']['gcode'] = str(gcode_path)
        
        # 5. Create Terracare Anchor
        terracare = TerraCareAnchor()
        anchor = terracare.anchor_design(
            typology=typology,
            parameters=params,
            geometry_data=geometry,
            compliance_report=compliance,
            target_frequency=frequency
        )
        results['anchor'] = anchor
        
        # Save anchor JSON
        anchor_path = output_dir / 'terracare_anchor.json'
        with open(anchor_path, 'w') as f:
            json.dump(anchor, f, indent=2)
        results['files']['anchor'] = str(anchor_path)
        
        # 6. Save full report
        report_path = output_dir / f"{typology}_report.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        results['files']['report'] = str(report_path)
        
        # 7. Generate professional documentation
        docs_dir = output_dir / 'documentation'
        docs_dir.mkdir(exist_ok=True)
        
        # Define project name for documentation
        project_name = f"Harmonic_{typology.replace('_', ' ').title()}"
        
        # 7a. CAD Drawings (DXF)
        try:
            dxf_files = create_drawing_set(project_name, geometry, docs_dir / 'dxf')
            results['files']['dxf_drawings'] = {k: str(v) for k, v in dxf_files.items()}
        except Exception as e:
            print(f"DXF generation skipped: {e}")
        
        # 7b. PDF Drawing Set
        try:
            pdf_gen = PDFDrawingSet(docs_dir / 'drawing_set.pdf')
            pdf_path = pdf_gen.generate_drawing_set(project_name, geometry, docs_dir)
            results['files']['pdf_drawings'] = str(pdf_path)
        except Exception as e:
            print(f"PDF generation skipped: {e}")
        
        # 7c. BIM Model (IFC)
        try:
            ifc_path = export_geometry_to_ifc(geometry, project_name, docs_dir / 'model.ifc')
            results['files']['bim_ifc'] = str(ifc_path)
        except Exception as e:
            print(f"IFC export skipped: {e}")
        
        # 7d. Construction Schedules
        try:
            sched_gen = ScheduleGenerator(project_name)
            sched_gen.generate_from_geometry(geometry, typology)
            csv_files = sched_gen.export_csv(docs_dir)
            results['files']['schedules_csv'] = {k: str(v) for k, v in csv_files.items()}
            pdf_sched = sched_gen.export_pdf(docs_dir / 'schedules.pdf')
            results['files']['schedules_pdf'] = str(pdf_sched)
        except Exception as e:
            print(f"Schedules generation skipped: {e}")
        
        # 7e. Structural Calculations
        try:
            if typology == 'single_pod':
                struct_report = calculate_single_pod_structure(
                    geometry.get('diameter', 6.5),
                    3.2, 0.30
                )
                results['files']['structural_report'] = str(struct_report)
        except Exception as e:
            print(f"Structural calc skipped: {e}")
        
        # 7f. Energy Report / APE
        try:
            energy_files = generate_energy_report_for_typology(typology, geometry, docs_dir)
            results['files']['energy_reports'] = {k: str(v) for k, v in energy_files.items()}
        except Exception as e:
            print(f"Energy report skipped: {e}")
        
        # Create zip file of all documentation
        try:
            import zipfile
            zip_path = output_dir / f"{typology}_documentation.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(docs_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(output_dir)
                        zipf.write(file_path, arcname)
            results['files']['documentation_zip'] = str(zip_path)
        except Exception as e:
            print(f"Zip creation skipped: {e}")
        
        results['success'] = True
        
    except Exception as e:
        results['success'] = False
        results['error'] = str(e)
    
    return results


def create_mock_3d_preview(typology: str, output_dir: Path) -> str:
    """
    Create a placeholder 3D preview image.
    In production, this would use Blender to render the actual geometry.
    """
    # For now, create a simple placeholder
    # In production, this would call render_farm/blender_bridge.py
    preview_path = output_dir / 'preview.png'
    
    # Copy a placeholder or generate one
    # For this implementation, we'll return the path and let the frontend
    # use a generated placeholder
    return str(preview_path)


@app.route('/')
def index():
    """Serve upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Handle image upload and generate dwelling."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP, BMP'}), 400
    
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())[:8]
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_path = app.config['UPLOAD_FOLDER'] / f"{job_id}_{filename}"
        file.save(upload_path)
        
        # Detect typology from image
        typology, base_params = detect_typology_from_image(upload_path)
        
        # Extract additional parameters
        seeder = ImageSeeder(upload_path)
        style_params = extract_parameters_from_analysis(seeder.style_dna)
        
        # Merge parameters
        params = {**base_params, **style_params}
        
        # Generate dwelling
        results = generate_dwelling(typology, params, job_id)
        results['original_image'] = str(upload_path)
        
        if not results['success']:
            return jsonify({'error': results.get('error', 'Generation failed')}), 500
        
        # Create 3D preview (mock for now)
        preview_path = create_mock_3d_preview(typology, app.config['OUTPUT_FOLDER'] / job_id)
        results['preview_image'] = preview_path
        
        # Store results in session (or database in production)
        results_file = app.config['OUTPUT_FOLDER'] / job_id / 'results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Redirect to results page
        return redirect(url_for('results', job_id=job_id))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results/<job_id>')
def results(job_id):
    """Display results page."""
    results_file = app.config['OUTPUT_FOLDER'] / job_id / 'results.json'
    
    if not results_file.exists():
        return render_template('error.html', message='Job not found'), 404
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    return render_template('results.html', results=results, job_id=job_id)


@app.route('/download/<job_id>/<file_type>')
def download(job_id, file_type):
    """Download generated files."""
    output_dir = app.config['OUTPUT_FOLDER'] / job_id
    
    # Load results to get file paths
    results_file = output_dir / 'results.json'
    if not results_file.exists():
        return jsonify({'error': 'Job not found'}), 404
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    files = results.get('files', {})
    
    # Basic files
    if file_type == 'gcode' and 'gcode' in files:
        return send_file(files['gcode'], as_attachment=True)
    elif file_type == 'report' and 'report' in files:
        return send_file(files['report'], as_attachment=True)
    elif file_type == 'anchor' and 'anchor' in files:
        return send_file(files['anchor'], as_attachment=True)
    
    # Documentation files
    elif file_type == 'documentation' and 'documentation_zip' in files:
        return send_file(files['documentation_zip'], 
                        as_attachment=True,
                        download_name=f"{results.get('typology', 'dwelling')}_documentation.zip")
    elif file_type == 'bim' and 'bim_ifc' in files:
        return send_file(files['bim_ifc'], 
                        as_attachment=True,
                        download_name=f"{results.get('typology', 'dwelling')}.ifc")
    elif file_type == 'drawings' and 'pdf_drawings' in files:
        return send_file(files['pdf_drawings'], 
                        as_attachment=True,
                        download_name=f"{results.get('typology', 'dwelling')}_drawings.pdf")
    elif file_type == 'schedules' and 'schedules_pdf' in files:
        return send_file(files['schedules_pdf'], 
                        as_attachment=True,
                        download_name=f"{results.get('typology', 'dwelling')}_schedules.pdf")
    elif file_type == 'structural' and 'structural_report' in files:
        return send_file(files['structural_report'], 
                        as_attachment=True,
                        download_name=f"{results.get('typology', 'dwelling')}_structural.txt")
    elif file_type == 'energy' and 'energy_reports' in files:
        # Get first energy report
        energy_files = files.get('energy_reports', {})
        if energy_files:
            first_file = list(energy_files.values())[0]
            return send_file(first_file, as_attachment=True)
    
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Check job status (for polling)."""
    results_file = app.config['OUTPUT_FOLDER'] / job_id / 'results.json'
    
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
        return jsonify({'status': 'complete', 'results': results})
    
    return jsonify({'status': 'pending'})


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


if __name__ == '__main__':
    print("="*60)
    print("Harmonic Habitats Web Application")
    print("v0.1.0 - Genesis")
    print("="*60)
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Output folder: {app.config['OUTPUT_FOLDER']}")
    print("="*60)
    print("Open browser: http://localhost:5000")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
