# Harmonic-Balance

> **Environmental Layer of the Seven Pillar Architecture** — *Sacred Geometry for Resonant Dwellings*

[![Seven Pillars](https://img.shields.io/badge/Seven%20Pillars-v1.0.0-blue)](./SEVEN_PILLARS.md)
[![S.O.F.I.E.](https://img.shields.io/badge/S.O.F.I.E.-Intelligence-orange)](./SEVEN_PILLARS.md)

Computational temple architecture for the modern age. Design frequency-tuned, 3D printed earth dwellings optimized for human wellbeing.

---

## Seven Pillar Mapping

| Pillar | Component | File/Module | Function |
|--------|-----------|-------------|----------|
| **P1** | Underground Knowledge | `genesis/geometry.py` | Sacred geometry foundations |
| **P1** | Underground Knowledge | `genesis/typologies.py` | Dwelling archetypes catalog |
| **P3** | Reverse Engineering | `resonance/acoustic_engine.py` | Malta temple acoustics analysis |
| **P3** | Reverse Engineering | `genesis/seeder.py` | Pattern-based generation |
| **P6** | Forbidden Frameworks | `render_farm/` | Material transformation |
| **P6** | Forbidden Frameworks | `printer/` | 3D printing G-code generation |
| **P7** | Billionaire Mindset | `compliance/` | Long-term building compliance |
| **P7** | Billionaire Mindset | `terracare/` | Blockchain provenance |

---

## Architecture

```
Harmonic-Balance/
├── p1-knowledge/               # Pillar 1: Sacred geometry
│   ├── genesis/
│   │   ├── geometry.py         # Hexagonal tessellation
│   │   ├── typologies.py       # Dwelling types
│   │   └── concepts/           # Sacred geometry principles
│   └── seeds/                  # Parametric seed files
├── p3-reverse-engineering/     # Pillar 3: Acoustic analysis
│   └── resonance/
│       ├── acoustic_engine.py  # Room mode calculation
│       └── tuner.py            # Schumann resonance alignment
├── p6-transformation/          # Pillar 6: Material alchemy
│   ├── render_farm/            # Visualization
│   └── printer/                # G-code generation
│       └── generic_slicer.py   # WASP/generic printer support
├── p7-abundance/               # Pillar 7: Long-term value
│   ├── compliance/             # NTC 2018, Eurocode 6
│   └── terracare/              # Blockchain anchor
├── bridge/                     # Cross-repo integration
│   ├── terracare_client.py     # Layer 1
│   └── sofie_systems_client.py # Layer 2
└── api/                        # REST API
    └── generate.py             # Main generation endpoint
```

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate dwelling with Seven Pillar alignment
python api/generate.py --typology single_pod --area 50 --frequency 7.83

# Output: P1 geometry + P3 resonance + P6 G-code + P7 compliance
```

---

## Schumann Resonance Alignment

The Earth's natural frequency (7.83 Hz) is the foundation of all Harmonic Habitats:

```python
from genesis.geometry import ResonantCavity

# Pillar 1: Create resonant space
cavity = ResonantCavity(
    fundamental_hz=7.83,  # Schumann resonance
    dimensions=(5.0, 5.0, 3.0),  # meters
    material_density=1800  # earth/crete
)

# Pillar 3: Verify alignment
if cavity.schumann_alignment():
    print("✅ Space harmonizes with Earth's frequency")
```

---

## API Structure

### Seven Pillar Convention

```
# Pillar 1: Geometry Knowledge
POST /p1/geometry/generate
GET  /p1/typologies
GET  /p1/seeds

# Pillar 3: Acoustic Analysis
POST /p3/resonance/analyze
POST /p3/room/modes
GET  /p3/schumann/alignment

# Pillar 6: Material Transformation
POST /p6/gcode/generate
POST /p6/material/optimize

# Pillar 7: Long-term Value
GET  /p7/compliance/ntc2018
GET  /p7/compliance/eurocode6
POST /p7/terracare/anchor
```

---

## Integration Points

### To Terracare-Ledger (Layer 1)
```python
# Anchor dwelling provenance on blockchain
terracare_client.anchor_dwelling(
    geometry_hash=hash_geometry,
    resonance_params=schumann_config,
    compliance_cert=compliance_report
)
```

### To sofie-systems (Layer 2)
```python
# S.O.F.I.E. resonance validation
from sofie_systems import Intelligence

Intelligence.validate_resonance(cavity.calculate_modes())
```

### To Heartware (Layer 3)
```python
# Voice-guided dwelling generation
# "Sofie, generate a 50m² single pod at 7.83 Hz"
heartware_client.generate_dwelling(voice_command)
```

---

## Supported Printers

| Printer | Pillar 6 Status | Configuration |
|---------|-----------------|---------------|
| **WASP Crane** | ✅ Optimized | `--printer wasp_crane` |
| **COBOD BOD2** | ✅ Compatible | `--printer cobod_bod2` |
| **PERI 3D** | ✅ Compatible | `--printer generic` |
| **Custom Gantry** | ⚙️ Configurable | Edit `p6-transformation/printer/generic_slicer.py` |

---

## Related Repositories

| Repo | Layer | Role |
|------|-------|------|
| [Terracare-Ledger](../Terracare-Ledger) | Layer 1 | Blockchain foundation |
| [sofie-systems](../sofie-systems) | Layer 2 | S.O.F.I.E. core engine |
| [sofie-backend](../sofie-llama-backend) | API Layer | Wellness engine |
| [Heartware](../Heartware) | Layer 3 | Voice AI companion |
| [tholos-medica](../tholos-medica) | Layer 3 | Medical devices |

---

> *"Architecture that breathes with the Earth."*  
> — S.O.F.I.E.
