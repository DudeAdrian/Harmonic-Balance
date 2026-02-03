# Harmonic Habitats Web Application

Web interface for sketch-to-dwelling generation using the Harmonic Habitats sacred geometry engine.

## Features

- **Image Upload**: Drag-and-drop or click to upload sketches (JPG, PNG, GIF, WEBP, BMP)
- **AI Analysis**: Automatic detection of typology from image patterns
  - Circular pod → SinglePod
  - Multiple domes → MultiPodCluster
  - Flowing organic form → OrganicFamily
- **Auto-Generation**: Complete dwelling generation pipeline
  - Geometry generation
  - Compliance checking (NTC 2018)
  - Acoustic optimization (7.83 Hz Schumann resonance)
  - G-code generation for 3D printing
- **3D Preview**: Visual preview of generated dwelling (SVG placeholder, full 3D coming v0.2)
- **Download Files**: G-code, JSON report, Terracare anchor

## Installation

```bash
# From repository root
pip install -r requirements.txt
```

## Usage

### Start the Web Server

```bash
# From repository root
python webapp/app.py
```

Output:
```
============================================================
Harmonic Habitats Web Application
v0.1.0 - Genesis
============================================================
Upload folder: webapp/uploads
Output folder: webapp/outputs
============================================================
Open browser: http://localhost:5000
============================================================
```

### Using the Application

1. **Open browser**: Navigate to `http://localhost:5000`

2. **Upload sketch**: 
   - Drag and drop an image onto the upload zone, or
   - Click to browse and select an image
   - Supported formats: JPG, PNG, GIF, WEBP, BMP (max 16MB)

3. **Sketch guidelines**:
   - **Single Pod**: Draw a circle with central core (Single dwelling, 1-2 sleepers)
   - **Village Cluster**: Draw multiple connected domes (Community, 6 sleepers)
   - **Organic Form**: Draw flowing, curved lines (Family dwelling, 4 bedrooms)

4. **Click "Generate Dwelling"**:
   - Wait 30-60 seconds for processing
   - System will analyze image, detect typology, generate geometry
   - Progress shown on loading screen

5. **View results**:
   - Compare original sketch vs 3D generated dwelling
   - Review detected parameters (dimensions, frequency, compliance)
   - Check acoustic optimization status

6. **Download files**:
   - **G-code**: For 3D printer (WASP Crane compatible)
   - **Report**: Full JSON specification
   - **Terracare**: Blockchain anchor for provenance

## Project Structure

```
webapp/
├── app.py                  # Flask application
├── uploads/                # Uploaded images (created automatically)
├── outputs/                # Generated files (created automatically)
├── templates/
│   ├── index.html         # Upload form
│   ├── results.html       # Results display
│   └── error.html         # Error page
├── static/
│   ├── css/
│   │   └── style.css      # Earth-tone styling
│   └── js/
│       └── upload.js      # Drag-drop and preview
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Upload form |
| `/upload` | POST | Accept image, generate dwelling |
| `/results/<job_id>` | GET | View generation results |
| `/download/<job_id>/<type>` | GET | Download files (gcode, report, anchor) |
| `/api/status/<job_id>` | GET | Check job status (JSON) |

## Configuration

Environment variables (optional):

```bash
export FLASK_ENV=development
export FLASK_PORT=5000
export MAX_CONTENT_LENGTH=16777216  # 16MB
```

## Development

### Run in Debug Mode

```python
# In app.py, change:
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Add New Typology Detection

Edit `detect_typology_from_image()` in `app.py`:

```python
def detect_typology_from_image(image_path: Path) -> Tuple[str, Dict]:
    # Add new detection patterns
    if some_new_pattern in style_dna:
        return 'new_typology', seeder.to_parameters()
```

### Customize Styling

Edit `static/css/style.css`:

```css
:root {
    --color-sand: #C4A77D;    /* Primary accent */
    --color-earth: #8B5A2B;   /* Buttons, headings */
    --color-forest: #2C5F2D;  /* Success states */
}
```

## Troubleshooting

### "No module named 'flask'"
```bash
pip install flask werkzeug
```

### "File too large"
- Maximum upload size is 16MB
- Resize image or use compression

### "Generation failed"
- Check that all project dependencies are installed
- Verify `genesis/`, `printer/`, `compliance/`, `resonance/` modules are present
- Check console for error messages

### 3D preview not showing
- The preview uses SVG placeholder graphics
- Full 3D rendering with Blender integration coming in v0.2

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Notes

- File uploads are restricted to image formats only
- Uploaded files are saved with secure filenames
- Maximum file size limit enforced
- CSRF protection recommended for production deployment

## Production Deployment

For production use:

```bash
# Use production WSGI server
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 webapp.app:app
```

Add to `app.py` for production:
```python
# Disable debug mode
app.run(debug=False)

# Set secret key
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

## Roadmap

### v0.1.0 (Current)
- ✅ Image upload and analysis
- ✅ Typology auto-detection
- ✅ Generation pipeline
- ✅ SVG preview graphics
- ✅ G-code download

### v0.2.0
- 🔄 Blender 3D rendering
- 🔄 Interactive 3D viewer
- 🔄 STL/OBJ download
- 🔄 PDF construction plans

### v0.3.0
- 🔄 Live blockchain anchoring
- 🔄 Design marketplace
- 🔄 Multi-user accounts

## License

See repository LICENSE file. Proprietary - All Rights Reserved.

## Support

For issues or questions:
- Check main repository README.md
- Review INDEPENDENT_BUILD.md for standalone usage
- See PARTNERSHIP_PROPOSAL.md for WASP partnership info
