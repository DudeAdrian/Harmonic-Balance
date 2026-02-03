# Harmonic-Balance

**Sacred geometry generation for resonant dwellings.**

Computational temple architecture for the modern age. Design frequency-tuned, 3D printed earth dwellings optimized for human wellbeing.

---

## 🏛️ Overview

Harmonic Habitats generates earth dwellings that combine:
- **Sacred geometry** (hexagonal tessellation, golden proportions)
- **Schumann resonance alignment** (7.83 Hz - Earth's natural frequency)
- **Malta temple acoustics** (ancient healing architecture)
- **Modern compliance** (Italy NTC 2018, Eurocode 6, nZEB)

**Compatible with WASP Crane and other large-format earth printers.**

---

## 🚀 Quick Start

```bash
# Generate a SinglePod for WASP Crane (default)
python api/generate.py --typology single_pod --area 50 --frequency 7.83

# Generate for any Marlin-compatible printer
python api/generate.py --typology single_pod --printer generic

# Export STL for use with any slicer
python api/generate.py --typology single_pod --export stl

# Batch process concept images
python api/generate.py --batch
```

---

## 🖨️ Printer Compatibility

### Supported Printers

| Printer | Status | Configuration |
|---------|--------|---------------|
| **WASP Crane** | ✅ Optimized | `--printer wasp_crane` (default) |
| **COBOD BOD2** | ✅ Compatible | `--printer cobod_bod2` |
| **PERI 3D** | ✅ Compatible | `--printer generic` |
| **Custom Gantry** | ⚙️ Configurable | Edit `printer/generic_slicer.py` |
| **Desktop FDM** | ⚠️ Formwork only | Export STL, print molds |

### Generic Earth Printer Support

Our software outputs **standard Marlin firmware G-code** compatible with any large-format earth printer:

- Standard G1/G2/G3 commands
- Configurable layer heights (15-25mm)
- Adjustable print speeds (30-60mm/s)
- Material-optimized flow rates

```python
from printer.generic_slicer import generate_for_printer

# Generate for any printer
result = generate_for_printer(
    typology='single_pod',
    printer_type='generic',
    diameter=6.5,
    height=3.2
)
```

---

## 🏗️ Typologies

### SinglePod
Circular dwelling for 1-2 sleepers:
- **Dimensions**: 6-7m diameter, 3.2m height
- **Area**: 48-55m²
- **Features**: Central service core (Type A), radial layout, honeycomb wall texture
- **Volume**: 8.5-9.5m³ RMDC

### MultiPodCluster
4-pod village arrangement for 6 sleepers:
- **Configuration**: 4 individual pods in circular arrangement
- **Site plan**: 12m arrangement radius, 8m central gathering space
- **Shared space**: Central gathering area with connecting paths

### OrganicFamily
Large flowing dwelling for extended family:
- **Dimensions**: 15m x 5.6m footprint
- **Levels**: 2 levels with spiral stairs
- **Bedrooms**: 4 bedrooms
- **Footprint**: 84m²

---

## 📐 Design Features

### Acoustic Engineering
- **Schumann resonance coupling**: Room modes aligned to 7.83 Hz
- **Honeycomb diffusion**: Wall cavities as acoustic diffusers
- **Malta oracle acoustics**: 80Hz resonance targets, 6.5s reverb

### Compliance
- **Italy NTC 2018**: Full seismic zone validation
- **Eurocode 6**: Masonry/earth structure verification
- **Eurocode 1**: Load calculations for printed earth
- **nZEB**: Nearly Zero Energy Building standards

| Climate Zone | Target EPh (kWh/m²/y) |
|--------------|----------------------|
| A | 35 |
| B | 40 |
| C | 45 |
| D | 50 |
| E | 55 |
| F | 60 |

---

## 🌍 Materials

### Standard Earth Mix
```
Clay:    30%
Sand:    50%
Silt:    20%
Water:   8%
Additives: Natural fibers (2%), Lime (5%)
```

**Performance:**
- Compression: 2-5 MPa
- Thermal conductivity: 0.8-1.2 W/mK
- Cure time: 28 days

*Calibrated for WASP Crane - adjust for other printers*

### Resonance-Enhanced Mix
Optional quartz additive for frequency-tuned structures.

---

## 📦 Export Options

### 3D Printing
- **G-code**: Direct to printer (Marlin-compatible)
- **STL**: Universal 3D print format
- **OBJ**: With materials and textures
- **.blend**: Full Blender scene

### Construction
- **Formwork**: STL → Desktop 3D print → Reusable molds
- **CNC**: OBJ → Toolpaths → Plywood formwork
- **Manual**: Dimensioned drawings → Traditional construction

### Documentation
- Compliance reports
- Material specifications
- Acoustic analysis
- Terracare blockchain anchor

---

## 🤝 Partnership Status

### WASP Partnership (In Discussion)

We are actively pursuing a strategic partnership with **WASP (World's Advanced Saving Project)** of Italy:

- **Technical integration**: Our software outputs WASP-ready G-code
- **Pilot project**: Proposed SinglePod demonstration print
- **Market opportunity**: Wellness-focused 3D printed dwellings
- **Compliance advantage**: Built-in Italy NTC 2018 validation

See [`docs/PARTNERSHIP_PROPOSAL.md`](docs/PARTNERSHIP_PROPOSAL.md) for full proposal.

### Open Architecture

**You do NOT need WASP partnership to use Harmonic Habitats.**

Our open-source architecture supports:
- ✅ Any Marlin-compatible 3D printer
- ✅ CNC manufacturing
- ✅ Traditional hand-building
- ✅ Hybrid construction methods

See [`docs/INDEPENDENT_BUILD.md`](docs/INDEPENDENT_BUILD.md) for standalone usage.

---

## 📁 Repository Structure

```
Harmonic-Balance/
├── genesis/              # Sacred geometry core
│   ├── geometry.py       # Base geometry & WASPPrinter
│   ├── seeder.py         # Image recognition & parametric DNA
│   └── typologies.py     # SinglePod, MultiPodCluster, OrganicFamily
│
├── printer/              # Generic 3D printing support
│   ├── generic_slicer.py # Marlin-compatible G-code
│   └── materials.py      # Earth mix specifications
│
├── resonance/            # Acoustic engineering
│   ├── tuner.py          # Basic Schumann alignment
│   └── acoustic_engine.py # Advanced room mode analysis
│
├── compliance/           # Italy/EU compliance
│   └── eurocodes.py      # NTC 2018, EC6, EC1, nZEB
│
├── render_farm/          # Visualization
│   └── blender_bridge.py # Blender mesh generation
│
├── terracare/            # Blockchain provenance
│   └── anchor.py         # Design hashing & anchoring
│
├── api/                  # Command-line interface
│   └── generate.py       # Complete generation pipeline
│
├── docs/                 # Documentation
│   ├── PARTNERSHIP_PROPOSAL.md  # WASP partnership proposal
│   └── INDEPENDENT_BUILD.md     # Standalone usage guide
│
└── README.md
```

---

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/DudeAdrian/Harmonic-Balance.git
cd Harmonic-Balance

# Install dependencies
pip install -r requirements.txt

# Run generation
python api/generate.py --help
```

### Requirements
- Python 3.8+
- numpy, scipy
- Pillow (image processing)
- bpy (optional, for Blender export)

---

## 📝 Usage Examples

### Generate for WASP Crane
```bash
python api/generate.py \
  --typology single_pod \
  --diameter 6.5 \
  --frequency 7.83 \
  --printer wasp_crane
```

### Export for Custom Slicer
```bash
python api/generate.py \
  --typology organic_family \
  --length 15 \
  --width 5.6 \
  --export stl obj
```

### Batch Process Concepts
```bash
# Place images in genesis/concepts/
python api/generate.py --batch --printer generic
```

### Programmatic Usage
```python
from genesis.typologies import SinglePod
from printer.generic_slicer import generate_for_printer

# Generate geometry
pod = SinglePod(diameter=6.5)
result = pod.generate()

# Generate G-code for your printer
gcode_result = generate_for_printer(
    'single_pod',
    printer_type='generic',
    diameter=6.5,
    height=3.2
)

print(gcode_result['gcode'])
```

---

## 🌐 Frequency

Everything resonates at **7.83 Hz**.

The Schumann resonance - Earth's heartbeat - is embedded in every Harmonic Habitat design.

---

## 📄 License

Private repository. See LICENSE for details.

---

## 🔗 Links

- **GitHub**: https://github.com/DudeAdrian/Harmonic-Balance
- **WASP**: https://www.3dwasp.com/
- **Documentation**: See `docs/` directory

---

*Computational temple architecture for the modern age.*
