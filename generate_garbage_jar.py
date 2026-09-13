"""
Procedural 3D Toxic Garbage Jar/Barrel Generator for Blender
============================================================
Author: Expert Blender Python (bpy) Developer
Description:
    Procedurally generates a stylized, low-poly 3D model of a 'Toxic Garbage Jar/Barrel'
    representing industrial pollution and plastic waste.
    Features:
    - Corrugated heavy steel drum with reinforced hoops and warning hazard band
    - Dark, rusty weathered grey PBR metal material
    - Viscous pool of glowing neon-green radioactive liquid spilling over the rim
    - Oozing toxic drips and droplets streaming down the sides and pooling at the base
    - Discarded plastic waste chunks floating in the sludge
    - Automatically exports as 'garbage_jar.glb' to the current working directory
"""

import bpy
import math
import os
import sys

# ==============================================================================
# CONFIGURATION & PARAMETERS
# ==============================================================================
CONFIG = {
    "output_filename": "garbage_jar.glb",
    "barrel_radius": 0.45,         # Diameter ~0.9m (fits hurdle width)
    "barrel_height": 1.15,         # Exact roadblock height in game engine
    
    # Palette
    "rusty_grey": (0.22, 0.23, 0.25, 1.0),       # Weathered industrial steel
    "rust_accent": (0.42, 0.22, 0.16, 1.0),      # Heavy oxidized rust
    "neon_green_goo": (0.10, 0.98, 0.22, 1.0),   # Radioactive glowing slime
    "hazard_yellow": (0.95, 0.75, 0.08, 1.0),    # Warning caution band
    "hazard_black": (0.08, 0.09, 0.10, 1.0),     # Hazard diagonal stripes
    "plastic_debris": (0.20, 0.65, 0.95, 1.0),   # Floating discarded plastic
}


# ==============================================================================
# PBR MATERIAL HELPER
# ==============================================================================
def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0, coat=0.0):
    """Creates a PBR material compatible with Blender 4.x/5.x and glTF 2.0."""
    mat = bpy.data.materials.new(name=name)
    if hasattr(mat, "use_nodes"):
        try:
            mat.use_nodes = True
        except Exception:
            pass

    nodes = mat.node_tree.nodes if mat.node_tree else None
    if nodes:
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            if "Base Color" in bsdf.inputs:
                bsdf.inputs["Base Color"].default_value = base_color
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metallic
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = roughness
            if coat > 0 and "Coat Weight" in bsdf.inputs:
                bsdf.inputs["Coat Weight"].default_value = coat
            if emission:
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emission
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_strength

    return mat


