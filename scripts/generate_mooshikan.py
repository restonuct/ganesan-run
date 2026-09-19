"""
Procedural 3D Mooshikan (Field Mouse with Leather Harness) for Blender
=====================================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a detailed 3D model of Mooshikan (Lord Ganesha's sacred vahana):
    - Anatomical yet stylized low-poly field mouse/rat mesh
    - Warm grey-brown fur with a soft cream underbelly
    - Tapered cute pointy snout with a delicate pink nose and glossy bead eyes
    - Large rounded mouse ears with soft pinkish interiors
    - Four agile paws in a grounded, dynamic running stance
    - Long, slender, elegantly curved pinkish tail
    - Fitted dark brown leather harness with metallic brass buckles, D-rings, and girth straps
    - Automatically exports to 'mooshikan.glb' in the current working directory.
"""

import bpy
import math
import os
import sys

# ==============================================================================
# CONFIGURATION & COLOR PALETTE
# ==============================================================================
CONFIG = {
    "output_filename": "mooshikan.glb",
    
    # Stylized Realistic Palette
    "fur_main": (0.46, 0.40, 0.35, 1.0),          # Warm Sandy Grey-Brown Fur
    "fur_belly": (0.84, 0.81, 0.76, 1.0),         # Cream Off-White Underbelly
    "nose_pink": (0.92, 0.60, 0.65, 1.0),         # Soft Pink Nose & Paw Pads
    "inner_ear_pink": (0.90, 0.62, 0.66, 1.0),    # Translucent Pink Inner Ear
    "tail_pink": (0.88, 0.62, 0.64, 1.0),         # Slender Pinkish Tail
    "eye_dark": (0.05, 0.05, 0.07, 1.0),          # Glossy Black Bead Eyes
    "eye_shine": (1.00, 1.00, 1.00, 1.0),         # Specular Highlight Sparkle
    "leather_brown": (0.28, 0.15, 0.08, 1.0),     # Fitted Dark Brown Leather Harness
    "leather_trim": (0.38, 0.22, 0.12, 1.0),      # Stitched Leather Edge
    "metal_brass": (0.88, 0.74, 0.24, 1.0),       # Metallic Buckles & D-Rings
    "saddle_pad": (0.75, 0.22, 0.15, 1.0),        # Sacred Red Trimmed Saddle Mat
}


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0):
    mat = bpy.data.materials.new(name=name)
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
            if emission and "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif emission and "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
    return mat


# ==============================================================================
# MESH GENERATION HELPERS (DIRECT BMESH FOR MAXIMUM PERFORMANCE)
# ==============================================================================
def add_sphere(name, radius, location=(0, 0, 0), scale=(1, 1, 1), rotation=(0, 0, 0), material=None, parent=None, segs=20, rings=14):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()
    return obj


def add_cylinder(name, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0), material=None, parent=None, vertices=16):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=vertices, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    obj.rotation_euler = rotation
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()
    return obj


def add_cone(name, radius1, depth, location=(0, 0, 0), rotation=(0, 0, 0), material=None, parent=None, vertices=16):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=vertices, radius1=radius1, radius2=0.0, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    obj.rotation_euler = rotation
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()
    return obj


def add_box(name, size, location=(0, 0, 0), rotation=(0, 0, 0), material=None, parent=None):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = size
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()
    return obj


