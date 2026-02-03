"""
harmonic-balance/render_farm/blender_bridge.py
Blender mesh generation for Harmonic Habitats.
Converts typologies to 3D meshes for visualization and export.
"""

import math
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Blender Python API (bpy) - imported when running in Blender context
try:
    import bpy
    import bmesh
    import mathutils
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False


# Material definitions
MATERIALS = {
    'raw_earth': {
        'name': 'RawEarth',
        'color': (0.768, 0.655, 0.490),  # #C4A77D
        'roughness': 0.9,
        'subsurface': 0.1,
        'displacement': 0.02
    },
    'wood_interior': {
        'name': 'WoodInterior',
        'color': (0.545, 0.353, 0.169),  # #8B5A2B
        'roughness': 0.6,
        'subsurface': 0.0
    },
    'honeycomb_surface': {
        'name': 'HoneycombSurface',
        'color': (0.7, 0.6, 0.45),
        'roughness': 0.85,
        'normal_strength': 0.5
    }
}


class BlenderMaterialSetup:
    """Setup materials for Harmonic Habitats."""
    
    @staticmethod
    def create_raw_earth_material():
        """Create raw earth material."""
        if not BLENDER_AVAILABLE:
            return None
        
        mat = bpy.data.materials.new(name='RawEarth')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default
        nodes.clear()
        
        # Output
        output = nodes.new('ShaderNodeOutputMaterial')
        
        # Principled BSDF
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (*MATERIALS['raw_earth']['color'], 1.0)
        bsdf.inputs['Roughness'].default_value = MATERIALS['raw_earth']['roughness']
        bsdf.inputs['Subsurface'].default_value = MATERIALS['raw_earth']['subsurface']
        
        # Displacement noise for earth texture
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 50.0
        noise.inputs['Detail'].default_value = 8.0
        
        # Link
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        links.new(noise.outputs['Fac'], output.inputs['Displacement'])
        
        return mat
    
    @staticmethod
    def create_wood_material():
        """Create wood interior material."""
        if not BLENDER_AVAILABLE:
            return None
        
        mat = bpy.data.materials.new(name='WoodInterior')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (*MATERIALS['wood_interior']['color'], 1.0)
        bsdf.inputs['Roughness'].default_value = MATERIALS['wood_interior']['roughness']
        
        output = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        return mat


