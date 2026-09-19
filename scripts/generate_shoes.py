"""
Procedural 3D Super Sneakers Model Generator for Blender
=========================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a stylized, commercial AAA 3D model of futuristic
    high-top super sneakers / jump shoes:
    - Pair of left & right high-top athletic jump boots with dynamic display stance
    - Heavy-duty coiled jump springs under the heels and forefoot with glowing energy
    - Aerodynamic multi-layer sporty upper with high-top padded collar and tongue
    - High-tech power ankle strap with metallic buckle and neon power laces
    - Swept-back speed wings on the outer heel counters
    - Radiant glowing neon orange/yellow sole energy cores and springs
    - Automatically exports to 'shoes.glb' in the current working directory.
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
    "output_filename": "shoes.glb",
    
    # Palette
    "color_upper_orange": (1.00, 0.38, 0.00, 1.0),     # Vibrant Athletic Orange
    "color_upper_white":  (0.95, 0.96, 0.98, 1.0),     # Pearlescent White Panels
    "color_charcoal":     (0.12, 0.14, 0.18, 1.0),     # Dark Carbon Trim / Outsole
    "color_gold_wing":    (0.98, 0.72, 0.12, 1.0),     # Golden Speed Wings
    "color_cyan_tech":    (0.00, 0.92, 1.00, 1.0),     # Cyan Power Accent
    "glow_spring_orange": (1.00, 0.55, 0.05, 1.0),     # Radiant Glowing Spring
    "glow_cyan":          (0.00, 0.85, 1.00, 1.0),     # Neon Cyan Accent
}


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_pbr_material(name, base_color, metallic=0.2, roughness=0.35, emission=None, emission_strength=1.0):
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
# HELPER: PROCEDURAL HELICAL SPRING MESH
# ==============================================================================
def create_helical_spring(name, radius=0.07, height=0.14, turns=3.2, steps=36, pipe_radius=0.016):
    curve_data = bpy.data.curves.new(name + "_Curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = pipe_radius
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new("POLY")
    spline.points.add(steps - 1)

    for i in range(steps):
        t = i / (steps - 1)
        angle = t * turns * 2.0 * math.pi
        z = t * height
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        spline.points[i].co = (x, y, z, 1.0)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj.select_set(False)
    return obj


# ==============================================================================
# PROCEDURAL SINGLE SNEAKER BUILDER
# ==============================================================================
def build_single_shoe(is_left=True, materials=None):
    shoe_root = bpy.data.objects.new(f"Shoe_{'Left' if is_left else 'Right'}", None)
    bpy.context.collection.objects.link(shoe_root)

    mirror_sign = -1.0 if is_left else 1.0

    # 1. OUTSOLE BASE PADS (Footprint Ground Pads)
    # Heel Ground Plate
    heel_pad_mesh = bpy.data.meshes.new("HeelPad_Mesh")
    heel_pad_obj = bpy.data.objects.new("HeelPad", heel_pad_mesh)
    bpy.context.collection.objects.link(heel_pad_obj)
    heel_pad_obj.parent = shoe_root
    heel_pad_obj.location = (0.0, -0.16, 0.02)
    heel_pad_obj.data.materials.append(materials["charcoal"])

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.26, 0.26, 0.04), verts=bm.verts)
    bm.to_mesh(heel_pad_mesh)
    bm.free()

    # Forefoot Ground Plate
    fore_pad_mesh = bpy.data.meshes.new("ForePad_Mesh")
    fore_pad_obj = bpy.data.objects.new("ForePad", fore_pad_mesh)
    bpy.context.collection.objects.link(fore_pad_obj)
    fore_pad_obj.parent = shoe_root
    fore_pad_obj.location = (0.0, 0.16, 0.02)
    fore_pad_obj.data.materials.append(materials["charcoal"])

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.28, 0.32, 0.04), verts=bm.verts)
    bm.to_mesh(fore_pad_mesh)
    bm.free()

    # 2. GLOWING HIGH-JUMP HELICAL SPRINGS (2 Under Each Shoe!)
    # Heel Spring
    heel_spring = create_helical_spring("Heel_Spring", radius=0.075, height=0.13, turns=3.2, pipe_radius=0.018)
    heel_spring.parent = shoe_root
    heel_spring.location = (0.0, -0.16, 0.04)
    heel_spring.data.materials.append(materials["glow_spring"])

    # Forefoot Spring
    fore_spring = create_helical_spring("Fore_Spring", radius=0.075, height=0.13, turns=3.2, pipe_radius=0.018)
    fore_spring.parent = shoe_root
    fore_spring.location = (0.0, 0.16, 0.04)
    fore_spring.data.materials.append(materials["glow_spring"])

    # Spring Core Pistons (Metallic dampeners inside the springs)
    for y_pos in [-0.16, 0.16]:
        piston_mesh = bpy.data.meshes.new("Piston_Mesh")
        piston_obj = bpy.data.objects.new("Piston", piston_mesh)
        bpy.context.collection.objects.link(piston_obj)
        piston_obj.parent = shoe_root
        piston_obj.location = (0.0, y_pos, 0.10)
        piston_obj.data.materials.append(materials["white"])

        bm_p = bmesh.new()
        bmesh.ops.create_cone(bm_p, cap_ends=True, cap_tris=False, segments=12, radius1=0.035, radius2=0.035, depth=0.12)
        bm_p.to_mesh(piston_mesh)
        bm_p.free()

    # 3. CHUNKY MIDSOLE (Resting on top of springs at Z = 0.18)
    midsole_mesh = bpy.data.meshes.new("Midsole_Mesh")
    midsole_obj = bpy.data.objects.new("Midsole", midsole_mesh)
    bpy.context.collection.objects.link(midsole_obj)
    midsole_obj.parent = shoe_root
    midsole_obj.location = (0.0, 0.02, 0.19)
    midsole_obj.data.materials.append(materials["charcoal"])

    bm_m = bmesh.new()
    bmesh.ops.create_cube(bm_m, size=1.0)
    # Tapered athletic sole platform
    for v in bm_m.verts:
        v.co.x *= 0.34
        v.co.y *= 0.74
        v.co.z *= 0.06
        if v.co.y > 0.15:
            v.co.z += (v.co.y - 0.15) * 0.28
        if v.co.y < -0.15:
            v.co.x *= 1.12
    bm_m.to_mesh(midsole_mesh)
    bm_m.free()

    # Glowing Energy Ribbon / Sole Rim
    glow_rim_mesh = bpy.data.meshes.new("GlowRim_Mesh")
    glow_rim_obj = bpy.data.objects.new("GlowRim", glow_rim_mesh)
    bpy.context.collection.objects.link(glow_rim_obj)
    glow_rim_obj.parent = shoe_root
    glow_rim_obj.location = (0.0, 0.02, 0.22)
    glow_rim_obj.data.materials.append(materials["glow_spring"])

    bm_gr = bmesh.new()
    bmesh.ops.create_cube(bm_gr, size=1.0)
    for v in bm_gr.verts:
        v.co.x *= 0.355
        v.co.y *= 0.755
        v.co.z *= 0.025
        if v.co.y > 0.15:
            v.co.z += (v.co.y - 0.15) * 0.28
    bm_gr.to_mesh(glow_rim_mesh)
    bm_gr.free()

    # 4. SNEAKER UPPER BODY (High-Top Boot)
    upper_mesh = bpy.data.meshes.new("Upper_Mesh")
    upper_obj = bpy.data.objects.new("Upper", upper_mesh)
    bpy.context.collection.objects.link(upper_obj)
    upper_obj.parent = shoe_root
    upper_obj.location = (0.0, 0.0, 0.24)
    upper_obj.data.materials.append(materials["orange"])

    bm_u = bmesh.new()
    bmesh.ops.create_cube(bm_u, size=1.0)
    for v in bm_u.verts:
        v.co.x *= 0.31
        v.co.y *= 0.70
        v.co.z *= 0.16
        v.co.z += 0.08
        if v.co.y > 0.1:
            v.co.x *= 0.88 - (v.co.y - 0.1) * 0.4
            v.co.z *= 0.75
        if v.co.y > 0.0 and v.co.z > 0.08:
            v.co.z += 0.05 - (v.co.y * 0.18)
    bm_u.to_mesh(upper_mesh)
    bm_u.free()

    # High-Top Ankle Collar
    ankle_mesh = bpy.data.meshes.new("Ankle_Mesh")
    ankle_obj = bpy.data.objects.new("Ankle", ankle_mesh)
    bpy.context.collection.objects.link(ankle_obj)
    ankle_obj.parent = shoe_root
    ankle_obj.location = (0.0, -0.10, 0.43)
    ankle_obj.data.materials.append(materials["orange"])

    bm_a = bmesh.new()
    bmesh.ops.create_cone(bm_a, cap_ends=True, cap_tris=False, segments=16, radius1=0.15, radius2=0.15, depth=0.22)
    for v in bm_a.verts:
        v.co.y *= 1.15
        v.co.y += (v.co.z * 0.2)
    bm_a.to_mesh(ankle_mesh)
    bm_a.free()

    # Inner Collar Padding (Charcoal lining)
    lining_mesh = bpy.data.meshes.new("Lining_Mesh")
    lining_obj = bpy.data.objects.new("Lining", lining_mesh)
    bpy.context.collection.objects.link(lining_obj)
    lining_obj.parent = shoe_root
    lining_obj.location = (0.0, -0.09, 0.54)
    lining_obj.data.materials.append(materials["charcoal"])

    bm_l = bmesh.new()
    bmesh.ops.create_cone(bm_l, cap_ends=True, cap_tris=False, segments=16, radius1=0.135, radius2=0.135, depth=0.04)
    bm_l.to_mesh(lining_mesh)
    bm_l.free()

    # High-Top Padded Tongue
    tongue_mesh = bpy.data.meshes.new("Tongue_Mesh")
    tongue_obj = bpy.data.objects.new("Tongue", tongue_mesh)
    bpy.context.collection.objects.link(tongue_obj)
    tongue_obj.parent = shoe_root
    tongue_obj.location = (0.0, 0.06, 0.44)
    tongue_obj.rotation_euler = (math.radians(-25), 0, 0)
    tongue_obj.data.materials.append(materials["charcoal"])

    bm_t = bmesh.new()
    bmesh.ops.create_cube(bm_t, size=1.0)
    bmesh.ops.scale(bm_t, vec=(0.18, 0.05, 0.24), verts=bm_t.verts)
    bm_t.to_mesh(tongue_mesh)
    bm_t.free()

    # 5. AERODYNAMIC SIDE PANELS (White Sporty Overlays)
    for s in [-1.0, 1.0]:
        panel_mesh = bpy.data.meshes.new(f"Panel_{s}_Mesh")
        panel_obj = bpy.data.objects.new(f"Panel_{s}", panel_mesh)
        bpy.context.collection.objects.link(panel_obj)
        panel_obj.parent = shoe_root
        panel_obj.location = (s * 0.16, -0.02, 0.32)
        panel_obj.rotation_euler = (0, s * math.radians(-5), math.radians(s * 4))
        panel_obj.data.materials.append(materials["white"])

        bm_sp = bmesh.new()
        bmesh.ops.create_cube(bm_sp, size=1.0)
        bmesh.ops.scale(bm_sp, vec=(0.025, 0.36, 0.14), verts=bm_sp.verts)
        bm_sp.to_mesh(panel_mesh)
        bm_sp.free()

    # 6. POWER ANKLE STRAP WITH METALLIC BUCKLE
    strap_mesh = bpy.data.meshes.new("Strap_Mesh")
    strap_obj = bpy.data.objects.new("Strap", strap_mesh)
    bpy.context.collection.objects.link(strap_obj)
    strap_obj.parent = shoe_root
    strap_obj.location = (0.0, -0.06, 0.46)
    strap_obj.data.materials.append(materials["white"])

    bm_st = bmesh.new()
    bmesh.ops.create_cone(bm_st, cap_ends=False, segments=16, radius1=0.165, radius2=0.165, depth=0.05)
    for v in bm_st.verts:
        v.co.y *= 1.2
    bm_st.to_mesh(strap_mesh)
    bm_st.free()

    # Buckle Clasp (Front)
    buckle_mesh = bpy.data.meshes.new("Buckle_Mesh")
    buckle_obj = bpy.data.objects.new("Buckle", buckle_mesh)
    bpy.context.collection.objects.link(buckle_obj)
    buckle_obj.parent = shoe_root
    buckle_obj.location = (0.0, 0.13, 0.46)
    buckle_obj.data.materials.append(materials["cyan"])

    bm_b = bmesh.new()
    bmesh.ops.create_cube(bm_b, size=1.0)
    bmesh.ops.scale(bm_b, vec=(0.09, 0.03, 0.045), verts=bm_b.verts)
    bm_b.to_mesh(buckle_mesh)
    bm_b.free()

    # 7. POWER LACES (3 Cross-Straps Over Instep)
    for i, y_lace in enumerate([0.08, 0.16, 0.24]):
        z_lace = 0.33 - (i * 0.035)
        lace_mesh = bpy.data.meshes.new(f"Lace_{i}_Mesh")
        lace_obj = bpy.data.objects.new(f"Lace_{i}", lace_mesh)
        bpy.context.collection.objects.link(lace_obj)
        lace_obj.parent = shoe_root
        lace_obj.location = (0.0, y_lace, z_lace)
        lace_obj.rotation_euler = (math.radians(-20), math.radians(90), 0)
        lace_obj.data.materials.append(materials["glow_spring"])

        bm_lc = bmesh.new()
        bmesh.ops.create_cone(bm_lc, cap_ends=True, cap_tris=False, segments=8, radius1=0.012, radius2=0.012, depth=0.20)
        bm_lc.to_mesh(lace_mesh)
        bm_lc.free()

    # 8. SWEPT-BACK AERODYNAMIC SPEED WING (Outer Flank Only)
    wing_mesh = bpy.data.meshes.new("SpeedWing_Mesh")
    wing_obj = bpy.data.objects.new("SpeedWing", wing_mesh)
    bpy.context.collection.objects.link(wing_obj)
    wing_obj.parent = shoe_root
    wing_obj.location = (mirror_sign * 0.17, -0.16, 0.40)
    wing_obj.rotation_euler = (math.radians(25), mirror_sign * math.radians(-15), mirror_sign * math.radians(18))
    wing_obj.data.materials.append(materials["gold"])

    bm_w = bmesh.new()
    for f_idx in range(3):
        f_offset_z = f_idx * 0.07
        f_offset_y = -f_idx * 0.06
        bmesh.ops.create_cone(
            bm_w,
            cap_ends=True,
            cap_tris=False,
            segments=6,
            radius1=0.035 - (f_idx * 0.005),
            radius2=0.005,
            depth=0.26 - (f_idx * 0.04)
        )
        for v in bm_w.verts[-8:]:
            v.co.y += f_offset_y
            v.co.z += f_offset_z
    bm_w.to_mesh(wing_mesh)
    bm_w.free()

    return shoe_root


# ==============================================================================
# MAIN SCENE BUILDER: PAIR OF SUPER SNEAKERS
# ==============================================================================
def build_super_sneakers():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Initialize PBR Materials
    materials = {
        "orange": create_pbr_material("Mat_Shoe_Orange", CONFIG["color_upper_orange"], metallic=0.15, roughness=0.32),
        "white": create_pbr_material("Mat_Shoe_White", CONFIG["color_upper_white"], metallic=0.2, roughness=0.22),
        "charcoal": create_pbr_material("Mat_Shoe_Charcoal", CONFIG["color_charcoal"], metallic=0.45, roughness=0.5),
        "gold": create_pbr_material("Mat_Shoe_Gold", CONFIG["color_gold_wing"], metallic=0.92, roughness=0.18),
        "cyan": create_pbr_material("Mat_Shoe_Cyan", CONFIG["color_cyan_tech"], metallic=0.6, roughness=0.2, emission=CONFIG["glow_cyan"], emission_strength=2.8),
        "glow_spring": create_pbr_material("Mat_Shoe_GlowSpring", CONFIG["glow_spring_orange"], metallic=0.8, roughness=0.15, emission=CONFIG["glow_spring_orange"], emission_strength=4.0),
    }

    # Root Empty for the complete collectible asset
    root = bpy.data.objects.new("Super_Sneakers_Pair_Root", None)
    bpy.context.collection.objects.link(root)

    # Build Left Shoe
    left_shoe = build_single_shoe(is_left=True, materials=materials)
    left_shoe.parent = root
    left_shoe.location = (-0.26, 0.0, 0.0)
    left_shoe.rotation_euler = (math.radians(-4), math.radians(4), math.radians(-8))

    # Build Right Shoe
    right_shoe = build_single_shoe(is_left=False, materials=materials)
    right_shoe.parent = root
    right_shoe.location = (0.26, 0.0, 0.0)
    right_shoe.rotation_euler = (math.radians(-4), math.radians(-4), math.radians(8))

    # Ground-level sacred energy ring / floating aura ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.55,
        minor_radius=0.016,
        major_segments=32,
        minor_segments=8,
        location=(0.0, 0.0, 0.28),
        rotation=(math.radians(90), 0, 0)
    )
    ring_obj = bpy.context.active_object
    ring_obj.name = "FloatingAuraRing"
    ring_obj.parent = root
    ring_obj.data.materials.append(materials["glow_spring"])

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_super_sneakers():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)

    print("=" * 65)
    print("SUPER SNEAKERS / JUMP SHOES PROCEDURAL GENERATOR")
    print("=" * 65)
    print("-> Procedurally modeling pair of futuristic jump sneakers with glowing springs...")
    build_super_sneakers()

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
    export_super_sneakers()
