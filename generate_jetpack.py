"""
Procedural 3D Jetpack Model Generator for Blender
==================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates a sleek, high-tech, commercial AAA 3D model of a
    futuristic twin-thruster rocket jetpack:
    - Twin aerodynamic rocket fuel cylinders with chrome nosecones & hazard rings
    - Central plasma reactor core with turbine intake and glowing cyan energy
    - Bell-shaped rocket nozzles with glowing blue/orange plasma exhaust tips
    - Contoured ergonomic backplate harness mount with stabilizer winglets
    - High-pressure braided fuel conduits and energy gauges
    - Automatically exports to 'jetpack.glb' in the current working directory.
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
    "output_filename": "jetpack.glb",
    
    # Material Palette
    "color_titanium":   (0.38, 0.44, 0.52, 1.0),     # Brushed Titanium Grey
    "color_chrome":     (0.90, 0.94, 0.98, 1.0),     # Polished Chrome Accents
    "color_carbon":     (0.12, 0.15, 0.18, 1.0),     # Carbon Backplate & Brackets
    "color_hazard":     (0.98, 0.65, 0.05, 1.0),     # Industrial Amber/Orange
    "glow_blue_core":   (0.00, 0.92, 1.00, 1.0),     # Cyan-Blue Core Plasma
    "glow_orange_fire": (1.00, 0.40, 0.00, 1.0),     # Fiery Orange Exhaust Plume
}


# ==============================================================================
# PBR MATERIAL FACTORY
# ==============================================================================
def create_pbr_material(name, base_color, metallic=0.85, roughness=0.25, emission=None, emission_strength=1.0):
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
# PROCEDURAL JETPACK MODEL BUILDER
# ==============================================================================
def build_jetpack():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Initialize PBR Materials
    materials = {
        "titanium": create_pbr_material("Mat_Titanium", CONFIG["color_titanium"], metallic=0.88, roughness=0.28),
        "chrome": create_pbr_material("Mat_Chrome", CONFIG["color_chrome"], metallic=0.96, roughness=0.12),
        "carbon": create_pbr_material("Mat_Carbon", CONFIG["color_carbon"], metallic=0.45, roughness=0.55),
        "hazard": create_pbr_material("Mat_Hazard", CONFIG["color_hazard"], metallic=0.75, roughness=0.25),
        "core_blue": create_pbr_material("Mat_Core_Blue", CONFIG["glow_blue_core"], metallic=0.8, roughness=0.15, emission=CONFIG["glow_blue_core"], emission_strength=4.5),
        "fire_orange": create_pbr_material("Mat_Fire_Orange", CONFIG["glow_orange_fire"], metallic=0.6, roughness=0.15, emission=CONFIG["glow_orange_fire"], emission_strength=5.0),
    }

    # Root Empty for Jetpack Asset
    root = bpy.data.objects.new("Jetpack_Root", None)
    bpy.context.collection.objects.link(root)

    # 1. CENTRAL BACKPLATE & MOUNTING HARNESS
    backplate_mesh = bpy.data.meshes.new("Backplate_Mesh")
    backplate_obj = bpy.data.objects.new("Backplate", backplate_mesh)
    bpy.context.collection.objects.link(backplate_obj)
    backplate_obj.parent = root
    backplate_obj.location = (0.0, -0.06, 0.0)
    backplate_obj.data.materials.append(materials["carbon"])

    bm_bp = bmesh.new()
    bmesh.ops.create_cube(bm_bp, size=1.0)
    # Contoured trapezoidal spinal shield
    for v in bm_bp.verts:
        v.co.x *= 0.38
        v.co.y *= 0.05
        v.co.z *= 0.65
        # Taper at waist
        if v.co.z < 0:
            v.co.x *= 0.85
        # Curve to hug player spine
        v.co.y += abs(v.co.x) * 0.12
    bm_bp.to_mesh(backplate_mesh)
    bm_bp.free()

    # Backplate Horizontal Reinforcement Cross-Beams
    for z_beam in [-0.18, 0.18]:
        beam_mesh = bpy.data.meshes.new(f"Beam_{z_beam}_Mesh")
        beam_obj = bpy.data.objects.new(f"Beam_{z_beam}", beam_mesh)
        bpy.context.collection.objects.link(beam_obj)
        beam_obj.parent = root
        beam_obj.location = (0.0, -0.02, z_beam)
        beam_obj.data.materials.append(materials["chrome"])

        bm_bm = bmesh.new()
        bmesh.ops.create_cube(bm_bm, size=1.0)
        bmesh.ops.scale(bm_bm, vec=(0.58, 0.04, 0.06), verts=bm_bm.verts)
        bm_bm.to_mesh(beam_mesh)
        bm_bm.free()

    # 2. CENTRAL PLASMA REACTOR CORE (The Heart of the Jetpack)
    reactor_mesh = bpy.data.meshes.new("ReactorHousing_Mesh")
    reactor_obj = bpy.data.objects.new("ReactorHousing", reactor_mesh)
    bpy.context.collection.objects.link(reactor_obj)
    reactor_obj.parent = root
    reactor_obj.location = (0.0, 0.05, 0.0)
    reactor_obj.data.materials.append(materials["titanium"])

    bm_rc = bmesh.new()
    bmesh.ops.create_cone(bm_rc, cap_ends=True, cap_tris=False, segments=12, radius1=0.14, radius2=0.14, depth=0.16)
    for v in bm_rc.verts:
        # Rotate cylinder along Y to face outward
        y_tmp = v.co.y
        v.co.y = -v.co.z
        v.co.z = y_tmp
    bm_rc.to_mesh(reactor_mesh)
    bm_rc.free()

    # Glowing Blue Plasma Core Sphere
    core_mesh = bpy.data.meshes.new("PlasmaCore_Mesh")
    core_obj = bpy.data.objects.new("PlasmaCore", core_mesh)
    bpy.context.collection.objects.link(core_obj)
    core_obj.parent = root
    core_obj.location = (0.0, 0.14, 0.0)
    core_obj.data.materials.append(materials["core_blue"])

    bm_cr = bmesh.new()
    bmesh.ops.create_icosphere(bm_cr, subdivisions=2, radius=0.08)
    bm_cr.to_mesh(core_mesh)
    bm_cr.free()

    # Circular Chrome Turbine Grille Ring
    grille_mesh = bpy.data.meshes.new("GrilleRing_Mesh")
    grille_obj = bpy.data.objects.new("GrilleRing", grille_mesh)
    bpy.context.collection.objects.link(grille_obj)
    grille_obj.parent = root
    grille_obj.location = (0.0, 0.13, 0.0)
    grille_obj.data.materials.append(materials["chrome"])

    bm_gr = bmesh.new()
    bmesh.ops.create_cone(bm_gr, cap_ends=False, segments=16, radius1=0.13, radius2=0.13, depth=0.04)
    for v in bm_gr.verts:
        y_tmp = v.co.y
        v.co.y = -v.co.z
        v.co.z = y_tmp
    bm_gr.to_mesh(grille_mesh)
    bm_gr.free()

    # 3. TWIN ROCKET FUEL CYLINDERS (Left & Right)
    for side, x_pos in [("Left", -0.27), ("Right", 0.27)]:
        tank_root = bpy.data.objects.new(f"ThrusterTank_{side}", None)
        bpy.context.collection.objects.link(tank_root)
        tank_root.parent = root
        tank_root.location = (x_pos, 0.0, 0.0)

        # Main Fuel Cylinder Body
        cyl_mesh = bpy.data.meshes.new(f"Cylinder_{side}_Mesh")
        cyl_obj = bpy.data.objects.new(f"Cylinder_{side}", cyl_mesh)
        bpy.context.collection.objects.link(cyl_obj)
        cyl_obj.parent = tank_root
        cyl_obj.location = (0.0, 0.0, 0.0)
        cyl_obj.data.materials.append(materials["titanium"])

        bm_cyl = bmesh.new()
        bmesh.ops.create_cone(bm_cyl, cap_ends=True, cap_tris=False, segments=16, radius1=0.135, radius2=0.135, depth=0.55)
        bm_cyl.to_mesh(cyl_mesh)
        bm_cyl.free()

        # Aerodynamic Top Nosecone
        nose_mesh = bpy.data.meshes.new(f"Nosecone_{side}_Mesh")
        nose_obj = bpy.data.objects.new(f"Nosecone_{side}", nose_mesh)
        bpy.context.collection.objects.link(nose_obj)
        nose_obj.parent = tank_root
        nose_obj.location = (0.0, 0.0, 0.38)
        nose_obj.data.materials.append(materials["chrome"])

        bm_ns = bmesh.new()
        bmesh.ops.create_cone(bm_ns, cap_ends=True, cap_tris=False, segments=16, radius1=0.135, radius2=0.02, depth=0.22)
        bm_ns.to_mesh(nose_mesh)
        bm_ns.free()

        # Chrome Nose Needle Antenna / Pitot Tube
        needle_mesh = bpy.data.meshes.new(f"Needle_{side}_Mesh")
        needle_obj = bpy.data.objects.new(f"Needle_{side}", needle_mesh)
        bpy.context.collection.objects.link(needle_obj)
        needle_obj.parent = tank_root
        needle_obj.location = (0.0, 0.0, 0.53)
        needle_obj.data.materials.append(materials["hazard"])

        bm_nd = bmesh.new()
        bmesh.ops.create_cone(bm_nd, cap_ends=True, cap_tris=False, segments=8, radius1=0.015, radius2=0.003, depth=0.10)
        bm_nd.to_mesh(needle_mesh)
        bm_nd.free()

        # Hazard Chevron Warning Collars (Upper & Lower Bands)
        for z_band in [-0.16, 0.16]:
            band_mesh = bpy.data.meshes.new(f"Band_{side}_{z_band}_Mesh")
            band_obj = bpy.data.objects.new(f"Band_{side}_{z_band}", band_mesh)
            bpy.context.collection.objects.link(band_obj)
            band_obj.parent = tank_root
            band_obj.location = (0.0, 0.0, z_band)
            band_obj.data.materials.append(materials["hazard"])

            bm_bd = bmesh.new()
            bmesh.ops.create_cone(bm_bd, cap_ends=False, segments=16, radius1=0.145, radius2=0.145, depth=0.045)
            bm_bd.to_mesh(band_mesh)
            bm_bd.free()

        # Vertical Glowing Energy Level Strip
        gauge_mesh = bpy.data.meshes.new(f"EnergyGauge_{side}_Mesh")
        gauge_obj = bpy.data.objects.new(f"EnergyGauge_{side}", gauge_mesh)
        bpy.context.collection.objects.link(gauge_obj)
        gauge_obj.parent = tank_root
        gauge_obj.location = (0.0, 0.135, 0.0)
        gauge_obj.data.materials.append(materials["core_blue"])

        bm_gg = bmesh.new()
        bmesh.ops.create_cube(bm_gg, size=1.0)
        bmesh.ops.scale(bm_gg, vec=(0.024, 0.01, 0.38), verts=bm_gg.verts)
        bm_gg.to_mesh(gauge_mesh)
        bm_gg.free()

        # 4. BELL-SHAPED ROCKET EXHAUST NOZZLES
        nozzle_mesh = bpy.data.meshes.new(f"Nozzle_{side}_Mesh")
        nozzle_obj = bpy.data.objects.new(f"Nozzle_{side}", nozzle_mesh)
        bpy.context.collection.objects.link(nozzle_obj)
        nozzle_obj.parent = tank_root
        nozzle_obj.location = (0.0, 0.0, -0.38)
        nozzle_obj.data.materials.append(materials["titanium"])

        bm_nz = bmesh.new()
        # Expanding bell nozzle: radius1 (throat)=0.10, radius2 (exit bell)=0.155
        bmesh.ops.create_cone(bm_nz, cap_ends=True, cap_tris=False, segments=16, radius1=0.10, radius2=0.155, depth=0.22)
        bm_nz.to_mesh(nozzle_mesh)
        bm_nz.free()

        # Chrome Nozzle Throat Ring
        collar_mesh = bpy.data.meshes.new(f"NozzleRing_{side}_Mesh")
        collar_obj = bpy.data.objects.new(f"NozzleRing_{side}", collar_mesh)
        bpy.context.collection.objects.link(collar_obj)
        collar_obj.parent = tank_root
        collar_obj.location = (0.0, 0.0, -0.27)
        collar_obj.data.materials.append(materials["chrome"])

        bm_cl = bmesh.new()
        bmesh.ops.create_cone(bm_cl, cap_ends=False, segments=16, radius1=0.115, radius2=0.115, depth=0.04)
        bm_cl.to_mesh(collar_mesh)
        bm_cl.free()

        # Glowing Blue/Orange Core Plasma Nozzle Insert
        plasma_rim_mesh = bpy.data.meshes.new(f"PlasmaRim_{side}_Mesh")
        plasma_rim_obj = bpy.data.objects.new(f"PlasmaRim_{side}", plasma_rim_mesh)
        bpy.context.collection.objects.link(plasma_rim_obj)
        plasma_rim_obj.parent = tank_root
        plasma_rim_obj.location = (0.0, 0.0, -0.48)
        plasma_rim_obj.data.materials.append(materials["core_blue"])

        bm_pr = bmesh.new()
        bmesh.ops.create_cone(bm_pr, cap_ends=True, cap_tris=False, segments=16, radius1=0.13, radius2=0.08, depth=0.03)
        bm_pr.to_mesh(plasma_rim_mesh)
        bm_pr.free()

        # Fiery Orange/Amber Plasma Exhaust Plume Tip
        flame_mesh = bpy.data.meshes.new(f"FlameTip_{side}_Mesh")
        flame_obj = bpy.data.objects.new(f"FlameTip_{side}", flame_mesh)
        bpy.context.collection.objects.link(flame_obj)
        flame_obj.parent = tank_root
        flame_obj.location = (0.0, 0.0, -0.58)
        flame_obj.data.materials.append(materials["fire_orange"])

        bm_fl = bmesh.new()
        # Inverted cone tip representing radiant flame exhaust
        bmesh.ops.create_cone(bm_fl, cap_ends=True, cap_tris=False, segments=12, radius1=0.10, radius2=0.01, depth=0.18)
        bm_fl.to_mesh(flame_mesh)
        bm_fl.free()

        # Stabilizer Aerodynamic Winglet (Flanking Exterior)
        ext_sign = -1.0 if side == "Left" else 1.0
        fin_mesh = bpy.data.meshes.new(f"Fin_{side}_Mesh")
        fin_obj = bpy.data.objects.new(f"Fin_{side}", fin_mesh)
        bpy.context.collection.objects.link(fin_obj)
        fin_obj.parent = tank_root
        fin_obj.location = (ext_sign * 0.14, 0.0, -0.15)
        fin_obj.rotation_euler = (0, ext_sign * math.radians(-12), 0)
        fin_obj.data.materials.append(materials["carbon"])

        bm_fn = bmesh.new()
        bmesh.ops.create_cube(bm_fn, size=1.0)
        # Swept delta fin
        for v in bm_fn.verts:
            v.co.x *= 0.12
            v.co.y *= 0.02
            v.co.z *= 0.22
            # Sweep back
            if ext_sign * v.co.x > 0:
                v.co.z -= 0.08
        bm_fn.to_mesh(fin_mesh)
        bm_fn.free()

        # Winglet Navigation Beacon Light
        beacon_mesh = bpy.data.meshes.new(f"Beacon_{side}_Mesh")
        beacon_obj = bpy.data.objects.new(f"Beacon_{side}", beacon_mesh)
        bpy.context.collection.objects.link(beacon_obj)
        beacon_obj.parent = fin_obj
        beacon_obj.location = (ext_sign * 0.12, 0.0, -0.06)
        beacon_obj.data.materials.append(materials["hazard"])

        bm_bc = bmesh.new()
        bmesh.ops.create_icosphere(bm_bc, subdivisions=1, radius=0.025)
        bm_bc.to_mesh(beacon_mesh)
        bm_bc.free()

    # 5. BRAIDED FUEL CONDUIT PIPES (Connecting Core to Tanks)
    for ext_sign in [-1.0, 1.0]:
        pipe_curve = bpy.data.curves.new(f"Conduit_{ext_sign}", type="CURVE")
        pipe_curve.dimensions = "3D"
        pipe_curve.bevel_depth = 0.022
        pipe_curve.bevel_resolution = 4
        spline = pipe_curve.splines.new("POLY")
        spline.points.add(2)
        # 3 coordinate points forming smooth L-shaped pipe
        spline.points[0].co = (0.0, 0.08, 0.0, 1.0)
        spline.points[1].co = (ext_sign * 0.14, 0.10, -0.08, 1.0)
        spline.points[2].co = (ext_sign * 0.25, 0.04, -0.16, 1.0)

        pipe_obj = bpy.data.objects.new(f"ConduitPipe_{ext_sign}", pipe_curve)
        bpy.context.collection.objects.link(pipe_obj)
        pipe_obj.parent = root
        bpy.context.view_layer.objects.active = pipe_obj
        pipe_obj.select_set(True)
        bpy.ops.object.convert(target="MESH")
        pipe_obj.select_set(False)
        pipe_obj.data.materials.append(materials["chrome"])

    # 6. FLOATING FLIGHT VELOCITY HALO (Cyan Pulsing Orbit Ring)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.52,
        minor_radius=0.016,
        major_segments=32,
        minor_segments=8,
        location=(0.0, 0.04, 0.0),
        rotation=(math.radians(82), 0, 0)
    )
    halo_obj = bpy.context.active_object
    halo_obj.name = "FlightAuraRing"
    halo_obj.parent = root
    halo_obj.data.materials.append(materials["core_blue"])

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_jetpack():
    output_filename = CONFIG["output_filename"]
    cwd = os.getcwd()
    export_filepath = os.path.join(cwd, output_filename)

    print("=" * 65)
    print("FUTURISTIC JETPACK PROCEDURAL GENERATOR")
    print("=" * 65)
    print("-> Procedurally modeling twin-rocket metallic jetpack with plasma thrusters...")
    build_jetpack()

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
    export_jetpack()