class SinglePodMesh:
    """Generate Blender mesh for SinglePod typology."""
    
    def __init__(self, diameter: float = 6.5, height: float = 3.2,
                 wall_thickness: float = 0.30, core_diameter: float = 1.2):
        self.diameter = diameter
        self.height = height
        self.wall_thickness = wall_thickness
        self.core_diameter = core_diameter
        self.radius = diameter / 2
    
    def generate(self, add_honeycomb: bool = True) -> Dict:
        """Generate complete SinglePod mesh."""
        if not BLENDER_AVAILABLE:
            return self._generate_mock_data()
        
        # Clean scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Create main cylinder (walls)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=self.radius,
            depth=self.height,
            vertices=64,
            location=(0, 0, self.height / 2)
        )
        walls = bpy.context.active_object
        walls.name = "Pod_Walls"
        
        # Create inner cylinder (hollow)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=self.radius - self.wall_thickness,
            depth=self.height + 0.1,
            vertices=64,
            location=(0, 0, self.height / 2)
        )
        inner = bpy.context.active_object
        inner.name = "Inner_Void"
        
        # Boolean difference to create hollow walls
        mod = walls.modifiers.new(name="Boolean", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = inner
        
        # Apply boolean
        bpy.context.view_layer.objects.active = walls
        bpy.ops.object.modifier_apply(modifier="Boolean")
        
        # Delete inner void
        bpy.data.objects.remove(inner)
        
        # Create service core (boolean cut)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=self.core_diameter / 2,
            depth=self.height,
            vertices=32,
            location=(0, 0, self.height / 2)
        )
        core = bpy.context.active_object
        core.name = "Service_Core"
        
        # Boolean cut core from walls
        mod = walls.modifiers.new(name="Boolean_Core", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = core
        bpy.ops.object.modifier_apply(modifier="Boolean_Core")
        bpy.data.objects.remove(core)
        
        # Create floor
        bpy.ops.mesh.primitive_circle_add(
            radius=self.radius - self.wall_thickness / 2,
            vertices=64,
            fill_type='NGON',
            location=(0, 0, 0)
        )
        floor = bpy.context.active_object
        floor.name = "Pod_Floor"
        
        # Extrude floor
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0.2)})
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Create roof
        bpy.ops.mesh.primitive_circle_add(
            radius=self.radius,
            vertices=64,
            fill_type='NGON',
            location=(0, 0, self.height)
        )
        roof = bpy.context.active_object
        roof.name = "Pod_Roof"
        
        # Add honeycomb texture if requested
        if add_honeycomb:
            self._add_honeycomb_surface(walls)
        
        # Assign materials
        earth_mat = BlenderMaterialSetup.create_raw_earth_material()
        if earth_mat:
            for obj in [walls, floor, roof]:
                if obj.data.materials:
                    obj.data.materials[0] = earth_mat
                else:
                    obj.data.materials.append(earth_mat)
        
        # Setup camera - 3/4 exterior view
        self._setup_camera_exterior()
        
        return {
            'typology': 'single_pod',
            'objects': ['Pod_Walls', 'Pod_Floor', 'Pod_Roof'],
            'materials': ['RawEarth'],
            'camera': '3/4_exterior'
        }
    
    def _add_honeycomb_surface(self, target_object):
        """Add honeycomb displacement to surface."""
        if not BLENDER_AVAILABLE:
            return
        
        # Add displacement modifier with honeycomb pattern
        disp = target_object.modifiers.new(name="Honeycomb_Disp", type='DISPLACE')
        # In real implementation, would use texture with hexagonal pattern
        disp.strength = 0.02
        disp.mid_level = 0.5
    
    def _setup_camera_exterior(self):
        """Setup 3/4 exterior camera view."""
        if not BLENDER_AVAILABLE:
            return
        
        # Delete default camera
        if 'Camera' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Camera'])
        
        # Create new camera at 3/4 angle
        bpy.ops.object.camera_add(location=(12, -12, 8))
        camera = bpy.context.active_object
        camera.rotation_euler = (math.radians(60), 0, math.radians(45))
        bpy.context.scene.camera = camera
        
        # Add lighting
        bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
        sun = bpy.context.active_object
        sun.data.energy = 5
    
    def _generate_mock_data(self) -> Dict:
        """Generate mock data when Blender not available."""
        return {
            'typology': 'single_pod',
            'diameter': self.diameter,
            'height': self.height,
            'note': 'Blender not available - mock data only',
            'objects': ['Pod_Walls', 'Pod_Floor', 'Pod_Roof'],
            'materials': ['RawEarth'],
            'export_formats': ['.blend', '.obj', '.stl']
        }


class MultiPodClusterMesh:
    """Generate Blender mesh for MultiPodCluster typology."""
    
    def __init__(self, pod_diameter: float = 6.0, arrangement_radius: float = 12.0,
                 pod_count: int = 4, pod_height: float = 3.0):
        self.pod_diameter = pod_diameter
        self.arrangement_radius = arrangement_radius
        self.pod_count = pod_count
        self.pod_height = pod_height
        self.angle_step = 2 * math.pi / pod_count
    
    def generate(self, add_walkways: bool = True) -> Dict:
        """Generate complete MultiPodCluster mesh."""
        if not BLENDER_AVAILABLE:
            return self._generate_mock_data()
        
        # Clean scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        pod_meshes = []
        
        for i in range(self.pod_count):
            angle = i * self.angle_step
            x = self.arrangement_radius * math.cos(angle)
            y = self.arrangement_radius * math.sin(angle)
            
            # Generate individual pod
            pod = SinglePodMesh(
                diameter=self.pod_diameter,
                height=self.pod_height,
                wall_thickness=0.30,
                core_diameter=1.0
            )
            result = pod.generate(add_honeycomb=False)
            
            # Move pod to position
            for obj_name in result['objects']:
                if obj_name in bpy.data.objects:
                    obj = bpy.data.objects[obj_name]
                    obj.location = (x, y, 0)
                    # Rename
                    obj.name = f"Pod_{i+1}_{obj_name}"
                    pod_meshes.append(obj.name)
        
        # Create connecting walkways
        if add_walkways:
            self._create_walkways()
        
        # Create central gathering space
        self._create_central_space()
        
        # Setup camera
        self._setup_camera_cluster()
        
        return {
            'typology': 'multi_pod_cluster',
            'pod_count': self.pod_count,
            'objects': pod_meshes,
            'connections': ['walkways', 'central_space']
        }
    
    def _create_walkways(self):
        """Create curved walkways between pods."""
        if not BLENDER_AVAILABLE:
            return
        
        for i in range(self.pod_count):
            angle = i * self.angle_step + self.angle_step / 2
            x = self.arrangement_radius * 0.7 * math.cos(angle)
            y = self.arrangement_radius * 0.7 * math.sin(angle)
            
            # Create walkway segment
            bpy.ops.mesh.primitive_plane_add(
                size=1.5,
                location=(x, y, 0.1)
            )
            walkway = bpy.context.active_object
            walkway.name = f"Walkway_{i+1}"
            walkway.scale = (3, 0.75, 1)
            
            # Rotate to face center
            walkway.rotation_euler = (0, 0, angle)
    
    def _create_central_space(self):
        """Create central gathering space."""
        if not BLENDER_AVAILABLE:
            return
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=4.0,
            depth=0.2,
            vertices=32,
            location=(0, 0, 0.1)
        )
        central = bpy.context.active_object
        central.name = "Central_Gathering_Floor"
        
        # Add fire pit
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.8,
            depth=0.4,
            location=(0, 0, 0.2)
        )
        fire_pit = bpy.context.active_object
        fire_pit.name = "Fire_Pit"
    
    def _setup_camera_cluster(self):
        """Setup aerial camera view for cluster."""
        if not BLENDER_AVAILABLE:
            return
        
        if 'Camera' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Camera'])
        
        bpy.ops.object.camera_add(location=(0, 0, 25))
        camera = bpy.context.active_object
        camera.rotation_euler = (0, 0, 0)
        bpy.context.scene.camera = camera
    
    def _generate_mock_data(self) -> Dict:
        """Generate mock data when Blender not available."""
        return {
            'typology': 'multi_pod_cluster',
            'pod_count': self.pod_count,
            'arrangement_radius': self.arrangement_radius,
            'note': 'Blender not available - mock data only'
        }


