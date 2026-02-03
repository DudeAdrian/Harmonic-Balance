# Harmonic-Balance

**Sacred geometry generation for resonant dwellings.**

Private repository for Harmonic Habitats. 
Computational temple architecture for the modern age.

## Genesis

- Hexagonal tessellation (bee wisdom)
- Golden ratio proportions (divine harmony)
- Schumann resonance alignment (7.83 Hz)
- Malta temple acoustics (ancient healing)

## Typologies

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
- **Application**: Small community or family compound

### OrganicFamily
Large flowing dwelling for extended family:
- **Dimensions**: 15m x 5.6m footprint
- **Levels**: 2 levels with spiral stairs
- **Bedrooms**: 4 bedrooms
- **Features**: Central gathering space, organic flowing form, multi-level
- **Footprint**: 84m²

### Technical Layout
Floor plan documentation system:
- Letter-coded zones (A-H)
- Zone A: Central service core
- Specific square meterages per zone
- Compliance-ready documentation

## Compliance

### Italy NTC 2018
- Seismic classification for all Italian zones (Z1-Z4)
- Design seismic acceleration calculations
- Structural behavior factors for 3D printed earth (q=1.8)

### Eurocode 6 (Masonry/Earth Structures)
- Compressive strength verification
- Slenderness checks for honeycomb walls
- Minimum wall thickness: 300mm base (400mm Z1 seismic)

### Eurocode 1 (Actions)
- Self-weight calculations for printed earth walls
- Wind load calculations (Italian zones)
- Snow load by altitude and zone

### nZEB Standards
- Energy Performance Index (EPh) targets by climate zone
- Thermal transmittance calculations for earth walls
- EU Directive 2010/31/EU compliance

| Climate Zone | Target EPh (kWh/m²/y) |
|--------------|----------------------|
| A | 35 |
| B | 40 |
| C | 45 |
| D | 50 |
| E | 55 |
| F | 60 |

## WASP Printer Specifications

### 3D WASP Crane WASP (Italy)
- **Technology**: Raw earth extrusion (RMDC - Raw Earth Material)
- **Layer height**: 50mm typical
- **Print speed**: 1500mm/min
- **Material**: Local earth with 10-15% stabilizer
- **Wall thickness**: 300-400mm (depending on seismic zone)
- **Max height**: 3.5m per module

### Print Parameters
```python
wall_thickness = 0.35  # 350mm for layered earth
layer_height = 0.05    # 50mm layers
print_speed = 1500     # mm/min
material = "local_earth_with_stabilizer"
```

## Usage

```python
from genesis.typologies import SinglePod, MultiPodCluster, OrganicFamily
from genesis.geometry import create_harmonic_habitat

# Generate single pod
pod = SinglePod(diameter=6.5)
result = pod.generate()

# Generate 4-pod cluster
cluster = MultiPodCluster(pod_count=4, arrangement_radius=12.0)
result = cluster.generate()

# Generate organic family dwelling
family = OrganicFamily(length=15.0, width=5.6, levels=2)
result = family.generate()

# Legacy habitat generation
habitat = create_harmonic_habitat(footprint_area=150, target_frequency=7.83, levels=2)
```

## Structure

```
genesis/       - Sacred geometry core & typologies
├── geometry.py    - Base geometry classes
├── seeder.py      - Image recognition & parametric DNA
└── typologies.py  - SinglePod, MultiPodCluster, OrganicFamily

resonance/     - Acoustic tuning
├── tuner.py       - Schumann resonance alignment

compliance/    - Italy/EU compliance
└── eurocodes.py   - NTC 2018, EC6, EC1, nZEB

terracare/     - Blockchain provenance
render_farm/   - Visualization pipeline
api/           - REST API endpoints
```

## Partnership

**3D WASP (Italy)** - Raw earth printing technology
- Location: Massa Lombarda, Ravenna
- Technology: Crane WASP modular 3D printing
- Material: Raw earth, locally sourced

## Frequency

Everything resonates at **7.83 Hz**.

The Schumann resonance - Earth's heartbeat.