# ==============================================================================
# PRIMITIVE HELPERS
# ==============================================================================
def add_cylinder(name, radius, depth, location, rotation=(0, 0, 0), scale=(1, 1, 1), material=None, parent=None, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    if hasattr(obj.data, "shade_smooth"):
        obj.data.shade_smooth()
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    return obj


def add_torus(name, major_rad, minor_rad, location, scale=(1, 1, 1), material=None, parent=None):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_rad,
        minor_radius=minor_rad,
        major_segments=16,
        minor_segments=8,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    if hasattr(obj.data, "shade_smooth"):
        obj.data.shade_smooth()
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    return obj


def add_sphere(name, radius, location, scale=(1, 1, 1), rotation=(0, 0, 0), material=None, parent=None, segs=14, rings=10):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segs,
        ring_count=rings,
        radius=radius,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    if hasattr(obj.data, "shade_smooth"):
        obj.data.shade_smooth()
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    return obj


def add_cube(name, size, location, rotation=(0, 0, 0), material=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    return obj


# ==============================================================================
# TOXIC GARBAGE BARREL BUILDER
# ==============================================================================
def build_toxic_garbage_jar(config):
    """Constructs the low-poly Toxic Garbage Jar/Barrel."""
    # 1. Materials
    mat_metal = create_pbr_material("RustyMetal", config["rusty_grey"], metallic=0.65, roughness=0.65)
    mat_rust = create_pbr_material("RustOxide", config["rust_accent"], metallic=0.3, roughness=0.85)
    mat_goo = create_pbr_material(
        "NeonToxicGoo",
        config["neon_green_goo"],
        metallic=0.1,
        roughness=0.08,
        coat=0.5,
        emission=config["neon_green_goo"],
        emission_strength=4.5
    )
    mat_hazard = create_pbr_material("HazardYellow", config["hazard_yellow"], roughness=0.45)
    mat_black = create_pbr_material("HazardBlack", config["hazard_black"], roughness=0.7)
    mat_plastic = create_pbr_material("PlasticWaste", config["plastic_debris"], roughness=0.3)

    # Master Root
    root = bpy.data.objects.new("ToxicGarbageJar", None)
    bpy.context.collection.objects.link(root)

    r = config["barrel_radius"]
    h = config["barrel_height"]

    # --- A. Main Steel Drum Body ---
    # Central barrel cylinder
    add_cylinder(
        "DrumBody",
        radius=r,
        depth=h,
        location=(0, 0, h / 2.0),
        material=mat_metal,
        parent=root,
        vertices=18
    )

    # Base Rim Hoop
    add_torus(
        "BaseRim",
        major_rad=r + 0.015,
        minor_rad=0.035,
        location=(0, 0, 0.05),
        material=mat_rust,
        parent=root
    )

    # Dual Middle Rib Hoops (structural steel rolling rings)
    for zh in [h * 0.35, h * 0.65]:
        add_torus(
            "MiddleRib",
            major_rad=r + 0.02,
            minor_rad=0.04,
            location=(0, 0, zh),
            material=mat_rust,
            parent=root
        )

    # Top Rim Lip (weathered edge)
    add_torus(
        "TopRim",
        major_rad=r + 0.02,
        minor_rad=0.045,
        location=(0, 0, h - 0.02),
        material=mat_rust,
        parent=root
    )

    # --- B. Warning Hazard Stripes Band ---
    # Center hazard belt
    add_cylinder(
        "HazardBand",
        radius=r + 0.008,
        depth=0.22,
        location=(0, 0, h * 0.5),
        material=mat_hazard,
        parent=root,
        vertices=18
    )

    # Hazard Chevron Strips
    num_chevrons = 6
    for i in range(num_chevrons):
        angle = (2.0 * math.pi * i) / num_chevrons
        hx = (r + 0.012) * math.cos(angle)
        hy = (r + 0.012) * math.sin(angle)
        add_cube(
            f"HazardChevron_{i}",
            size=(0.04, 0.12, 0.22),
            location=(hx, hy, h * 0.5),
            rotation=(0, math.radians(35), angle),
            material=mat_black,
            parent=root
        )

    # --- C. Bubbling Toxic Slime Pool at the Top ---
    # Slime Surface dome overflowing
    add_sphere(
        "ToxicPool",
        radius=r * 0.96,
        location=(0, 0, h - 0.04),
        scale=(1.02, 1.02, 0.38),
        material=mat_goo,
        parent=root,
        segs=16,
        rings=10
    )

    # Slime Bubbles bursting on surface
    bubble_coords = [
        ( 0.14,  0.12, h + 0.08, 0.09),
        (-0.16, -0.08, h + 0.06, 0.07),
        ( 0.05, -0.18, h + 0.05, 0.06),
        (-0.08,  0.20, h + 0.07, 0.08),
        ( 0.24, -0.10, h + 0.04, 0.05),
    ]
    for idx, (bx, by, bz, brad) in enumerate(bubble_coords):
        add_sphere(
            f"SlimeBubble_{idx}",
            radius=brad,
            location=(bx, by, bz),
            material=mat_goo,
            parent=root,
            segs=12,
            rings=8
        )

    # --- D. Overflowing Spills & Dripping Slime Streams ---
    # 1. Major Spill: Cascading down front-left quadrant
    major_spill_points = [
        # (x, y, z, rx, ry, rz)
        (-r * 0.85, -r * 0.55, h + 0.01, 0.16, 0.14, 0.08),  # Lip crest
        (-r * 0.98, -r * 0.35, h - 0.15, 0.12, 0.10, 0.22),  # Upper cascade
        (-r * 1.02, -r * 0.22, h - 0.40, 0.10, 0.09, 0.28),  # Mid flow
        (-r * 1.01, -r * 0.12, h - 0.65, 0.09, 0.08, 0.26),  # Lower stream
        (-r * 0.98, -r * 0.06, h - 0.88, 0.08, 0.07, 0.24),  # Near ground
    ]
    for idx, (sx, sy, sz, sx_r, sy_r, sz_r) in enumerate(major_spill_points):
        add_sphere(
            f"SpillBlob_{idx}",
            radius=1.0,
            location=(sx, sy, sz),
            scale=(sx_r, sy_r, sz_r),
            material=mat_goo,
            parent=root,
            segs=10,
            rings=8
        )

    # 2. Secondary Minor Drips around opposite rim
    minor_drip_angles = [0.6, 2.2, 3.8, 5.1]
    for idx, m_ang in enumerate(minor_drip_angles):
        mx = (r + 0.02) * math.cos(m_ang)
        my = (r + 0.02) * math.sin(m_ang)
        # Droplet running down
        drip_len = 0.20 + (idx % 3) * 0.12
        add_cylinder(
            f"MinorDrip_{idx}",
            radius=0.035,
            depth=drip_len,
            location=(mx, my, h - drip_len / 2.0),
            material=mat_goo,
            parent=root,
            vertices=8
        )
        # Droplet bulb at bottom of drip
        add_sphere(
            f"DropletBulb_{idx}",
            radius=0.05,
            location=(mx * 1.01, my * 1.01, h - drip_len),
            scale=(1.0, 1.0, 1.2),
            material=mat_goo,
            parent=root,
            segs=8,
            rings=6
        )

    # 3. Ground Toxic Slime Puddle spreading at the base
    add_cylinder(
        "GroundSlimePuddle",
        radius=r * 1.35,
        depth=0.03,
        location=(-0.10, -0.08, 0.015),
        scale=(1.25, 1.0, 1.0),
        material=mat_goo,
        parent=root,
        vertices=16
    )

    # --- E. Floating Plastic Waste & Debris ---
    # Crushed Plastic Water Bottle sticking out of the toxic pool
    add_cylinder(
        "PlasticBottle_Body",
        radius=0.055,
        depth=0.18,
        location=(0.18, 0.15, h + 0.09),
        rotation=(math.radians(35), math.radians(20), math.radians(-15)),
        material=mat_plastic,
        parent=root,
        vertices=8
    )
    add_cylinder(
        "PlasticBottle_Cap",
        radius=0.025,
        depth=0.04,
        location=(0.23, 0.19, h + 0.18),
        rotation=(math.radians(35), math.radians(20), math.radians(-15)),
        material=mat_hazard,
        parent=root,
        vertices=8
    )

    # Discarded Plastic Canister chunk
    add_cube(
        "PlasticChunk",
        size=(0.09, 0.09, 0.12),
        location=(-0.12, 0.18, h + 0.06),
        rotation=(math.radians(-25), math.radians(30), math.radians(45)),
        material=mat_plastic,
        parent=root
    )

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def generate_and_export():
    """Builds and exports the Toxic Garbage Jar to GLB format."""
    print("=" * 60)
    print("PRO PROCEDURAL TOXIC GARBAGE JAR GENERATOR")
    print("=" * 60)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    print("-> Assembling rusty toxic garbage jar with overflowing neon-green sludge...")
    build_toxic_garbage_jar(CONFIG)

    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, CONFIG["output_filename"])

    print(f"-> Exporting model to GLB: {export_filepath}")
    bpy.ops.export_scene.gltf(
        filepath=export_filepath,
        export_format="GLB",
        use_selection=False,
        export_materials="EXPORT",
        export_normals=True,
        export_apply=True,
        export_yup=True
    )

    if os.path.exists(export_filepath):
        size_kb = os.path.getsize(export_filepath) / 1024.0
        print(f"SUCCESS: Toxic Garbage Jar exported successfully!")
        print(f"File: {export_filepath} ({size_kb:.1f} KB)")
    else:
        print(f"ERROR: Export failed, file not found at {export_filepath}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    generate_and_export()
