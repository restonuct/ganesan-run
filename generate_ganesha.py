"""
Procedural 3D Lord Ganesha Model Generator for Blender (Cute Chibi Style)
=========================================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a charming, stylized, cute Chibi-style 3D model
    of Lord Ganesha matching the exact visual design:
    - Rounded soft body with warm golden-yellow complexion
    - Wearing a vibrant orange/saffron dhoti and draped upvastram (shoulder sash)
    - Large round ears with soft baby-pink inner ear pads
    - An elephantine trunk curved gently to the left (Vakratunda)
    - Ornate multi-tiered golden Mukut (crown) featuring a prominent central red ruby gemstone
    - Sacred holy ivory tusks (including the auspicious broken right tusk)
    - Cute expressive Chibi eyes with glossy reflection highlights
    - Golden ornaments: wrist bangles, waistband (Kamarbandh), and anklets
    - Automatically exports to 'ganesha.glb' in the current working directory.
"""

import bpy
import math
import os
import sys

# ==============================================================================
# CONFIGURATION & CHIBI COLOR PALETTE
# ==============================================================================
CONFIG = {
    "output_filename": "ganesha.glb",
    "total_height": 1.72,          # Scaled for runner collision box
    
    # Stylized Cute Chibi PBR Palette
    "golden_yellow_skin": (0.96, 0.77, 0.26, 1.0), # Warm golden-yellow divine skin
    "saffron_orange": (0.95, 0.42, 0.08, 1.0),     # Auspicious saffron/orange dhoti & upvastram
    "saffron_dark": (0.80, 0.32, 0.05, 1.0),       # Pleat shadow accents
    "ornate_gold": (1.00, 0.80, 0.15, 1.0),        # 24K Temple Gold for Mukut & Jewelry
    "ruby_gem": (0.92, 0.05, 0.15, 1.0),           # Central Red Ruby Gemstone
    "inner_ear_pink": (0.94, 0.60, 0.65, 1.0),     # Cute soft pink inner ear pad
    "ivory_white": (0.98, 0.97, 0.92, 1.0),        # Holy ivory tusks
    "chibi_eye_dark": (0.08, 0.09, 0.12, 1.0),     # Glossy dark eyes
    "chibi_eye_shine": (1.00, 1.00, 1.00, 1.0),    # Eye sparkle highlights
    "tilak_vermilion": (0.88, 0.12, 0.12, 1.0),    # Sacred red tilak
    "tilak_yellow": (1.00, 0.88, 0.10, 1.0),       # Sandalwood tilak base
    "modak_gold": (1.00, 0.75, 0.12, 1.0),         # Modak in palm
}


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_pbr_material(name, base_color, metallic=0.0, roughness=0.4, emission=None, emission_strength=1.0):
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
# MESH PRIMITIVE HELPERS
# ==============================================================================
def add_sphere(name, radius, location=(0, 0, 0), scale=(1, 1, 1), material=None, parent=None, segs=24, rings=16):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    obj.scale = scale
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()
    return obj


