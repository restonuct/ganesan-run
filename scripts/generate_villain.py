"""
Procedural 3D Polluter Villain Runner Generator for Blender
===========================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a stylized, low-poly villain runner character:
    - Dark charcoal-grey hoodie with neon-green/cyan biohazard trim along hood and sleeves
    - Lower-face tactical respirator half-mask with twin air-filter cartridges
    - Upper tinted visor goggles with sinister specular reflection
    - Athletic sprinting pose with dynamic bent limbs
    - Detailed metallic toxic waste canister backpack with industrial ribs, pressure gauge,
      and dripping, glowing radioactive green sludge (emissive PBR shader)
    - Automatically exports to 'villain.glb' in the current working directory.
"""

import bpy
import math
import os
import sys

# ==============================================================================
# CONFIGURATION & COLOR PALETTE
# ==============================================================================
CONFIG = {
    "output_filename": "villain.glb",
    "total_height": 1.85,
    
    # Stylized Cyber-Polluter Palette
    "hoodie_charcoal": (0.12, 0.13, 0.16, 1.0),   # Dark Charcoal-Grey Matte Fabric
    "hoodie_inner": (0.06, 0.07, 0.08, 1.0),      # Dark Hood Shadow Interior
    "pants_slate": (0.16, 0.18, 0.22, 1.0),       # Reinforced Cargo Pants
    "boots_black": (0.08, 0.08, 0.10, 1.0),       # Heavy Duty Combat Sneakers
    "mask_dark": (0.20, 0.22, 0.26, 1.0),         # Half-Mask Respirator Shell
    "filter_metal": (0.42, 0.45, 0.50, 1.0),      # Filter Cartridge Metal
    "goggles_tint": (0.05, 0.85, 0.70, 1.0),      # Cyan-Tinted Visor
    "canister_steel": (0.50, 0.54, 0.58, 1.0),    # Brushed Steel Toxic Drum
    "canister_cap": (0.80, 0.65, 0.15, 1.0),      # Brass Pressure Valve
    "bio_trim_neon": (0.05, 1.00, 0.45, 1.0),     # Neon-Green / Cyan Biohazard Trim
    "toxic_sludge": (0.15, 1.00, 0.18, 1.0),      # Glowing Radioactive Green Liquid
    "strap_leather": (0.10, 0.10, 0.12, 1.0),     # Backpack Harness Straps
    "hazard_yellow": (0.95, 0.80, 0.05, 1.0),     # Biohazard Label
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
# DIRECT BMESH MESH GENERATORS
# ==============================================================================
def add_sphere(name, radius, location=(0, 0, 0), scale=(1, 1, 1), rotation=(0, 0, 0), material=None, parent=None, segs=16, rings=12):
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
# PROCEDURAL POLLUTER VILLAIN BUILDER
# ==============================================================================
def build_villain():
    # 1. Clean factory scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Materials
    mat_hoodie = create_pbr_material("Mat_HoodieCharcoal", CONFIG["hoodie_charcoal"], metallic=0.04, roughness=0.75)
    mat_hood_inner = create_pbr_material("Mat_HoodInner", CONFIG["hoodie_inner"], metallic=0.0, roughness=0.9)
    mat_pants = create_pbr_material("Mat_PantsSlate", CONFIG["pants_slate"], metallic=0.08, roughness=0.65)
    mat_boots = create_pbr_material("Mat_BootsBlack", CONFIG["boots_black"], metallic=0.15, roughness=0.45)
    mat_mask = create_pbr_material("Mat_RespiratorMask", CONFIG["mask_dark"], metallic=0.25, roughness=0.35)
    mat_filter = create_pbr_material("Mat_FilterMetal", CONFIG["filter_metal"], metallic=0.75, roughness=0.3)
    mat_goggles = create_pbr_material("Mat_GogglesTint", CONFIG["goggles_tint"], metallic=0.2, roughness=0.1, emission=CONFIG["goggles_tint"], emission_strength=1.5)
    mat_canister = create_pbr_material("Mat_CanisterSteel", CONFIG["canister_steel"], metallic=0.85, roughness=0.28)
    mat_cap = create_pbr_material("Mat_CanisterBrass", CONFIG["canister_cap"], metallic=0.88, roughness=0.3)
    mat_trim = create_pbr_material("Mat_BioTrimNeon", CONFIG["bio_trim_neon"], metallic=0.1, roughness=0.2, emission=CONFIG["bio_trim_neon"], emission_strength=2.8)
    mat_sludge = create_pbr_material("Mat_ToxicSludge", CONFIG["toxic_sludge"], metallic=0.05, roughness=0.15, emission=CONFIG["toxic_sludge"], emission_strength=3.5)
    mat_straps = create_pbr_material("Mat_BackpackStraps", CONFIG["strap_leather"], metallic=0.1, roughness=0.6)
    mat_hazard = create_pbr_material("Mat_HazardLabel", CONFIG["hazard_yellow"], metallic=0.1, roughness=0.4, emission=CONFIG["hazard_yellow"], emission_strength=1.2)

    root = bpy.data.objects.new("Polluter_Villain", None)
    bpy.context.collection.objects.link(root)

    # --------------------------------------------------------------------------
    # A. ATHLETIC RUNNER SPRINTING POSE (TORSO & LEGS)
    # --------------------------------------------------------------------------
    # Torso leaning forward slightly into the sprint (pitching forward by ~12 deg)
    torso_z = 1.05
    torso_lean = math.radians(12)

    # Upper Torso (Charcoal Hoodie)
    add_box(
        "Torso_Hoodie",
        size=(0.48, 0.32, 0.52),
        location=(0, -0.06, torso_z),
        rotation=(torso_lean, 0, 0),
        material=mat_hoodie,
        parent=root
    )

    # Kangaroo Pouch Pocket on hoodie front
    add_box(
        "Hoodie_Pouch_Pocket",
        size=(0.34, 0.08, 0.18),
        location=(0, -0.22, torso_z - 0.12),
        rotation=(torso_lean, 0, 0),
        material=mat_hoodie,
        parent=root
    )

    # Neon-Green Biohazard Vertical Accent Lines on hoodie chest
    for side in (-1, 1):
        add_box(
            f"Hoodie_ChestStripe_{'R' if side > 0 else 'L'}",
            size=(0.024, 0.02, 0.40),
            location=(side * 0.16, -0.22, torso_z + 0.04),
            rotation=(torso_lean, 0, 0),
            material=mat_trim,
            parent=root
        )

    # Pelvis & Waist
    add_box(
        "Pelvis_Pants",
        size=(0.42, 0.28, 0.20),
        location=(0, -0.02, torso_z - 0.30),
        rotation=(torso_lean, 0, 0),
        material=mat_pants,
        parent=root
    )

    # Dynamic Running Legs (Left Leg forward, Right Leg trailing in full stride)
    # 1. Left Leg (Swinging forward)
    add_cylinder(
        "Leg_Thigh_L",
        radius=0.11,
        depth=0.38,
        location=(-0.16, -0.16, 0.62),
        rotation=(math.radians(-32), 0, 0),
        material=mat_pants,
        parent=root
    )
    add_cylinder(
        "Leg_Shin_L",
        radius=0.09,
        depth=0.36,
        location=(-0.16, -0.26, 0.30),
        rotation=(math.radians(22), 0, 0),
        material=mat_pants,
        parent=root
    )
    # Left Sneaker
    add_box(
        "Foot_Boot_L",
        size=(0.14, 0.30, 0.14),
        location=(-0.16, -0.32, 0.12),
        rotation=(math.radians(10), 0, 0),
        material=mat_boots,
        parent=root
    )
    # Neon Green Sneaker Sole Trim
    add_box(
        "Boot_Sole_L",
        size=(0.145, 0.31, 0.03),
        location=(-0.16, -0.32, 0.05),
        rotation=(math.radians(10), 0, 0),
        material=mat_trim,
        parent=root
    )

    # 2. Right Leg (Trailing back in full extension)
    add_cylinder(
        "Leg_Thigh_R",
        radius=0.11,
        depth=0.38,
        location=(0.16, 0.14, 0.60),
        rotation=(math.radians(38), 0, 0),
        material=mat_pants,
        parent=root
    )
    add_cylinder(
        "Leg_Shin_R",
        radius=0.09,
        depth=0.36,
        location=(0.16, 0.36, 0.38),
        rotation=(math.radians(-42), 0, 0),
        material=mat_pants,
        parent=root
    )
    # Right Sneaker (Pushed back)
    add_box(
        "Foot_Boot_R",
        size=(0.14, 0.30, 0.14),
        location=(0.16, 0.52, 0.22),
        rotation=(math.radians(-25), 0, 0),
        material=mat_boots,
        parent=root
    )
    add_box(
        "Boot_Sole_R",
        size=(0.145, 0.31, 0.03),
        location=(0.16, 0.52, 0.15),
        rotation=(math.radians(-25), 0, 0),
        material=mat_trim,
        parent=root
    )

    # --------------------------------------------------------------------------
    # B. DYNAMIC SPRINTING ARMS & HOODIE SLEEVES
    # --------------------------------------------------------------------------
    # Right Arm: Pumping forward
    add_cylinder(
        "Arm_Upper_R",
        radius=0.085,
        depth=0.34,
        location=(0.30, -0.16, torso_z + 0.08),
        rotation=(math.radians(-45), 0, math.radians(-15)),
        material=mat_hoodie,
        parent=root
    )
    add_cylinder(
        "Arm_Forearm_R",
        radius=0.075,
        depth=0.30,
        location=(0.34, -0.32, torso_z - 0.06),
        rotation=(math.radians(45), 0, 0),
        material=mat_hoodie,
        parent=root
    )
    # Right Glove Fist
    add_sphere(
        "Glove_Fist_R",
        radius=0.08,
        location=(0.34, -0.42, torso_z + 0.06),
        material=mat_boots,
        parent=root
    )
    # Neon Green Sleeve Racing Stripe on Right Arm
    add_box(
        "SleeveStripe_R",
        size=(0.02, 0.32, 0.02),
        location=(0.38, -0.16, torso_z + 0.10),
        rotation=(math.radians(-45), 0, math.radians(-15)),
        material=mat_trim,
        parent=root
    )

    # Left Arm: Sweeping back in sprint stride
    add_cylinder(
        "Arm_Upper_L",
        radius=0.085,
        depth=0.34,
        location=(-0.30, 0.08, torso_z + 0.08),
        rotation=(math.radians(42), 0, math.radians(15)),
        material=mat_hoodie,
        parent=root
    )
    add_cylinder(
        "Arm_Forearm_L",
        radius=0.075,
        depth=0.30,
        location=(-0.34, 0.26, torso_z - 0.04),
        rotation=(math.radians(-35), 0, 0),
        material=mat_hoodie,
        parent=root
    )
    add_sphere(
        "Glove_Fist_L",
        radius=0.08,
        location=(-0.34, 0.38, torso_z - 0.14),
        material=mat_boots,
        parent=root
    )
    add_box(
        "SleeveStripe_L",
        size=(0.02, 0.32, 0.02),
        location=(-0.38, 0.08, torso_z + 0.10),
        rotation=(math.radians(42), 0, math.radians(15)),
        material=mat_trim,
        parent=root
    )

    # --------------------------------------------------------------------------
    # C. HOODED HEAD & BIOHAZARD TRIM
    # --------------------------------------------------------------------------
    head_z = torso_z + 0.42
    head_y = -0.12

    # Outer Pulled-Up Hoodie Shell
    add_sphere(
        "Hood_Outer_Shell",
        radius=0.26,
        location=(0, head_y, head_z),
        scale=(1.05, 1.15, 1.12),
        rotation=(torso_lean, 0, 0),
        material=mat_hoodie,
        parent=root
    )

    # Inner Hood Dark Face Cavity
    add_sphere(
        "Hood_Inner_Void",
        radius=0.22,
        location=(0, head_y - 0.06, head_z),
        scale=(0.95, 0.95, 1.0),
        material=mat_hood_inner,
        parent=root
    )

    # Neon Green Biohazard Trim along the Hood Opening Rim
    add_cylinder(
        "Hood_Neon_Trim_Rim",
        radius=0.24,
        depth=0.03,
        location=(0, head_y - 0.14, head_z),
        rotation=(math.radians(90) + torso_lean, 0, 0),
        material=mat_trim,
        parent=root
    )

    # --------------------------------------------------------------------------
    # D. HALF-MASK TACTICAL RESPIRATOR & VISOR GOGGLES
    # --------------------------------------------------------------------------
    # Lower-Face Respirator Shell (covering mouth, nose bridge, jaw)
    add_box(
        "Respirator_HalfMask",
        size=(0.20, 0.15, 0.14),
        location=(0, head_y - 0.16, head_z - 0.08),
        rotation=(torso_lean, 0, 0),
        material=mat_mask,
        parent=root
    )

    # Twin Cylindrical Air Filter Cartridges on the sides
    for side in (-1, 1):
        add_cylinder(
            f"Filter_Cartridge_{'R' if side > 0 else 'L'}",
            radius=0.055,
            depth=0.08,
            location=(side * 0.13, head_y - 0.18, head_z - 0.09),
            rotation=(0, side * math.radians(90), 0),
            material=mat_filter,
            parent=root
        )
        # Glowing Green Filter Intake Ring
        add_cylinder(
            f"Filter_GlowRing_{'R' if side > 0 else 'L'}",
            radius=0.045,
            depth=0.084,
            location=(side * 0.13, head_y - 0.18, head_z - 0.09),
            rotation=(0, side * math.radians(90), 0),
            material=mat_sludge,
            parent=root
        )

    # Cybernetic Visor / Tactical Goggles across the eyes
    add_box(
        "Visor_Goggles",
        size=(0.22, 0.08, 0.065),
        location=(0, head_y - 0.17, head_z + 0.04),
        rotation=(torso_lean, 0, 0),
        material=mat_goggles,
        parent=root
    )

    # --------------------------------------------------------------------------
    # E. METALLIC TOXIC WASTE CANISTER BACKPACK LEAKING GREEN SLUDGE
    # --------------------------------------------------------------------------
    pack_z = torso_z + 0.02
    pack_y = 0.18

    # Shoulder Harness Straps
    for side in (-1, 1):
        add_box(
            f"HarnessStrap_{'R' if side > 0 else 'L'}",
            size=(0.06, 0.32, 0.025),
            location=(side * 0.16, -0.06, torso_z + 0.14),
            rotation=(math.radians(52), 0, 0),
            material=mat_straps,
            parent=root
        )

    # Main Metallic Toxic Waste Barrel Canister
    canister = add_cylinder(
        "Toxic_Waste_Canister",
        radius=0.18,
        depth=0.55,
        location=(0, pack_y, pack_z),
        rotation=(math.radians(-10), 0, 0),
        material=mat_canister,
        parent=root
    )

    # Canister Reinforcement Ribs (Industrial Steel Rings)
    for rz in (-0.18, 0.0, 0.18):
        add_cylinder(
            f"Canister_Rib_{rz}",
            radius=0.19,
            depth=0.035,
            location=(0, pack_y, pack_z + rz),
            rotation=(math.radians(-10), 0, 0),
            material=mat_canister,
            parent=root
        )

    # Top Heavy Industrial Pressure Valve Cap
    add_cylinder(
        "Canister_Top_Cap",
        radius=0.10,
        depth=0.08,
        location=(0, pack_y - 0.04, pack_z + 0.30),
        rotation=(math.radians(-10), 0, 0),
        material=mat_cap,
        parent=root
    )

    # Top Exhaust Chimney Pipe (Venting toxic green vapor)
    add_cylinder(
        "Canister_Exhaust_Pipe",
        radius=0.04,
        depth=0.16,
        location=(0.08, pack_y - 0.03, pack_z + 0.38),
        rotation=(math.radians(-15), math.radians(12), 0),
        material=mat_canister,
        parent=root
    )

    # Biohazard Hazard Trefoil Decal Plaque on the rear face
    add_box(
        "Biohazard_Plaque",
        size=(0.14, 0.015, 0.14),
        location=(0, pack_y + 0.185, pack_z),
        rotation=(math.radians(-10), 0, 0),
        material=mat_hazard,
        parent=root
    )

    # Pressure Gauge Dial on the canister side
    add_cylinder(
        "Pressure_Gauge",
        radius=0.05,
        depth=0.03,
        location=(-0.18, pack_y, pack_z + 0.14),
        rotation=(0, math.radians(-90), 0),
        material=mat_cap,
        parent=root
    )

    # --------------------------------------------------------------------------
    # F. LEAKING GLOWING RADIOACTIVE GREEN LIQUID SLUDGE
    # --------------------------------------------------------------------------
    # Sludge spill leaking out the top seam and running down the metallic barrel
    add_box(
        "Sludge_Top_Seam_Leak",
        size=(0.14, 0.08, 0.06),
        location=(0, pack_y + 0.14, pack_z + 0.26),
        rotation=(math.radians(-10), 0, 0),
        material=mat_sludge,
        parent=root
    )

    # Vertical dripping sludge streaks flowing down the canister
    sludge_streaks = [
        ( 0.08, pack_y + 0.18, pack_z + 0.10, 0.03, 0.02, 0.28),
        (-0.06, pack_y + 0.18, pack_z + 0.02, 0.025, 0.02, 0.36),
        ( 0.00, pack_y + 0.185, pack_z - 0.12, 0.04, 0.025, 0.22),
    ]
    for s_idx, s_data in enumerate(sludge_streaks):
        sx, sy, sz, sw, sd, sh = s_data
        add_box(
            f"Sludge_Streak_{s_idx}",
            size=(sw, sd, sh),
            location=(sx, sy, sz),
            rotation=(math.radians(-10), 0, 0),
            material=mat_sludge,
            parent=root
        )

    # Dripping Sludge Globules hanging at bottom of canister
    globules = [
        (-0.06, pack_y + 0.14, pack_z - 0.28, 0.035),
        ( 0.04, pack_y + 0.15, pack_z - 0.32, 0.045),
        ( 0.10, pack_y + 0.12, pack_z - 0.27, 0.030),
    ]
    for g_idx, g_data in enumerate(globules):
        gx, gy, gz, grad = g_data
        add_sphere(
            f"Sludge_Drip_Globule_{g_idx}",
            radius=grad,
            location=(gx, gy, gz),
            scale=(1.0, 1.0, 1.4),
            material=mat_sludge,
            parent=root
        )

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_villain():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)
    
    print("=" * 65)
    print("POLLUTER VILLAIN RUNNER (PROCEDURAL GLB GENERATOR)")
    print("=" * 65)
    print("-> Assembling Polluter Villain runner model...")
    root = build_villain()
    
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
    export_villain()
