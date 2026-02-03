# Independent Build Guide

**Use Harmonic Habitats without WASP partnership**

This guide explains how to use Harmonic Habitats software with any construction method—whether you have access to a large-format 3D printer, CNC equipment, or prefer traditional construction techniques.

---

## Table of Contents

1. [Export Formats](#export-formats)
2. [3D Printing Options](#3d-printing-options)
3. [CNC Manufacturing](#cnc-manufacturing)
4. [Manual Construction](#manual-construction)
5. [Hybrid Approaches](#hybrid-approaches)
6. [Printer Compatibility](#printer-compatibility)
7. [Troubleshooting](#troubleshooting)

---

## Export Formats

Our software exports to industry-standard formats compatible with any manufacturing workflow:

### 3D Models

| Format | Extension | Use Case |
|--------|-----------|----------|
| **STL** | `.stl` | Universal 3D printing, slicer input |
| **OBJ** | `.obj` | 3D modeling, texturing, visualization |
| **Blender** | `.blend` | Full scene with materials, cameras, lighting |
| **GLTF** | `.gltf` | Web visualization, AR/VR |

### G-code

| Type | Compatibility |
|------|---------------|
| **Standard G-code** | Any Marlin-based printer |
| **Arc commands (G2/G3)** | WASP, COBOD, most industrial printers |
| **Linear only (G1)** | Universal fallback |

### Documentation

- **PDF drawings** (coming soon)
- **Material lists** (`printer/materials.py`)
- **Compliance reports** (`compliance/eurocodes.py`)

---

## 3D Printing Options

### Option 1: WASP Crane (Optimized)

Our default configuration. See [PARTNERSHIP_PROPOSAL.md](./PARTNERSHIP_PROPOSAL.md) for partnership benefits.

```bash
python api/generate.py --typology single_pod --printer wasp_crane
```

### Option 2: Generic Large-Format Printer

Works with any gantry or robotic arm printer:

```bash
python api/generate.py --typology single_pod --printer generic
```

**Compatible Systems:**
- COBOD BOD2
- PERI 3D Construction
- ICON Vulcan
- Apis Cor
- Custom gantry systems

**Adjustments needed:**
- Edit `printer/generic_slicer.py` for your printer's reach/height
- Calibrate layer height to your nozzle diameter
- Adjust print speeds based on your extrusion system

### Option 3: Export to Slicer

Generate STL and use any slicer:

```bash
python api/generate.py --typology single_pod --export stl
```

**Then use:**
- **PrusaSlicer** (with earth printing mods)
- **Cura** (custom material profiles)
- **Simplify3D**
- **Slic3r**

**Earth Printing Slicer Settings:**
```
Layer height: 15-25mm
Nozzle diameter: 30-50mm
Print speed: 30-60mm/s
Material: Clay/earth (non-heated)
Retraction: Disabled or minimal
```

---

## CNC Manufacturing

### Large-Format CNC Milling

Export `.stl` → CNC mill from foam, wood, or composite:

**Workflow:**
1. Generate geometry: `python api/generate.py --typology single_pod --export stl`
2. Import to CAM software (Fusion 360, Vectric, etc.)
3. Generate toolpaths for foam cutting
4. Mill formwork sections
5. Use as molds for rammed earth or concrete

### Robotic Arm Fabrication

ABB, KUKA, UR robotic arms with milling heads:

- Export `.obj` for import to RoboDK or similar
- Generate toolpaths for subtractive or additive processes
- Scale to your robot's work envelope

---

## Manual Construction

### Method 1: 3D Printed Formwork

**Most accessible approach.**

1. **Generate scaled formwork:**
   ```bash
   python api/generate.py --typology single_pod --export stl
   ```

2. **Print formwork sections** on smaller 3D printer:
   - Scale down to 1:10 or 1:20 for desktop FDM printers
   - Use as visualization and planning models
   - Scale to 1:1 sections for reusable plastic formwork

3. **Assemble formwork** on site:
   - Use printed sections as molds
   - Fill with rammed earth, cob, or concrete
   - Reuse formwork for multiple sections

**Recommended desktop printers:**
- Prusa i3 MK3S+ (for 1:10 models)
- Creality CR-10 (for larger sections)
- Any FDM printer ≥220mm build volume

### Method 2: CNC-Cut Wooden Formwork

Export geometry → CNC router → plywood formwork:

**Steps:**
1. Unroll/unfold curved surfaces in CAD
2. Generate flat patterns
3. CNC cut from plywood/OSB
4. Assemble on site
5. Fill with earth mix

### Method 3: Traditional Masonry/Cob

Use our geometry as **design guides** for hand-building:

- Print 2D plans and sections (coming soon)
- Follow dimensions and proportions
- Build with adobe, cob, rammed earth, or stone
- Maintain Schumann resonance dimensions for acoustic benefit

---

## Hybrid Approaches

### Approach 1: Printed Walls + Conventional Roof

**Most cost-effective for first builds:**

1. Print earth walls only (up to top plate height)
2. Install conventional timber or steel roof structure
3. Any roofing material (tile, metal, membrane)

**Benefits:**
- Reduced print time and material
- Standard roof weatherproofing
- Easier permitting in some jurisdictions

### Approach 2: Structural Shell + Infill

1. Print structural walls with voids
2. Hand-place insulation in voids
3. Apply earthen or lime plaster finish

### Approach 3: Modular Pods

1. Print wall sections separately
2. Transport and crane-lift into position
3. Join sections on foundation

---

## Printer Compatibility

### Supported Printers

| Printer | Status | Notes |
|---------|--------|-------|
| **WASP Crane** | ✅ Optimized | Default settings, tested configurations |
| **COBOD BOD2** | ✅ Compatible | Adjust for gantry-style movements |
| **PERI 3D** | ✅ Compatible | Standard G-code compatible |
| **Custom Gantry** | ⚙️ Configurable | Edit `printer/generic_slicer.py` |
| **Custom Robot** | ⚙️ Configurable | May need custom post-processor |
| **Desktop FDM** | ⚠️ Limited | For formwork/models only |

### Testing Your Printer

Generate a test cylinder:

```bash
python -c "
from printer.generic_slicer import GenericSlicer, PrinterConfig
config = PrinterConfig.custom(
    name='My Printer',
    reach_radius_m=2.0,
    max_height_m=2.5,
    nozzle_diameter_mm=30,
    default_layer_height_mm=15,
    max_print_speed_mm_s=40
)
slicer = GenericSlicer(config)
print(slicer.generate_circular_wall(diameter=1.0, height=0.5))
" > test_print.gcode
```

Print the test cylinder and verify:
- [ ] Clean arc movements
- [ ] Consistent layer height
- [ ] No gaps or surges in extrusion
- [ ] Structural integrity after curing

### Creating Custom Configurations

Edit `printer/generic_slicer.py` to add your printer:

```python
@classmethod
def my_custom_printer(cls) -> 'PrinterConfig':
    return cls(
        name="My Custom Printer",
        reach_radius_m=4.0,        # Your reach
        max_height_m=3.0,          # Your height
        nozzle_diameter_mm=45.0,   # Your nozzle
        default_layer_height_mm=22.0,
        max_print_speed_mm_s=45.0,
        firmware="Marlin"
    )
```

Then use:
```bash
python api/generate.py --typology single_pod --printer my_custom
```

---

## Troubleshooting

### G-code Issues

| Problem | Solution |
|---------|----------|
| Arcs not smooth | Use `--printer generic` for G1-only output |
| Moves too fast | Reduce speed in `generic_slicer.py` |
| Extrusion inconsistent | Adjust flow rate in G-code header |
| Printer doesn't recognize | Check firmware compatibility (Marlin vs. RepRap) |

### Material Issues

| Problem | Solution |
|---------|----------|
| Mix too dry | Increase water by 1-2% |
| Mix too wet | Add more clay/sand binder |
| Cracking during curing | Reduce clay content, add more sand |
| Poor layer adhesion | Increase moisture, reduce layer height |

### Scale Issues

| Problem | Solution |
|---------|----------|
| Structure too large for printer | Use modular approach, print in sections |
| Desktop printer too small | Export to CNC service or use manual formwork |
| Height exceeds printer | Build in two lifts with intermediate curing |

---

## Community and Support

### Getting Help

- **GitHub Issues:** Report technical problems
- **Discussions:** Share your build experience
- **Documentation:** Check latest docs in repository

### Contributing

Share your independent build:
- Fork the repository
- Document your printer configuration
- Submit PR with new `PrinterConfig`
- Share photos and lessons learned

---

## Summary

**You do NOT need WASP partnership to use Harmonic Habitats.**

Our open architecture supports:
- ✅ Any Marlin-compatible 3D printer
- ✅ CNC manufacturing
- ✅ Traditional hand-building
- ✅ Hybrid construction methods

**Start building today:**
1. Export geometry in your preferred format
2. Adapt to your equipment and skills
3. Build locally, sustainably, affordably

The future of housing is open source.

---

*For partnership opportunities with WASP, see [PARTNERSHIP_PROPOSAL.md](./PARTNERSHIP_PROPOSAL.md)*
