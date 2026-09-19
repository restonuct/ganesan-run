"""
Procedural 3D 2X Multiplier Badge Model Generator for Blender
=============================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a stylized, commercial AAA 3D emblem badge of a
    "2X" Score Multiplier power-up:
    - Bold, beveled, shiny 24K gold 3D typography displaying "2X"
    - Deep royal ruby-red metallic enamel shield medallion backing with golden rim
    - Stepped 8-pointed golden sunburst relief behind typography
    - Floating tilted celestial orbital ring (halo) with radiant amber-gold emission
    - Floating crystalline diamond star gems adorning the orbital halo
    - Automatically exports to 'multiplier.glb' in the current working directory.
"""

import bpy
import bmesh
import math
import os
import sys

# ==============================================================================
# CONFIGURATION & PALETTE
# ==============================================================================
CONFIG = {
    "output_filename": "multiplier.glb",
    
    # Material Palette
    "color_gold_text":   (1.00, 0.82, 0.12, 1.0),     # 24K Polished Metallic Gold
    "color_enamel_red":  (0.85, 0.10, 0.14, 1.0),     # Regal Ruby-Red Metallic Enamel
    "color_gold_bezel":  (0.95, 0.72, 0.15, 1.0),     # Ornate Golden Bezel Rim
    "color_star_gems":   (1.00, 0.98, 0.90, 1.0),     # Radiant Diamond Stars
    "glow_orbit_ring":   (1.00, 0.75, 0.10, 1.0),     # Glowing Celestial Orbit Halo
    "glow_inner_aura":   (1.00, 0.50, 0.05, 1.0),     # Warm Amber Rim Glow
}


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_pbr_material(name, base_color, metallic=0.9, roughness=0.18, emission=None, emission_strength=1.0):
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
# PROCEDURAL 2X MULTIPLIER BADGE BUILDER
# ==============================================================================
def build_multiplier():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Initialize PBR Materials
    materials = {
        "gold_text": create_pbr_material("Mat_Gold_Text", CONFIG["color_gold_text"], metallic=0.96, roughness=0.12),
        "ruby_red":  create_pbr_material("Mat_Ruby_Red", CONFIG["color_enamel_red"], metallic=0.75, roughness=0.22),
        "gold_rim":  create_pbr_material("Mat_Gold_Rim", CONFIG["color_gold_bezel"], metallic=0.92, roughness=0.16),
        "orbit_glow": create_pbr_material("Mat_Orbit_Glow", CONFIG["glow_orbit_ring"], metallic=0.8, roughness=0.15, emission=CONFIG["glow_orbit_ring"], emission_strength=4.5),
        "star_gem":  create_pbr_material("Mat_Star_Gem", CONFIG["color_star_gems"], metallic=0.85, roughness=0.10, emission=CONFIG["color_star_gems"], emission_strength=3.0),
    }

    # Root Empty for Multiplier Asset
    root = bpy.data.objects.new("Multiplier_2X_Root", None)
    bpy.context.collection.objects.link(root)

    # 1. RUBY RED ENAMEL MEDALLION PLATE
    badge_mesh = bpy.data.meshes.new("Badge_Plate_Mesh")
    badge_obj = bpy.data.objects.new("Badge_Plate", badge_mesh)
    bpy.context.collection.objects.link(badge_obj)
    badge_obj.parent = root
    badge_obj.location = (0.0, 0.0, 0.0)
    badge_obj.data.materials.append(materials["ruby_red"])

    bm_bp = bmesh.new()
    # Cylinder rotated along X to face forward (Y axis)
    bmesh.ops.create_cone(bm_bp, cap_ends=True, cap_tris=False, segments=24, radius1=0.42, radius2=0.42, depth=0.08)
    for v in bm_bp.verts:
        y_tmp = v.co.y
        v.co.y = -v.co.z
        v.co.z = y_tmp
    bm_bp.to_mesh(badge_mesh)
    bm_bp.free()

    # 2. OUTER GOLDEN BEVELED RIM
    rim_mesh = bpy.data.meshes.new("Badge_Rim_Mesh")
    rim_obj = bpy.data.objects.new("Badge_Rim", rim_mesh)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.parent = root
    rim_obj.location = (0.0, 0.0, 0.0)
    rim_obj.data.materials.append(materials["gold_rim"])

    bm_rm = bmesh.new()
    # Outer ring collar: radius1=0.45, radius2=0.45, depth=0.10
    bmesh.ops.create_cone(bm_rm, cap_ends=False, segments=24, radius1=0.455, radius2=0.455, depth=0.10)
    for v in bm_rm.verts:
        y_tmp = v.co.y
        v.co.y = -v.co.z
        v.co.z = y_tmp
    bm_rm.to_mesh(rim_mesh)
    bm_rm.free()

    # Stepped Golden Front Lip Ring
    lip_mesh = bpy.data.meshes.new("Badge_Lip_Mesh")
    lip_obj = bpy.data.objects.new("Badge_Lip", lip_mesh)
    bpy.context.collection.objects.link(lip_obj)
    lip_obj.parent = root
    lip_obj.location = (0.0, 0.045, 0.0)
    lip_obj.data.materials.append(materials["gold_rim"])

    bm_lp = bmesh.new()
    bmesh.ops.create_cone(bm_lp, cap_ends=False, segments=24, radius1=0.465, radius2=0.43, depth=0.02)
    for v in bm_lp.verts:
        y_tmp = v.co.y
        v.co.y = -v.co.z
        v.co.z = y_tmp
    bm_lp.to_mesh(lip_mesh)
    bm_lp.free()

    # 3. EMBOSSED 8-POINTED GOLDEN SUNBURST STAR (Behind Text)
    for idx, star_rot in enumerate([0, math.radians(45)]):
        star_mesh = bpy.data.meshes.new(f"StarFacet_{idx}_Mesh")
        star_obj = bpy.data.objects.new(f"StarFacet_{idx}", star_mesh)
        bpy.context.collection.objects.link(star_obj)
        star_obj.parent = root
        star_obj.location = (0.0, 0.042, 0.0)
        star_obj.rotation_euler = (0, star_rot, 0)
        star_obj.data.materials.append(materials["gold_rim"])

        bm_st = bmesh.new()
        bmesh.ops.create_cube(bm_st, size=1.0)
        bmesh.ops.scale(bm_st, vec=(0.52, 0.012, 0.52), verts=bm_st.verts)
        bm_st.to_mesh(star_mesh)
        bm_st.free()

    # 4. BOLD 3D "2X" METALLIC TYPOGRAPHY
    bpy.ops.object.text_add(location=(0.0, 0.05, 0.0))
    txt_obj = bpy.context.active_object
    txt_obj.name = "Text_2X"
    txt_obj.parent = root
    txt_obj.data.body = "2X"
    txt_obj.data.size = 0.54
    txt_obj.data.extrude = 0.08
    txt_obj.data.bevel_depth = 0.018
    txt_obj.data.bevel_resolution = 3
    txt_obj.data.align_x = "CENTER"
    txt_obj.data.align_y = "CENTER"
    txt_obj.rotation_euler = (math.radians(90), 0, 0)

    # Convert text curve to clean mesh
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    txt_obj.location = (0.0, 0.055, 0.0)
    txt_obj.data.materials.append(materials["gold_text"])

    # 5. FLOATING CELESTIAL ORBITAL RING (HALO)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.64,
        minor_radius=0.018,
        major_segments=40,
        minor_segments=8,
        location=(0.0, 0.0, 0.0),
        rotation=(math.radians(65), math.radians(22), 0)
    )
    halo_obj = bpy.context.active_object
    halo_obj.name = "Celestial_Orbit_Ring"
    halo_obj.parent = root
    halo_obj.data.materials.append(materials["orbit_glow"])

    # 6. ORBITING DIAMOND STAR GEMS (4 Nodes along the ring)
    halo_rot_matrix = halo_obj.rotation_euler
    for idx, angle in enumerate([0, math.pi / 2, math.pi, 3 * math.pi / 2]):
        gem_mesh = bpy.data.meshes.new(f"OrbitGem_{idx}_Mesh")
        gem_obj = bpy.data.objects.new(f"OrbitGem_{idx}", gem_mesh)
        bpy.context.collection.objects.link(gem_obj)
        gem_obj.parent = halo_obj

        # Compute position along circle in local space of halo
        r_gem = 0.64
        gem_obj.location = (r_gem * math.cos(angle), r_gem * math.sin(angle), 0.0)
        gem_obj.data.materials.append(materials["star_gem"])

        bm_gm = bmesh.new()
        # Faceted octahedral diamond gem
        bmesh.ops.create_cone(bm_gm, cap_ends=True, cap_tris=False, segments=4, radius1=0.045, radius2=0.0, depth=0.06)
        bmesh.ops.create_cone(bm_gm, cap_ends=True, cap_tris=False, segments=4, radius1=0.045, radius2=0.0, depth=-0.06)
        bm_gm.to_mesh(gem_mesh)
        bm_gm.free()

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_multiplier():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)

    print("=" * 65)
    print("2X MULTIPLIER BADGE PROCEDURAL GENERATOR")
    print("=" * 65)
    print("-> Procedurally modeling 2X emblem badge with 3D typography and celestial halo...")
    build_multiplier()

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
    export_multiplier()
