# Harmonic Habitats Examples

Complete example configurations for generating dwellings with the Harmonic Habitats engine.

## Quick Start

### Using Example JSON Files

```bash
# Generate from example configuration
python api/generate.py --config examples/example_single_pod.json

# Override specific parameters
python api/generate.py --config examples/example_single_pod.json --frequency 14.3

# Generate all examples
for config in examples/*.json; do
    python api/generate.py --config "$config"
done
```

## Example Files

### example_single_pod.json

**SinglePod** - Circular dwelling for 1-2 sleepers

- **Diameter**: 6.5m
- **Height**: 3.2m  
- **Area**: 33.2m²
- **Features**: Central service core, radial layout, honeycomb walls

```bash
python api/generate.py --config examples/example_single_pod.json
```

### example_organic_family.json

**OrganicFamily** - Multi-level flowing dwelling

- **Dimensions**: 15m × 5.6m
- **Levels**: 2
- **Bedrooms**: 4
- **Features**: Spiral stairs, central gathering, flowing walls

```bash
python api/generate.py --config examples/example_organic_family.json
```

### example_cluster.json

**MultiPodCluster** - 4-pod village arrangement

- **Pods**: 4 individual units
- **Arrangement**: Circular, 12m radius
- **Total sleepers**: 6
- **Features**: Central gathering space, pod independence

```bash
python api/generate.py --config examples/example_cluster.json
```

## JSON Configuration Structure

### Required Fields

```json
{
  "typology": {
    "type": "single_pod|multi_pod_cluster|organic_family"
  },
  "geometry": {
    // Typology-specific dimensions
  },
  "printer": {
    "type": "wasp_crane|generic|cobod_bod2"
  }
}
```

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `acoustics.target_frequency_hz` | Schumann target | 7.83 |
| `materials.mix_type` | Material preset | local_earth |
| `compliance.location` | Building location | italy |
| `export_formats` | Output formats | ["gcode"] |
| `anchor_to_terracare` | Create blockchain anchor | false |

## Creating Custom Configurations

### 1. Start from Template

Copy an existing example:

```bash
cp examples/example_single_pod.json examples/my_custom_pod.json
```

### 2. Modify Parameters

Edit the JSON file with your specifications:

```json
{
  "geometry": {
    "diameter_m": 7.0,  // Changed from 6.5
    "height_m": 3.5
  },
  "printer": {
    "type": "generic"   // Changed from wasp_crane
  }
}
```

### 3. Generate

```bash
python api/generate.py --config examples/my_custom_pod.json
```

## Command Line Overrides

Command line flags override JSON values:

```bash
# Override printer type
python api/generate.py --config examples/example_single_pod.json --printer cobod

# Override frequency
python api/generate.py --config examples/example_single_pod.json --frequency 14.3

# Override output location
python api/generate.py --config examples/example_single_pod.json --output ./my_build
```

## Parameter Reference

### Geometry Parameters by Typology

#### SinglePod

| Parameter | Type | Description |
|-----------|------|-------------|
| `diameter_m` | float | Pod diameter in meters |
| `height_m` | float | Wall height in meters |
| `wall_thickness_m` | float | Wall thickness |
| `core_diameter_m` | float | Central service core diameter |

#### MultiPodCluster

| Parameter | Type | Description |
|-----------|------|-------------|
| `pod_count` | int | Number of pods (typically 4) |
| `pod_diameter_m` | float | Individual pod diameter |
| `arrangement_radius_m` | float | Radius of circular arrangement |
| `central_space_diameter_m` | float | Central gathering space diameter |

#### OrganicFamily

| Parameter | Type | Description |
|-----------|------|-------------|
| `length_m` | float | Building length |
| `width_m` | float | Building width |
| `levels` | int | Number of floors |
| `height_per_level_m` | float | Ceiling height per level |

### Material Presets

| Preset | Use Case |
|--------|----------|
| `local_earth` | Standard construction |
| `enhanced_resonance` | Frequency-tuned structures |

### Printer Types

| Type | Description |
|------|-------------|
| `wasp_crane` | WASP Crane (default) |
| `generic` | Generic Marlin printer |
| `cobod_bod2` | COBOD BOD2 gantry system |

## Output

Each generation creates:

```
outputs/YYYYMMDD_HHMMSS_typology/
├── {typology}_report.json       # Complete generation report
├── {typology}.gcode             # Printer G-code
├── printer_compatibility_report.txt  # Printer specs
├── exports/                     # 3D files (if requested)
│   ├── {typology}.stl
│   ├── {typology}.obj
│   └── {typology}.blend
└── terracare_anchor.json        # Blockchain anchor (if enabled)
```

## Tips

1. **Start Small**: Test with SinglePod before complex clusters
2. **Validate Printer**: Check compatibility report before printing
3. **Material Testing**: Always test mix before full print
4. **Version Control**: Save your JSON configs in git
5. **Iterate**: Use `--output` to keep different design versions

## See Also

- [Main README](../README.md)
- [Independent Build Guide](../docs/INDEPENDENT_BUILD.md)
- [Partnership Proposal](../docs/PARTNERSHIP_PROPOSAL.md)
