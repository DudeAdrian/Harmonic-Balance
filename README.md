# Harmonic-Balance

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![License](https://img.shields.io/badge/license-Proprietary-red)]()
[![Version](https://img.shields.io/badge/version-0.1.0--genesis-orange)]()

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

### 3 Commands to First Dwelling

```bash
# 1. Clone repository
git clone https://github.com/DudeAdrian/Harmonic-Balance.git
cd Harmonic-Balance

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate your first dwelling
python api/generate.py --typology single_pod --area 50 --frequency 7.83
```

**Output:** `outputs/YYYYMMDD_HHMMSS_single_pod/` containing:
- `single_pod.gcode` - Ready to print
- `single_pod_report.json` - Complete specification
- `printer_compatibility_report.txt` - Setup guide

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HARMONIC HABITATS v0.1.0                     │
│                   Sacred Geometry Engine                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   GENESIS    │───▶│  RESONANCE   │───▶│ COMPLIANCE   │      │
│  │              │    │              │    │              │      │
│  │ • Geometry   │    │ • Schumann   │    │ • NTC 2018   │      │
│  │ • Typologies │    │ • Room Modes │    │ • Eurocode 6 │      │
│  │ • Seeder     │    │ • Malta      │    │ • nZEB       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             ▼                                   │
│                  ┌──────────────────────┐                       │
│                  │   GENERIC SLICER     │                       │
│                  │                      │                       │
│                  │ • Marlin G-code      │                       │
│                  │ • G2/G3 Arcs         │                       │
│                  │ • WASP/generic       │                       │
│                  └──────────────────────┘                       │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │    OUTPUT    │    │   EXPORTS    │    │  TERRACARE   │      │
│  │              │    │              │    │              │      │
│  │ • .gcode     │    │ • .stl       │    │ • Anchor     │      │
│  │ • Reports    │    │ • .obj       │    │ • Provenance │      │
│  │ • Materials  │    │ • .blend     │    │ • Version    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
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

### MultiPodCluster
4-pod village arrangement for 6 sleepers:
- **Configuration**: 4 individual pods in circular arrangement
- **Site plan**: 12m arrangement radius, 8m central gathering space

### OrganicFamily
Large flowing dwelling for extended family:
- **Dimensions**: 15m x 5.6m footprint
- **Levels**: 2 levels with spiral stairs
- **Bedrooms**: 4 bedrooms

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/DudeAdrian/Harmonic-Balance.git
cd Harmonic-Balance

# Install dependencies
pip install -r requirements.txt

# Verify installation
python api/generate.py --version
```

### Requirements
- Python 3.9+
- numpy, scipy
- Pillow (image processing)
- PyYAML (config files)
- bpy (optional, for Blender export)

---

## 📝 Usage Examples

### Using Example Configurations

```bash
# Single Pod
python api/generate.py --config examples/example_single_pod.json

# Organic Family
python api/generate.py --config examples/example_organic_family.json

# Cluster
python api/generate.py --config examples/example_cluster.json
```

### Command Line Generation

```bash
# Generate for WASP Crane
python api/generate.py \
  --typology single_pod \
  --diameter 6.5 \
  --frequency 7.83 \
  --printer wasp_crane

# Export for Custom Slicer
python api/generate.py \
  --typology organic_family \
  --length 15 \
  --width 5.6 \
  --export stl obj

# Batch Process Concepts
python api/generate.py --batch --printer generic
```

---

## 🌍 Materials

### Standard Earth Mix
```
Clay:    30%  (binder)
Sand:    50%  (aggregate)
Silt:    20%  (filler)
Water:   8%   (activation)
Additives: Natural fibers (2%), Lime (5%)
```

**Performance:**
- Compression: 2-5 MPa
- Thermal conductivity: 0.8-1.2 W/mK
- Cure time: 28 days

*Calibrated for WASP Crane - adjust for other printers*

---

## 🤝 Partnership Status

### WASP Partnership (In Discussion)

We are actively pursuing a strategic partnership with **WASP (World's Advanced Saving Project)** of Italy:

- **Technical integration**: Our software outputs WASP-ready G-code
- **Pilot project**: Proposed SinglePod demonstration print
- **Market opportunity**: Wellness-focused 3D printed dwellings

See [`docs/PARTNERSHIP_PROPOSAL.md`](docs/PARTNERSHIP_PROPOSAL.md) for full proposal.

### Open Architecture

**You do NOT need WASP partnership to use Harmonic Habitats.**

Our open architecture supports:
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
├── printer/              # Generic 3D printing (Marlin-compatible)
├── resonance/            # Acoustic engineering
├── compliance/           # Italy/EU compliance (NTC 2018)
├── render_farm/          # Blender integration
├── terracare/            # Blockchain provenance
├── api/                  # CLI interface
├── config/               # YAML configuration
├── examples/             # Example JSON configs
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD
```

---

## 🗺️ Roadmap

### v0.1.0 Genesis (Current)
- ✅ Sacred geometry engine
- ✅ Schumann resonance alignment
- ✅ WASP/generic printer support
- ✅ NTC 2018 compliance
- ✅ Terracare anchoring

### v0.2.0 Compliance Expansion
- 🔄 Eurocode 8 seismic analysis
- 🔄 German DIN standards
- 🔄 French DTU codes
- 🔄 US IBC integration

### v0.3.0 Terracare Integration
- 🔄 Live blockchain anchoring
- 🔄 IPFS document storage
- 🔄 Design marketplace
- 🔄 Automated permitting

### v0.4.0 AI Optimization
- 🔄 Generative design AI
- 🔄 Climate-responsive forms
- 🔄 Material optimization
- 🔄 Structural topology

---

## 🔒 License

**Proprietary - All Rights Reserved**

This software is private and proprietary. See [LICENSE](LICENSE) for details.

- No commercial use without written agreement
- Sacred geometry algorithms protected
- Partnership licensing available

---

## 🌐 Frequency

Everything resonates at **7.83 Hz**.

The Schumann resonance - Earth's heartbeat - is embedded in every Harmonic Habitat design.

---

## 🔗 Links

- **GitHub**: https://github.com/DudeAdrian/Harmonic-Balance
- **WASP**: https://www.3dwasp.com/
- **Examples**: See `examples/` directory

---

*Computational temple architecture for the modern age.*  
**v0.1.0-genesis - Sacred Geometry Engine**