def add_cylinder(name, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0), material=None, parent=None, vertices=20):
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
# PROCEDURAL CHIBI LORD GANESHA BUILDER
# ==============================================================================
def build_chibi_ganesha():
    # 1. Clean factory scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Materials Setup
    mat_skin = create_pbr_material("Mat_GaneshaSkin", CONFIG["golden_yellow_skin"], metallic=0.04, roughness=0.35)
    mat_dhoti = create_pbr_material("Mat_DhotiOrange", CONFIG["saffron_orange"], metallic=0.0, roughness=0.55)
    mat_dhoti_dark = create_pbr_material("Mat_DhotiDark", CONFIG["saffron_dark"], metallic=0.0, roughness=0.6)
    mat_gold = create_pbr_material("Mat_MukutGold", CONFIG["ornate_gold"], metallic=0.88, roughness=0.22)
    mat_ruby = create_pbr_material("Mat_RubyGem", CONFIG["ruby_gem"], metallic=0.1, roughness=0.15, emission=CONFIG["ruby_gem"], emission_strength=1.6)
    mat_ear_pink = create_pbr_material("Mat_EarPink", CONFIG["inner_ear_pink"], metallic=0.0, roughness=0.45)
    mat_ivory = create_pbr_material("Mat_IvoryTusk", CONFIG["ivory_white"], metallic=0.05, roughness=0.25)
    mat_eye_dark = create_pbr_material("Mat_EyeDark", CONFIG["chibi_eye_dark"], metallic=0.1, roughness=0.1)
    mat_eye_shine = create_pbr_material("Mat_EyeShine", CONFIG["chibi_eye_shine"], metallic=0.0, roughness=0.05, emission=(1, 1, 1, 1), emission_strength=2.0)
    mat_tilak_red = create_pbr_material("Mat_TilakRed", CONFIG["tilak_vermilion"], metallic=0.0, roughness=0.4)
    mat_tilak_yellow = create_pbr_material("Mat_TilakYellow", CONFIG["tilak_yellow"], metallic=0.1, roughness=0.35)
    mat_modak = create_pbr_material("Mat_ModakGold", CONFIG["modak_gold"], metallic=0.75, roughness=0.28)

    root = bpy.data.objects.new("Lord_Ganesha_Chibi", None)
    bpy.context.collection.objects.link(root)

    # --------------------------------------------------------------------------
    # A. CHUBBY LOWER BODY & SAFFRON DHOTI
    # --------------------------------------------------------------------------
    torso_y = 0.62
    tummy = add_sphere(
        "Tummy_Belly",
        radius=0.40,
        location=(0, -0.04, torso_y),
        scale=(1.05, 1.12, 1.0),
        material=mat_skin,
        parent=root
    )

    # Saffron Dhoti wrap around hips & legs
    dhoti_base = add_sphere(
        "Dhoti_Base",
        radius=0.42,
        location=(0, -0.04, torso_y - 0.12),
        scale=(1.08, 1.10, 0.85),
        material=mat_dhoti,
        parent=root
    )

    # Dhoti central folded pleats (Patta)
    dhoti_pleats = add_box(
        "Dhoti_Pleats",
        size=(0.20, 0.14, 0.44),
        location=(0, -0.42, torso_y - 0.22),
        rotation=(math.radians(8), 0, 0),
        material=mat_dhoti_dark,
        parent=root
    )

    # Ornate Golden Kamarbandh (Waistband belt)
    add_cylinder(
        "Golden_Kamarbandh",
        radius=0.43,
        depth=0.07,
        location=(0, -0.04, torso_y - 0.05),
        rotation=(math.radians(6), 0, 0),
        material=mat_gold,
        parent=root
    )
    # Belt buckle medallion
    add_sphere(
        "Belt_Medallion",
        radius=0.08,
        location=(0, -0.47, torso_y - 0.04),
        scale=(1.0, 0.4, 1.0),
        material=mat_gold,
        parent=root
    )
    # Medallion ruby center
    add_sphere(
        "Belt_Ruby",
        radius=0.035,
        location=(0, -0.50, torso_y - 0.04),
        material=mat_ruby,
        parent=root
    )

    # Chubby Cute Legs & Golden Anklets
    leg_x_offset = 0.22
    for side in (-1, 1):
        leg = add_cylinder(
            f"Leg_{'R' if side > 0 else 'L'}",
            radius=0.16,
            depth=0.38,
            location=(side * leg_x_offset, -0.02, 0.24),
            rotation=(math.radians(10), side * math.radians(-5), 0),
            material=mat_dhoti,
            parent=root
        )
        foot = add_sphere(
            f"Foot_{'R' if side > 0 else 'L'}",
            radius=0.15,
            location=(side * leg_x_offset, -0.10, 0.10),
            scale=(1.0, 1.35, 0.7),
            material=mat_skin,
            parent=root
        )
        add_cylinder(
            f"Anklet_{'R' if side > 0 else 'L'}",
            radius=0.17,
            depth=0.04,
            location=(side * leg_x_offset, -0.02, 0.16),
            material=mat_gold,
            parent=root
        )

    # --------------------------------------------------------------------------
    # B. SAFFRON UPVASTRAM (SHOULDER SASH DRAPED DIAGONALLY)
    # --------------------------------------------------------------------------
    add_cylinder(
        "Upvastram_Sash_Diagonal",
        radius=0.08,
        depth=0.68,
        location=(-0.10, -0.16, torso_y + 0.16),
        rotation=(math.radians(35), math.radians(-38), math.radians(20)),
        material=mat_dhoti,
        parent=root
    )
    add_cylinder(
        "Upvastram_GoldBorder",
        radius=0.085,
        depth=0.68,
        location=(-0.11, -0.17, torso_y + 0.16),
        rotation=(math.radians(35), math.radians(-38), math.radians(20)),
        material=mat_gold,
        parent=root
    )
    add_box(
        "Upvastram_Tail",
        size=(0.14, 0.08, 0.32),
        location=(-0.30, 0.08, torso_y + 0.22),
        rotation=(math.radians(-15), math.radians(10), 0),
        material=mat_dhoti,
        parent=root
    )

    # Sacred Holy Thread (Yajnopavita)
    add_cylinder(
        "Yajnopavita_Thread",
        radius=0.022,
        depth=0.66,
        location=(0.04, -0.18, torso_y + 0.14),
        rotation=(math.radians(30), math.radians(35), 0),
        material=mat_gold,
        parent=root
    )

    # --------------------------------------------------------------------------
    # C. CUTE CHIBI HEAD (ROUNDED SOFT EXPRESSION)
    # --------------------------------------------------------------------------
    head_y = 1.08
    head = add_sphere(
        "Chibi_Head",
        radius=0.42,
        location=(0, -0.05, head_y),
        scale=(1.08, 1.02, 1.0),
        material=mat_skin,
        parent=root
    )

    for side in (-1, 1):
        add_sphere(
            f"Cheek_{'R' if side > 0 else 'L'}",
            radius=0.18,
            location=(side * 0.28, -0.28, head_y - 0.06),
            scale=(1.0, 1.0, 0.9),
            material=mat_skin,
            parent=root
        )

    # --------------------------------------------------------------------------
    # D. LARGE ROUNDED EARS WITH PINK INNER PADS
    # --------------------------------------------------------------------------
    ear_x = 0.44
    for side in (-1, 1):
        ear_outer = add_cylinder(
            f"Ear_Outer_{'R' if side > 0 else 'L'}",
            radius=0.28,
            depth=0.05,
            location=(side * ear_x, 0.02, head_y + 0.06),
            rotation=(math.radians(8), side * math.radians(-32), math.radians(6)),
            material=mat_skin,
            parent=root
        )
        ear_inner = add_cylinder(
            f"Ear_Inner_{'R' if side > 0 else 'L'}",
            radius=0.20,
            depth=0.06,
            location=(side * (ear_x - 0.01), -0.01, head_y + 0.06),
            rotation=(math.radians(8), side * math.radians(-32), math.radians(6)),
            material=mat_ear_pink,
            parent=root
        )
        add_cylinder(
            f"Earring_{'R' if side > 0 else 'L'}",
            radius=0.07,
            depth=0.03,
            location=(side * (ear_x + 0.16), 0.01, head_y - 0.16),
            rotation=(0, math.radians(90), 0),
            material=mat_gold,
            parent=root
        )

    # --------------------------------------------------------------------------
    # E. TRUNK CURVED GENTLY TO THE LEFT (VAKRATUNDA)
    # --------------------------------------------------------------------------
    trunk_segments = [
        (0.00,  -0.42, head_y - 0.06, 0.16,  25,   0,   0),
        (0.04,  -0.49, head_y - 0.18, 0.14,  35,  12, -10),
        (0.10,  -0.54, head_y - 0.30, 0.12,  42,  25, -20),
        (0.18,  -0.53, head_y - 0.40, 0.10,  30,  45, -35),
        (0.25,  -0.47, head_y - 0.45, 0.085, 10,  65, -45),
        (0.28,  -0.40, head_y - 0.43, 0.07, -15,  85, -60),
    ]

    for idx, seg in enumerate(trunk_segments):
        sx, sy, sz, srad, rx, ry, rz = seg
        add_sphere(
            f"Trunk_Segment_{idx}",
            radius=srad,
            location=(sx, sy, sz),
            material=mat_skin,
            parent=root
        )

    # Golden Modak cradled at tip of trunk
    add_sphere(
        "Trunk_Tip_Modak",
        radius=0.075,
        location=(0.31, -0.36, head_y - 0.40),
        scale=(1.0, 1.0, 1.25),
        material=mat_modak,
        parent=root
    )

    # --------------------------------------------------------------------------
    # F. HOLY TUSKS (EKADANTA: BROKEN RIGHT, INTACT LEFT)
    # --------------------------------------------------------------------------
    add_cone(
        "Tusk_Left_Intact",
        radius1=0.05,
        depth=0.18,
        location=(0.14, -0.42, head_y - 0.18),
        rotation=(math.radians(110), math.radians(25), math.radians(-15)),
        material=mat_ivory,
        parent=root
    )
    add_cylinder(
        "Tusk_Right_Broken",
        radius=0.05,
        depth=0.07,
        location=(-0.14, -0.42, head_y - 0.18),
        rotation=(math.radians(105), math.radians(-25), math.radians(15)),
        material=mat_ivory,
        parent=root
    )

    # --------------------------------------------------------------------------
    # G. CUTE BIG CHIBI EYES & SACRED FOREHEAD TILAK
    # --------------------------------------------------------------------------
    eye_x = 0.18
    for side in (-1, 1):
        add_sphere(
            f"Eye_Dark_{'R' if side > 0 else 'L'}",
            radius=0.065,
            location=(side * eye_x, -0.44, head_y + 0.08),
            scale=(1.0, 0.4, 1.2),
            material=mat_eye_dark,
            parent=root
        )
        add_sphere(
            f"Eye_ShineMain_{'R' if side > 0 else 'L'}",
            radius=0.024,
            location=(side * (eye_x - 0.015), -0.465, head_y + 0.11),
            scale=(1.0, 0.4, 1.0),
            material=mat_eye_shine,
            parent=root
        )
        add_sphere(
            f"Eye_ShineSmall_{'R' if side > 0 else 'L'}",
            radius=0.012,
            location=(side * (eye_x + 0.02), -0.46, head_y + 0.06),
            scale=(1.0, 0.4, 1.0),
            material=mat_eye_shine,
            parent=root
        )

    # Sacred Forehead Tilak
    add_box(
        "Tilak_Yellow_Base",
        size=(0.14, 0.03, 0.04),
        location=(0, -0.46, head_y + 0.18),
        rotation=(math.radians(12), 0, 0),
        material=mat_tilak_yellow,
        parent=root
    )
    add_box(
        "Tilak_Red_Center",
        size=(0.04, 0.035, 0.14),
        location=(0, -0.465, head_y + 0.22),
        rotation=(math.radians(12), 0, 0),
        material=mat_tilak_red,
        parent=root
    )

    # --------------------------------------------------------------------------
    # H. ORNATE GOLDEN CROWN (MUKUT) WITH CENTRAL RED GEMSTONE
    # --------------------------------------------------------------------------
    crown_base_z = head_y + 0.32

    # Tier 1: Wide ornate golden headband ring
    add_cylinder(
        "Mukut_Band_Base",
        radius=0.38,
        depth=0.10,
        location=(0, -0.04, crown_base_z),
        material=mat_gold,
        parent=root
    )

    # Tier 2: Fluted middle coronet
    add_cylinder(
        "Mukut_Tier_Middle",
        radius=0.30,
        depth=0.14,
        location=(0, -0.04, crown_base_z + 0.11),
        material=mat_gold,
        parent=root
    )

    # Tier 3: Ornate golden conical spire (Shikhara peak)
    add_cone(
        "Mukut_Spire_Top",
        radius1=0.22,
        depth=0.28,
        location=(0, -0.04, crown_base_z + 0.30),
        material=mat_gold,
        parent=root
    )

    # Crown Kalash Finial jewel tip
    add_sphere(
        "Mukut_Kalash_Finial",
        radius=0.065,
        location=(0, -0.04, crown_base_z + 0.46),
        scale=(1.0, 1.0, 1.3),
        material=mat_gold,
        parent=root
    )

    # Ornate Frontal Crown Arch Medallion
    add_box(
        "Mukut_Front_Crest",
        size=(0.24, 0.08, 0.22),
        location=(0, -0.40, crown_base_z + 0.07),
        rotation=(math.radians(12), 0, 0),
        material=mat_gold,
        parent=root
    )

    # PROMINENT CENTRAL RED RUBY GEMSTONE
    add_sphere(
        "Mukut_Central_Ruby_Gem",
        radius=0.085,
        location=(0, -0.45, crown_base_z + 0.09),
        scale=(1.0, 0.6, 1.25),
        material=mat_ruby,
        parent=root
    )

    # Flanking smaller ruby pearls on crown band
    for side in (-1, 1):
        add_sphere(
            f"Mukut_SideRuby_{'R' if side > 0 else 'L'}",
            radius=0.04,
            location=(side * 0.22, -0.34, crown_base_z + 0.04),
            scale=(1.0, 0.7, 1.0),
            material=mat_ruby,
            parent=root
        )

    # Divine Radiance Halo (Prabhavali Ring) behind crown
    add_cylinder(
        "Prabhavali_Halo",
        radius=0.52,
        depth=0.03,
        location=(0, 0.22, head_y + 0.28),
        rotation=(math.radians(90), 0, 0),
        material=mat_gold,
        parent=root
    )

    # --------------------------------------------------------------------------
    # I. CHATURBHUJA (4 CUTE CHIBI ARMS & DIVINE EMBLEMS)
    # --------------------------------------------------------------------------
    arm_y = torso_y + 0.18

    # Lower Right Arm: Raised in Abhaya Mudra (Blessing & Protection)
    add_cylinder(
        "Arm_Lower_R",
        radius=0.10,
        depth=0.34,
        location=(-0.38, -0.15, arm_y),
        rotation=(math.radians(-35), math.radians(-25), math.radians(20)),
        material=mat_skin,
        parent=root
    )
    add_sphere(
        "Hand_Abhaya_R",
        radius=0.10,
        location=(-0.46, -0.32, arm_y + 0.12),
        scale=(0.6, 1.0, 1.2),
        material=mat_skin,
        parent=root
    )
    add_cylinder(
        "Bangle_R",
        radius=0.115,
        depth=0.04,
        location=(-0.44, -0.28, arm_y + 0.06),
        rotation=(math.radians(-35), math.radians(-25), math.radians(20)),
        material=mat_gold,
        parent=root
    )

    # Lower Left Arm: Holding Sweet Modak Bowl
    add_cylinder(
        "Arm_Lower_L",
        radius=0.10,
        depth=0.34,
        location=(0.38, -0.15, arm_y),
        rotation=(math.radians(-25), math.radians(35), math.radians(-20)),
        material=mat_skin,
        parent=root
    )
    add_sphere(
        "Hand_Modak_L",
        radius=0.10,
        location=(0.46, -0.32, arm_y + 0.06),
        scale=(1.0, 1.0, 0.8),
        material=mat_skin,
        parent=root
    )
    add_sphere(
        "Palm_Modak",
        radius=0.09,
        location=(0.46, -0.34, arm_y + 0.16),
        scale=(1.0, 1.0, 1.28),
        material=mat_modak,
        parent=root
    )
    add_cylinder(
        "Bangle_L",
        radius=0.115,
        depth=0.04,
        location=(0.44, -0.28, arm_y + 0.02),
        rotation=(math.radians(-25), math.radians(35), math.radians(-20)),
        material=mat_gold,
        parent=root
    )

    # Upper Arms (Holding sacred lotus & divine emblem)
    for side in (-1, 1):
        add_cylinder(
            f"Arm_Upper_{'R' if side > 0 else 'L'}",
            radius=0.09,
            depth=0.32,
            location=(side * 0.38, 0.06, arm_y + 0.18),
            rotation=(math.radians(20), side * math.radians(45), 0),
            material=mat_skin,
            parent=root
        )
        add_cylinder(
            f"Armlet_{'R' if side > 0 else 'L'}",
            radius=0.105,
            depth=0.04,
            location=(side * 0.36, 0.05, arm_y + 0.18),
            rotation=(math.radians(20), side * math.radians(45), 0),
            material=mat_gold,
            parent=root
        )

    # Sacred Pink Lotus held in Upper Right Hand
    add_sphere(
        "Sacred_Lotus_Bud",
        radius=0.08,
        location=(-0.52, -0.02, arm_y + 0.38),
        scale=(1.0, 1.0, 1.35),
        material=mat_ear_pink,
        parent=root
    )
    # Sacred Ankusha (Goad) held in Upper Left Hand
    add_cylinder(
        "Ankusha_Shaft",
        radius=0.02,
        depth=0.36,
        location=(0.52, -0.02, arm_y + 0.38),
        rotation=(math.radians(15), math.radians(-10), 0),
        material=mat_gold,
        parent=root
    )
    add_box(
        "Ankusha_Blade",
        size=(0.04, 0.10, 0.12),
        location=(0.52, -0.04, arm_y + 0.52),
        material=mat_gold,
        parent=root
    )

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_chibi_ganesha():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)
    
    print("=" * 65)
    print("CHIBI LORD GANESHA PROCEDURAL GENERATOR")
    print("=" * 65)
    print("-> Assembling Chibi Lord Ganesha model...")
    root = build_chibi_ganesha()
    
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
    export_chibi_ganesha()