# ==============================================================================
# PROCEDURAL MOOSHIKAN FIELD MOUSE BUILDER
# ==============================================================================
def build_mooshikan():
    # 1. Clean factory scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Materials
    mat_fur = create_pbr_material("Mat_MouseFur", CONFIG["fur_main"], metallic=0.02, roughness=0.65)
    mat_belly = create_pbr_material("Mat_MouseBelly", CONFIG["fur_belly"], metallic=0.02, roughness=0.7)
    mat_nose = create_pbr_material("Mat_MouseNose", CONFIG["nose_pink"], metallic=0.05, roughness=0.35)
    mat_ear_pink = create_pbr_material("Mat_InnerEar", CONFIG["inner_ear_pink"], metallic=0.02, roughness=0.45)
    mat_tail = create_pbr_material("Mat_MouseTail", CONFIG["tail_pink"], metallic=0.04, roughness=0.4)
    mat_eye = create_pbr_material("Mat_MouseEye", CONFIG["eye_dark"], metallic=0.1, roughness=0.08)
    mat_eye_shine = create_pbr_material("Mat_EyeShine", CONFIG["eye_shine"], metallic=0.0, roughness=0.05, emission=(1, 1, 1, 1), emission_strength=2.0)
    mat_leather = create_pbr_material("Mat_LeatherHarness", CONFIG["leather_brown"], metallic=0.12, roughness=0.42)
    mat_leather_trim = create_pbr_material("Mat_LeatherTrim", CONFIG["leather_trim"], metallic=0.15, roughness=0.48)
    mat_brass = create_pbr_material("Mat_HarnessBrass", CONFIG["metal_brass"], metallic=0.88, roughness=0.25)
    mat_saddle = create_pbr_material("Mat_SaddlePad", CONFIG["saddle_pad"], metallic=0.08, roughness=0.6)

    root = bpy.data.objects.new("Mooshikan_Mouse", None)
    bpy.context.collection.objects.link(root)

    # --------------------------------------------------------------------------
    # A. ANATOMICAL FIELD MOUSE BODY
    # --------------------------------------------------------------------------
    # Center torso / ribcage
    add_sphere(
        "Mouse_Torso_Chest",
        radius=0.26,
        location=(0, -0.10, 0.28),
        scale=(0.92, 1.35, 0.95),
        material=mat_fur,
        parent=root
    )

    # Rounded rear haunches (athletic curve)
    add_sphere(
        "Mouse_Haunches_Rear",
        radius=0.28,
        location=(0, 0.22, 0.30),
        scale=(1.08, 1.22, 1.04),
        material=mat_fur,
        parent=root
    )

    # Soft cream underbelly
    add_sphere(
        "Mouse_Underbelly",
        radius=0.22,
        location=(0, 0.02, 0.20),
        scale=(0.88, 1.55, 0.65),
        material=mat_belly,
        parent=root
    )

    # --------------------------------------------------------------------------
    # B. HEAD, POINTY SNOUT & CUTE FACE
    # --------------------------------------------------------------------------
    # Head base
    head_z = 0.36
    head_y = -0.42
    add_sphere(
        "Mouse_Head_Base",
        radius=0.19,
        location=(0, head_y, head_z),
        scale=(1.0, 1.15, 0.95),
        material=mat_fur,
        parent=root
    )

    # Tapered pointy muzzle / snout (cone facing forward in -Y)
    add_cone(
        "Mouse_Pointy_Snout",
        radius1=0.13,
        depth=0.28,
        location=(0, head_y - 0.20, head_z - 0.04),
        rotation=(math.radians(88), 0, 0),
        material=mat_fur,
        parent=root
    )

    # Cute pink nose tip
    add_sphere(
        "Mouse_Pink_NoseTip",
        radius=0.038,
        location=(0, head_y - 0.34, head_z - 0.045),
        scale=(1.0, 1.1, 0.9),
        material=mat_nose,
        parent=root
    )

    # Glossy Bead Eyes
    eye_x = 0.12
    for side in (-1, 1):
        add_sphere(
            f"Mouse_Eye_{'R' if side > 0 else 'L'}",
            radius=0.032,
            location=(side * eye_x, head_y - 0.12, head_z + 0.05),
            scale=(1.0, 0.6, 1.1),
            material=mat_eye,
            parent=root
        )
        add_sphere(
            f"Mouse_EyeShine_{'R' if side > 0 else 'L'}",
            radius=0.010,
            location=(side * (eye_x - 0.008), head_y - 0.135, head_z + 0.065),
            scale=(1.0, 0.5, 1.0),
            material=mat_eye_shine,
            parent=root
        )

    # Large Rounded Field Mouse Ears
    ear_x = 0.16
    for side in (-1, 1):
        # Outer Ear Shell
        add_cylinder(
            f"Mouse_Ear_Outer_{'R' if side > 0 else 'L'}",
            radius=0.14,
            depth=0.024,
            location=(side * ear_x, head_y + 0.08, head_z + 0.15),
            rotation=(math.radians(-15), side * math.radians(35), math.radians(-10)),
            material=mat_fur,
            parent=root
        )
        # Inner Ear Pink Hollow
        add_cylinder(
            f"Mouse_Ear_Inner_{'R' if side > 0 else 'L'}",
            radius=0.105,
            depth=0.028,
            location=(side * (ear_x - 0.01), head_y + 0.07, head_z + 0.15),
            rotation=(math.radians(-15), side * math.radians(35), math.radians(-10)),
            material=mat_ear_pink,
            parent=root
        )

    # Whiskers (Fine brass/white bristles)
    for side in (-1, 1):
        for w_idx, pitch in enumerate([-12, 0, 14]):
            add_cylinder(
                f"Whisker_{'R' if side > 0 else 'L'}_{w_idx}",
                radius=0.003,
                depth=0.22,
                location=(side * 0.10, head_y - 0.26, head_z - 0.04),
                rotation=(math.radians(pitch), side * math.radians(72), math.radians(10)),
                material=mat_nose,
                parent=root
            )

    # --------------------------------------------------------------------------
    # C. FOUR AGILE RUNNING PAWS
    # --------------------------------------------------------------------------
    # Front Paws (reaching forward)
    for side in (-1, 1):
        # Front Upper Leg
        add_cylinder(
            f"FrontLeg_Upper_{'R' if side > 0 else 'L'}",
            radius=0.055,
            depth=0.18,
            location=(side * 0.15, -0.22, 0.20),
            rotation=(math.radians(-25), side * math.radians(10), 0),
            material=mat_fur,
            parent=root
        )
        # Front Paw Foot with pink pads
        add_sphere(
            f"FrontPaw_{'R' if side > 0 else 'L'}",
            radius=0.055,
            location=(side * 0.17, -0.32, 0.06),
            scale=(0.9, 1.4, 0.55),
            material=mat_nose,
            parent=root
        )

    # Hind Paws (flexed haunch muscles)
    for side in (-1, 1):
        # Thigh haunch
        add_sphere(
            f"HindThigh_{'R' if side > 0 else 'L'}",
            radius=0.14,
            location=(side * 0.22, 0.22, 0.24),
            scale=(0.7, 1.2, 1.0),
            material=mat_fur,
            parent=root
        )
        # Hind Foot
        add_sphere(
            f"HindPaw_{'R' if side > 0 else 'L'}",
            radius=0.07,
            location=(side * 0.22, 0.32, 0.07),
            scale=(0.85, 1.6, 0.5),
            material=mat_nose,
            parent=root
        )

    # --------------------------------------------------------------------------
    # D. LONG PINKISH TAIL (ELEGANT GRACEFUL S-CURVE)
    # --------------------------------------------------------------------------
    # Multi-jointed slender tail extending out the back and curving up
    tail_segments = [
        # (x, y, z, radius, length, rot_x, rot_y, rot_z)
        (0.00,  0.48, 0.24, 0.034, 0.22,  -15,   0,   0),
        (0.02,  0.68, 0.21, 0.030, 0.22,  -10,   6,   4),
        (0.06,  0.88, 0.20, 0.026, 0.22,    5,  12,   8),
        (0.12,  1.07, 0.24, 0.022, 0.22,   25,  18,  12),
        (0.18,  1.23, 0.34, 0.018, 0.20,   45,  20,  15),
        (0.22,  1.34, 0.48, 0.014, 0.18,   65,  15,  10),
        (0.24,  1.38, 0.62, 0.010, 0.16,   80,   8,   5),
    ]

    for t_idx, t_data in enumerate(tail_segments):
        tx, ty, tz, trad, tlen, rx, ry, rz = t_data
        add_cylinder(
            f"Mouse_Tail_Seg_{t_idx}",
            radius=trad,
            depth=tlen,
            location=(tx, ty, tz),
            rotation=(math.radians(rx), math.radians(ry), math.radians(rz)),
            material=mat_tail,
            parent=root
        )

    # --------------------------------------------------------------------------
    # E. FITTED LEATHER HARNESS & METALLIC BUCKLES
    # --------------------------------------------------------------------------
    # 1. Front Chest Yoke Strap (wrapping around chest below neck)
    add_cylinder(
        "Harness_ChestStrap",
        radius=0.27,
        depth=0.045,
        location=(0, -0.22, 0.26),
        rotation=(math.radians(48), 0, 0),
        material=mat_leather,
        parent=root
    )

    # 2. Main Girth Strap (encircling the torso midsection)
    add_cylinder(
        "Harness_GirthStrap",
        radius=0.28,
        depth=0.055,
        location=(0, -0.02, 0.28),
        rotation=(math.radians(8), 0, 0),
        material=mat_leather,
        parent=root
    )

    # 3. Rear Flank Strap (over haunches)
    add_cylinder(
        "Harness_RearStrap",
        radius=0.29,
        depth=0.045,
        location=(0, 0.20, 0.29),
        rotation=(math.radians(-12), 0, 0),
        material=mat_leather,
        parent=root
    )

    # 4. Spine Bridging Leather Straps (Left and Right)
    for side in (-1, 1):
        add_box(
            f"Harness_SpineBridge_{'R' if side > 0 else 'L'}",
            size=(0.04, 0.44, 0.018),
            location=(side * 0.14, 0.00, 0.52),
            rotation=(math.radians(-5), 0, 0),
            material=mat_leather,
            parent=root
        )

    # 5. Padded Saddle Mounting Pad on upper spine
    add_box(
        "Harness_SaddleMount",
        size=(0.28, 0.32, 0.035),
        location=(0, 0.02, 0.54),
        rotation=(math.radians(-4), 0, 0),
        material=mat_saddle,
        parent=root
    )
    # Gold / Leather Trim around Saddle Pad
    add_box(
        "Harness_SaddleTrim",
        size=(0.30, 0.34, 0.02),
        location=(0, 0.02, 0.535),
        rotation=(math.radians(-4), 0, 0),
        material=mat_brass,
        parent=root
    )

    # 6. Polished Brass Buckles, D-Rings & Hardware
    # Central back ring connector
    add_cylinder(
        "Hardware_CenterRing",
        radius=0.045,
        depth=0.015,
        location=(0, 0.02, 0.57),
        rotation=(math.radians(90), 0, 0),
        material=mat_brass,
        parent=root
    )

    # Side Buckles on girth straps
    for side in (-1, 1):
        add_box(
            f"Hardware_Buckle_Side_{'R' if side > 0 else 'L'}",
            size=(0.02, 0.065, 0.045),
            location=(side * 0.29, -0.02, 0.28),
            rotation=(0, side * math.radians(12), 0),
            material=mat_brass,
            parent=root
        )
        # Front chest D-Ring
        add_cylinder(
            f"Hardware_ChestDRing_{'R' if side > 0 else 'L'}",
            radius=0.03,
            depth=0.012,
            location=(side * 0.16, -0.34, 0.22),
            rotation=(0, side * math.radians(35), math.radians(45)),
            material=mat_brass,
            parent=root
        )

    # Chest Medallion Emblem (Sacred Auspicious Pendant on Harness)
    add_sphere(
        "Harness_Pendant_Medallion",
        radius=0.045,
        location=(0, -0.38, 0.18),
        scale=(1.0, 0.4, 1.0),
        material=mat_brass,
        parent=root
    )

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_mooshikan():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)
    
    print("=" * 65)
    print("MOOSHIKAN (FIELD MOUSE WITH LEATHER HARNESS) GENERATOR")
    print("=" * 65)
    print("-> Assembling Mooshikan field mouse model...")
    root = build_mooshikan()
    
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
        print(f"SUCCESS: {output_filename} exported successfully! ({size_kb:.1f} KB)")
    else:
        print(f"ERROR: Export failed at {export_filepath}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    export_mooshikan()
