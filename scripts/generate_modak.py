"""
Procedural 3D Golden Modak Model Generator for Blender (Traditional Sacred Sweet)
================================================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a stylized, commercial AAA 3D model of a traditional
    sacred Modak sweet:
    - Bulbous faceted/fluted base with 21 sharp vertical ridges (pleats)
    - Tapering gracefully upward into an elegant concave neck and pointed apex
    - Ornate stepped lotus petal base pedestal (Peetha)
    - Rich 24K polished metallic gold PBR material with radiant specular reflection
    - Automatically exports to 'modak.glb' in the current working directory.
"""

import bpy
import bmesh
import math
import os
import sys

# ==============================================================================
# CONFIGURATION & GOLD PALETTE
# ==============================================================================
CONFIG = {
    "output_filename": "modak.glb",
    "num_pleats": 21,              # Auspicious 21 sacred Modak pleats
    "num_rings": 36,               # Vertical resolution for silky smooth curvature
    "pleat_depth": 0.12,           # Sharpness of radial fluting
    "total_height": 1.25,          # Sweet height
    
    # 24K Indian Temple Gold PBR Palette
    "gold_base": (1.00, 0.78, 0.16, 1.0),        # 24K Rich Temple Gold
    "gold_glow": (1.00, 0.65, 0.05, 1.0),        # Warm Specular Inner Glow
    "lotus_gold": (0.95, 0.70, 0.12, 1.0),       # Lotus Pedestal Gold
    "jewel_ruby": (0.92, 0.08, 0.12, 1.0),       # Apex Jewel Finial Accent
}


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_pbr_material(name, base_color, metallic=0.92, roughness=0.18, emission=None, emission_strength=1.0):
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
# PROCEDURAL FLUTED MODAK SWEET BUILDER
# ==============================================================================
def build_golden_modak():
    # 1. Clean scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Materials
    mat_gold = create_pbr_material("Mat_ModakGold", CONFIG["gold_base"], metallic=0.94, roughness=0.18, emission=CONFIG["gold_glow"], emission_strength=0.35)
    mat_lotus = create_pbr_material("Mat_LotusBase", CONFIG["lotus_gold"], metallic=0.88, roughness=0.25)
    mat_gem = create_pbr_material("Mat_ApexGem", CONFIG["jewel_ruby"], metallic=0.1, roughness=0.1, emission=CONFIG["jewel_ruby"], emission_strength=2.0)

    root = bpy.data.objects.new("Golden_Modak_Root", None)
    bpy.context.collection.objects.link(root)

    # --------------------------------------------------------------------------
    # A. 21-PLEATED BULBOUS FLUTED BODY WITH POINTED APEX
    # --------------------------------------------------------------------------
    mesh = bpy.data.meshes.new("Modak_Fluted_Mesh")
    obj = bpy.data.objects.new("Modak_Fluted_Body", mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = root
    obj.data.materials.append(mat_gold)

    bm = bmesh.new()
    num_pleats = CONFIG["num_pleats"]
    num_rings = CONFIG["num_rings"]
    pleat_depth = CONFIG["pleat_depth"]
    total_h = CONFIG["total_height"]
    base_offset_z = 0.16

    # Radial angular steps: 2 vertices per pleat (1 crest, 1 valley) = 42 vertices per ring
    radial_steps = num_pleats * 2

    # Radius profile function as height t goes from 0.0 (bottom) to 1.0 (apex)
    def radius_profile(t):
        if t <= 0.35:
            # Rounded bulbous lower swell: expanding outward
            s = t / 0.35
            return 0.32 + math.sin(s * math.pi * 0.5) * 0.30
        elif t <= 0.75:
            # Elegant convex to concave transition
            s = (t - 0.35) / 0.40
            return 0.62 * (1.0 - s * 0.55)
        else:
            # Tapering upward into a sharp pointed apex
            s = (t - 0.75) / 0.25
            return 0.279 * ((1.0 - s) ** 1.35)

    # Flute sharpness / amplitude modulation along height
    def flute_amplitude(t):
        if t < 0.08:
            return (t / 0.08) * pleat_depth * 0.6
        elif t < 0.85:
            return pleat_depth
        else:
            # Flutes sharpen and pinch together at the apex
            return pleat_depth * (1.0 - (t - 0.85) / 0.15)

    ring_verts = []

    # Generate ring vertices
    for r in range(num_rings + 1):
        t = r / float(num_rings)
        z = base_offset_z + t * total_h
        base_r = radius_profile(t)
        amp = flute_amplitude(t)

        current_ring = []
        for i in range(radial_steps):
            angle = (i / float(radial_steps)) * (2.0 * math.pi)
            # Alternate crests and valleys across the 21 pleats
            is_crest = (i % 2 == 0)
            r_mod = base_r + (amp if is_crest else -amp * 0.65)
            # Ensure radius does not go negative
            r_mod = max(0.001, r_mod)

            x = r_mod * math.cos(angle)
            y = r_mod * math.sin(angle)
            vert = bm.verts.new((x, y, z))
            current_ring.append(vert)

        ring_verts.append(current_ring)

    # Add apex peak point
    apex_vert = bm.verts.new((0, 0, base_offset_z + total_h + 0.04))
    # Add bottom center point
    bottom_center = bm.verts.new((0, 0, base_offset_z))

    bm.verts.ensure_lookup_table()

    # Create quad faces between adjacent rings
    for r in range(num_rings):
        ring_a = ring_verts[r]
        ring_b = ring_verts[r + 1]
        for i in range(radial_steps):
            next_i = (i + 1) % radial_steps
            v1 = ring_a[i]
            v2 = ring_a[next_i]
            v3 = ring_b[next_i]
            v4 = ring_b[i]
            bm.faces.new((v1, v2, v3, v4))

    # Cap top ring to apex point (triangles)
    top_ring = ring_verts[num_rings]
    for i in range(radial_steps):
        next_i = (i + 1) % radial_steps
        bm.faces.new((top_ring[i], top_ring[next_i], apex_vert))

    # Cap bottom ring to bottom center point (triangles)
    bottom_ring = ring_verts[0]
    for i in range(radial_steps):
        next_i = (i + 1) % radial_steps
        bm.faces.new((bottom_center, bottom_ring[next_i], bottom_ring[i]))

    # Calculate normals & smooth shading
    bm.to_mesh(mesh)
    bm.free()
    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()

    # --------------------------------------------------------------------------
    # B. APEX JEWEL FINIAL
    # --------------------------------------------------------------------------
    jewel_mesh = bpy.data.meshes.new("Apex_Jewel_Mesh")
    jewel_obj = bpy.data.objects.new("Apex_Jewel_Finial", jewel_mesh)
    bpy.context.collection.objects.link(jewel_obj)
    jewel_obj.parent = root
    jewel_obj.location = (0, 0, base_offset_z + total_h + 0.05)
    jewel_obj.data.materials.append(mat_gem)

    bm_j = bmesh.new()
    bmesh.ops.create_cone(bm_j, cap_ends=True, cap_tris=False, segments=12, radius1=0.032, radius2=0.0, depth=0.09)
    bm_j.to_mesh(jewel_mesh)
    bm_j.free()
    if hasattr(jewel_mesh, "shade_smooth"):
        jewel_mesh.shade_smooth()

    # --------------------------------------------------------------------------
    # C. ORNATE LOTUS PETAL PEETHA (BASE PLINTH)
    # --------------------------------------------------------------------------
    # Tier 1: Wide round base disc
    base_disc_mesh = bpy.data.meshes.new("Lotus_BaseDisc_Mesh")
    base_disc = bpy.data.objects.new("Lotus_BaseDisc", base_disc_mesh)
    bpy.context.collection.objects.link(base_disc)
    base_disc.parent = root
    base_disc.location = (0, 0, 0.04)
    base_disc.data.materials.append(mat_lotus)

    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=24, radius1=0.55, radius2=0.50, depth=0.08)
    bm_b.to_mesh(base_disc_mesh)
    bm_b.free()

    # Tier 2: Lotus Petals radiating around the base
    num_petals = 12
    petal_r = 0.44
    for p in range(num_petals):
        p_angle = (p / float(num_petals)) * (2.0 * math.pi)
        px = petal_r * math.cos(p_angle)
        py = petal_r * math.sin(p_angle)

        p_mesh = bpy.data.meshes.new(f"LotusPetal_{p}_mesh")
        p_obj = bpy.data.objects.new(f"LotusPetal_{p}", p_mesh)
        bpy.context.collection.objects.link(p_obj)
        p_obj.parent = root
        p_obj.location = (px, py, 0.10)
        p_obj.rotation_euler = (math.radians(18), 0, p_angle - math.pi / 2.0)
        p_obj.scale = (0.16, 0.22, 0.06)
        p_obj.data.materials.append(mat_lotus)

        bm_p = bmesh.new()
        bmesh.ops.create_uvsphere(bm_p, u_segments=12, v_segments=8, radius=1.0)
        bm_p.to_mesh(p_mesh)
        bm_p.free()
        if hasattr(p_mesh, "shade_smooth"):
            p_mesh.shade_smooth()

    # Tier 3: Inner golden ring seat
    seat_mesh = bpy.data.meshes.new("Lotus_Seat_Mesh")
    seat_obj = bpy.data.objects.new("Lotus_Seat_Ring", seat_mesh)
    bpy.context.collection.objects.link(seat_obj)
    seat_obj.parent = root
    seat_obj.location = (0, 0, 0.14)
    seat_obj.data.materials.append(mat_gold)

    bm_s = bmesh.new()
    bmesh.ops.create_cone(bm_s, cap_ends=True, cap_tris=False, segments=24, radius1=0.38, radius2=0.36, depth=0.06)
    bm_s.to_mesh(seat_mesh)
    bm_s.free()

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_golden_modak():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)
    
    print("=" * 65)
    print("GOLDEN MODAK PROCEDURAL GENERATOR (21 SACRED PLEATS)")
    print("=" * 65)
    print("-> Assembling Traditional Golden Modak sweet model...")
    root = build_golden_modak()
    
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
    export_golden_modak()