class OrganicFamilyMesh:
    """Generate Blender mesh for OrganicFamily typology."""
    
    def __init__(self, length: float = 15.0, width: float = 5.6,
                 height_per_level: float = 2.8, levels: int = 2):
        self.length = length
        self.width = width
        self.height_per_level = height_per_level
        self.levels = levels
        self.total_height = height_per_level * levels
    
    def generate(self) -> Dict:
        """Generate flowing form with spiral staircase."""
        if not BLENDER_AVAILABLE:
            return self._generate_mock_data()
        
        # Clean scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Create flowing base shape using curves
        self._create_flowing_form()
        
        # Add spiral staircase
        self._create_spiral_staircase()
        
        # Add levels/flooring
        self._create_level_floors()
        
        # Setup camera
        self._setup_camera_section()
        
        return {
            'typology': 'organic_family',
            'length': self.length,
            'levels': self.levels,
            'features': ['flowing_form', 'spiral_staircase']
        }
    
    def _create_flowing_form(self):
        """Create flowing organic shape using curve lofting."""
        if not BLENDER_AVAILABLE:
            return
        
        # Create base curve
        curve_data = bpy.data.curves.new('FlowingCurve', 'CURVE')
        curve_data.dimensions = '3D'
        
        spline = curve_data.splines.new('NURBS')
        points = [
            (-self.length/2, -self.width/2, 0),
            (-self.length/4, self.width/2, 0),
            (0, -self.width/3, 0),
            (self.length/4, self.width/2, 0),
            (self.length/2, -self.width/2, 0)
        ]
        
        spline.points.add(len(points) - 1)
        for i, pt in enumerate(points):
            spline.points[i].co = (*pt, 1)
        
        curve_obj = bpy.data.objects.new('FlowingShape', curve_data)
        bpy.context.collection.objects.link(curve_obj)
        
        # Extrude to create volume
        curve_data.bevel_depth = self.width / 2
        curve_data.extrude = self.total_height / 2
    
    def _create_spiral_staircase(self):
        """Create spiral staircase geometry."""
        if not BLENDER_AVAILABLE:
            return
        
        stair_diameter = 1.2
        riser_height = 0.18
        total_steps = int(self.total_height / riser_height)
        
        for i in range(total_steps):
            angle = i * 0.5  # 0.5 rad per step
            z = i * riser_height
            x = (stair_diameter / 2) * math.cos(angle)
            y = (stair_diameter / 2) * math.sin(angle)
            
            bpy.ops.mesh.primitive_cube_add(
                size=0.3,
                location=(x, y, z)
            )
            step = bpy.context.active_object
            step.name = f"Stair_Step_{i+1}"
            step.scale = (1.5, 0.3, 0.05)
            step.rotation_euler = (0, 0, angle)
        
        # Central column
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.15,
            depth=self.total_height,
            location=(0, 0, self.total_height / 2)
        )
        column = bpy.context.active_object
        column.name = "Stair_Column"
    
    def _create_level_floors(self):
        """Create floor plates for each level."""
        if not BLENDER_AVAILABLE:
            return
        
        for level in range(1, self.levels + 1):
            z = level * self.height_per_level
            
            bpy.ops.mesh.primitive_plane_add(
                size=1,
                location=(0, 0, z)
            )
            floor = bpy.context.active_object
            floor.name = f"Level_{level}_Floor"
            floor.scale = (self.length / 2, self.width / 2, 1)
    
    def _setup_camera_section(self):
        """Setup cross-section interior camera view."""
        if not BLENDER_AVAILABLE:
            return
        
        if 'Camera' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Camera'])
        
        bpy.ops.object.camera_add(location=(self.length / 2, 0, self.total_height / 2))
        camera = bpy.context.active_object
        camera.rotation_euler = (math.radians(90), 0, math.radians(90))
        bpy.context.scene.camera = camera
    
    def _generate_mock_data(self) -> Dict:
        """Generate mock data when Blender not available."""
        return {
            'typology': 'organic_family',
            'length': self.length,
            'width': self.width,
            'levels': self.levels,
            'note': 'Blender not available - mock data only'
        }


