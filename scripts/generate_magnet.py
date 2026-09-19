"""
Procedural 3D Horseshoe Magnet Model Generator for Blender
==========================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a classic, commercial AAA 3D model of a
    horseshoe coin magnet power-up:
    - Classic horseshoe arch body in candy apple red metallic lacquer
    - High-polish brushed silver/chrome polar end tips (North & South poles)
    - Embossed polarity markers ("N" and "S") on the front polar faces
    - Electric cyan-blue magnetic field flux arcs bridging between the pole tips
    - Floating magnetic energy attraction beads and orbital velocity halo
    - Automatically exports to 'magnet.glb' in the current working directory.
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
    "output_filename": "magnet.glb",
    
    # Material Palette
    "color_candy_red":     (0.92, 0.12, 0.15, 1.0),    # Candy Apple Red Metallic
    "color_chrome_silver": (0.92, 0.95, 0.98, 1.0),    # Polished Silver Pole Tips
    "color_pole_text":     (0.20, 0.25, 0.32, 1.0),    # Dark Steel Polarity Marker
    "glow_magnetic_blue":  (0.00, 0.92, 1.00, 1.0),    # Electric Cyan Magnetic Field
    "glow_spark_bead":     (0.75, 0.95, 1.00, 1.0),    # Magnetic Attraction Energy
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
# PROCEDURAL HORSESHOE MAGNET BUILDER
# ==============================================================================
def build_magnet():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Initialize PBR Materials
    materials = {
        "red":        create_pbr_material("Mat_Magnet_Red", CONFIG["color_candy_red"], metallic=0.88, roughness=0.16),
        "silver":     create_pbr_material("Mat_Magnet_Silver", CONFIG["color_chrome_silver"], metallic=0.96, roughness=0.12),
        "marker":     create_pbr_material("Mat_Pole_Marker", CONFIG["color_pole_text"], metallic=0.75, roughness=0.3),
        "field_blue": create_pbr_material("Mat_Field_Blue", CONFIG["glow_magnetic_blue"], metallic=0.7, roughness=0.15, emission=CONFIG["glow_magnetic_blue"], emission_strength=4.5),
        "spark":      create_pbr_material("Mat_Energy_Spark", CONFIG["glow_spark_bead"], metallic=0.9, roughness=0.10, emission=CONFIG["glow_spark_bead"], emission_strength=3.5),
    }

    # Root Empty for Magnet Asset
    root = bpy.data.objects.new("Horseshoe_Magnet_Root", None)
    bpy.context.collection.objects.link(root)

    radius_arch = 0.30
    tube_radius = 0.095
    leg_length = 0.20

    # 1. CONTINUOUS RED METALLIC HORSESHOE ARCH
    curve_data = bpy.data.curves.new("Horseshoe_Curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = tube_radius
    curve_data.bevel_resolution = 5
    spline = curve_data.splines.new("POLY")

    steps_arch = 20
    total_pts = steps_arch + 3
    spline.points.add(total_pts - 1)

    # Point 0: Bottom of left leg
    spline.points[0].co = (-radius_arch, 0.0, -leg_length, 1.0)
    # Point 1: Top of left leg
    spline.points[1].co = (-radius_arch, 0.0, 0.0, 1.0)

    # Arch Points 2 to steps_arch + 1: Semi-circle from Left to Right
    for i in range(steps_arch + 1):
        t = i / steps_arch
        # Angle from pi (left) down to 0 (right)
        theta = math.pi - (t * math.pi)
        x = radius_arch * math.cos(theta)
        z = radius_arch * math.sin(theta)
        spline.points[2 + i].co = (x, 0.0, z, 1.0)

    # Last point: Bottom of right leg
    spline.points[-1].co = (radius_arch, 0.0, -leg_length, 1.0)

    arch_obj = bpy.data.objects.new("Horseshoe_Arch_Red", curve_data)
    bpy.context.collection.objects.link(arch_obj)
    arch_obj.parent = root
    bpy.context.view_layer.objects.active = arch_obj
    arch_obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    arch_obj.select_set(False)
    arch_obj.data.materials.append(materials["red"])

    # 2. SILVER POLAR TIPS (North and South Poles)
    for idx, (label, x_tip) in enumerate([("N", -radius_arch), ("S", radius_arch)]):
        tip_mesh = bpy.data.meshes.new(f"PolarTip_{idx}_Mesh")
        tip_obj = bpy.data.objects.new(f"PolarTip_{idx}", tip_mesh)
        bpy.context.collection.objects.link(tip_obj)
        tip_obj.parent = root
        tip_obj.location = (x_tip, 0.0, -leg_length - 0.08)
        tip_obj.data.materials.append(materials["silver"])

        bm_tip = bmesh.new()
        bmesh.ops.create_cone(
            bm_tip,
            cap_ends=True,
            cap_tris=False,
            segments=18,
            radius1=tube_radius * 1.02,
            radius2=tube_radius * 1.02,
            depth=0.16
        )
        bm_tip.to_mesh(tip_mesh)
        bm_tip.free()

        # Polarity Divider Seam Ring
        seam_mesh = bpy.data.meshes.new(f"SeamRing_{idx}_Mesh")
        seam_obj = bpy.data.objects.new(f"SeamRing_{idx}", seam_mesh)
        bpy.context.collection.objects.link(seam_obj)
        seam_obj.parent = root
        seam_obj.location = (x_tip, 0.0, -leg_length)
        seam_obj.data.materials.append(materials["marker"])

        bm_sm = bmesh.new()
        bmesh.ops.create_cone(bm_sm, cap_ends=False, segments=18, radius1=tube_radius * 1.05, radius2=tube_radius * 1.05, depth=0.015)
        bm_sm.to_mesh(seam_mesh)
        bm_sm.free()

        # Embossed Polarity Letter ("N" or "S") on Front Face
        bpy.ops.object.text_add(location=(x_tip, tube_radius * 1.01, -leg_length - 0.08))
        txt_pole = bpy.context.active_object
        txt_pole.name = f"Text_Pole_{label}"
        txt_pole.parent = root
        txt_pole.data.body = label
        txt_pole.data.size = 0.10
        txt_pole.data.extrude = 0.018
        txt_pole.data.bevel_depth = 0.004
        txt_pole.data.bevel_resolution = 2
        txt_pole.data.align_x = "CENTER"
        txt_pole.data.align_y = "CENTER"
        txt_pole.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.convert(target="MESH")
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        txt_pole.location = (x_tip, tube_radius * 1.01, -leg_length - 0.08)
        txt_pole.data.materials.append(materials["marker"])

    # 3. ELECTRIC MAGNETIC FIELD FLUX ARCS (Bridging North and South Poles)
    # Arc 1: Direct downward looping flux arc
    arc1_curve = bpy.data.curves.new("FluxArc_1", type="CURVE")
    arc1_curve.dimensions = "3D"
    arc1_curve.bevel_depth = 0.014
    arc1_curve.bevel_resolution = 3
    spline1 = arc1_curve.splines.new("POLY")
    steps_flux = 16
    spline1.points.add(steps_flux)

    z_tip_bottom = -leg_length - 0.16
    for i in range(steps_flux + 1):
        t = i / steps_flux
        # Span from -radius_arch to +radius_arch
        theta = math.pi - (t * math.pi)
        x = radius_arch * math.cos(theta)
        # Parabolic dip between poles
        z = z_tip_bottom - (0.16 * math.sin(t * math.pi))
        spline1.points[i].co = (x, 0.0, z, 1.0)

    arc1_obj = bpy.data.objects.new("MagneticFluxArc_Primary", arc1_curve)
    bpy.context.collection.objects.link(arc1_obj)
    arc1_obj.parent = root
    bpy.context.view_layer.objects.active = arc1_obj
    arc1_obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    arc1_obj.select_set(False)
    arc1_obj.data.materials.append(materials["field_blue"])

    # Arc 2: Secondary forward-bulging flux arc
    arc2_curve = bpy.data.curves.new("FluxArc_2", type="CURVE")
    arc2_curve.dimensions = "3D"
    arc2_curve.bevel_depth = 0.010
    arc2_curve.bevel_resolution = 3
    spline2 = arc2_curve.splines.new("POLY")
    spline2.points.add(steps_flux)

    for i in range(steps_flux + 1):
        t = i / steps_flux
        theta = math.pi - (t * math.pi)
        x = radius_arch * math.cos(theta)
        y = 0.12 * math.sin(t * math.pi)
        z = z_tip_bottom - (0.08 * math.sin(t * math.pi))
        spline2.points[i].co = (x, y, z, 1.0)

    arc2_obj = bpy.data.objects.new("MagneticFluxArc_Secondary", arc2_curve)
    bpy.context.collection.objects.link(arc2_obj)
    arc2_obj.parent = root
    bpy.context.view_layer.objects.active = arc2_obj
    arc2_obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    arc2_obj.select_set(False)
    arc2_obj.data.materials.append(materials["field_blue"])

    # 4. MAGNETIC ATTRACTION ENERGY BEADS (Floating spark nodes)
    for idx, (bx, by, bz) in enumerate([
        (-0.15, 0.04, z_tip_bottom - 0.12),
        (0.0, 0.08, z_tip_bottom - 0.18),
        (0.15, -0.04, z_tip_bottom - 0.12),
        (-0.08, -0.05, z_tip_bottom - 0.09),
        (0.08, 0.06, z_tip_bottom - 0.09)
    ]):
        bead_mesh = bpy.data.meshes.new(f"MagneticBead_{idx}_Mesh")
        bead_obj = bpy.data.objects.new(f"MagneticBead_{idx}", bead_mesh)
        bpy.context.collection.objects.link(bead_obj)
        bead_obj.parent = root
        bead_obj.location = (bx, by, bz)
        bead_obj.data.materials.append(materials["spark"])

        bm_bd = bmesh.new()
        bmesh.ops.create_icosphere(bm_bd, subdivisions=1, radius=0.024)
        bm_bd.to_mesh(bead_mesh)
        bm_bd.free()

    # 5. SURROUNDING CELESTIAL MAGNETIC HALO (Orbital Velocity Ring)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.54,
        minor_radius=0.016,
        major_segments=36,
        minor_segments=8,
        location=(0.0, 0.0, 0.06),
        rotation=(math.radians(78), 0, 0)
    )
    halo_obj = bpy.context.active_object
    halo_obj.name = "MagneticHalo_Ring"
    halo_obj.parent = root
    halo_obj.data.materials.append(materials["field_blue"])

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_magnet():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)

    print("=" * 65)
    print("CLASSIC HORSESHOE MAGNET PROCEDURAL GENERATOR")
    print("=" * 65)
    print("-> Procedurally modeling horseshoe magnet with silver tips and flux arcs...")
    build_magnet()

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
    export_magnet()