class BlenderExporter:
    """Export Blender scenes to various formats."""
    
    @staticmethod
    def export_blend(filepath: str):
        """Save as .blend file."""
        if BLENDER_AVAILABLE:
            bpy.ops.wm.save_as_mainfile(filepath=filepath)
        else:
            print(f"[MOCK] Would save .blend to {filepath}")
    
    @staticmethod
    def export_obj(filepath: str):
        """Export to OBJ format."""
        if BLENDER_AVAILABLE:
            bpy.ops.export_scene.obj(
                filepath=filepath,
                use_selection=False,
                use_materials=True
            )
        else:
            print(f"[MOCK] Would export .obj to {filepath}")
    
    @staticmethod
    def export_stl(filepath: str, for_wasp: bool = True):
        """Export to STL for WASP slicer."""
        if BLENDER_AVAILABLE:
            # Select all mesh objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    obj.select_set(True)
            
            bpy.ops.export_mesh.stl(
                filepath=filepath,
                use_selection=True,
                ascii=False
            )
        else:
            print(f"[MOCK] Would export .stl to {filepath} (for WASP: {for_wasp})")
    
    @staticmethod
    def export_all(base_path: str, basename: str) -> Dict:
        """Export all formats."""
        results = {}
        
        blend_path = f"{base_path}/{basename}.blend"
        BlenderExporter.export_blend(blend_path)
        results['blend'] = blend_path
        
        obj_path = f"{base_path}/{basename}.obj"
        BlenderExporter.export_obj(obj_path)
        results['obj'] = obj_path
        
        stl_path = f"{base_path}/{basename}.stl"
        BlenderExporter.export_stl(stl_path, for_wasp=True)
        results['stl'] = stl_path
        
        return results


def generate_typology_mesh(typology: str, export_path: str = None, **params) -> Dict:
    """
    Generate mesh for any typology and export.
    
    Args:
        typology: 'single_pod', 'multi_pod_cluster', 'organic_family'
        export_path: Directory to save exports
        **params: Typology-specific parameters
    
    Returns:
        Export file paths
    """
    if typology == 'single_pod':
        generator = SinglePodMesh(
            diameter=params.get('diameter', 6.5),
            height=params.get('height', 3.2)
        )
    elif typology == 'multi_pod_cluster':
        generator = MultiPodClusterMesh(
            pod_diameter=params.get('pod_diameter', 6.0),
            arrangement_radius=params.get('arrangement_radius', 12.0),
            pod_count=params.get('pod_count', 4)
        )
    elif typology == 'organic_family':
        generator = OrganicFamilyMesh(
            length=params.get('length', 15.0),
            width=params.get('width', 5.6),
            levels=params.get('levels', 2)
        )
    else:
        raise ValueError(f"Unknown typology: {typology}")
    
    # Generate mesh
    result = generator.generate()
    
    # Export if path provided
    if export_path:
        Path(export_path).mkdir(parents=True, exist_ok=True)
        exports = BlenderExporter.export_all(export_path, typology)
        result['exports'] = exports
    
    return result


if __name__ == "__main__":
    print("=== Blender Bridge Test (Mock Mode) ===")
    print(f"Blender available: {BLENDER_AVAILABLE}")
    
    result = generate_typology_mesh('single_pod', diameter=6.5)
    print(f"SinglePod: {result}")
    
    result = generate_typology_mesh('multi_pod_cluster', pod_count=4)
    print(f"MultiPodCluster: {result}")
    
    result = generate_typology_mesh('organic_family', levels=2)
    print(f"OrganicFamily: {result}")
