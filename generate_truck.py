"""
Procedural 3D Municipal Garbage Trucks Generator for Blender (3 Distinct Variations)
===================================================================================
Author: Expert Senior 3D Game Developer & Blender Python (bpy) Specialist
Description:
    Procedurally generates low-poly municipal garbage and dump trucks with three
    distinct gameplay and visual variations:
    1. Standard Block Truck:
       - Weathered rusty olive-green / slate-grey compactor dump body
       - Full-height solid driver cab, chrome grille, front bumper
       - Industrial side reinforcement ribs and rear compactor hopper door
    2. Ramp Truck:
       - Front triangular steel wedge incline ramp sloping smoothly from ground to roof
       - High-contrast yellow and black diagonal chevron hazard warning stripes
       - Side safety guard rails leading onto the rooftop catwalk
    3. Moving Truck:
       - Heavy container cargo body in hazard diesel orange
       - Bold yellow and black diagonal chevron hazard warning stripes along side panels
       - Dual rooftop flashing amber warning beacons and dual vertical chrome exhaust stacks
    Exports 'truck.glb' (with all variations) and 'truck_ramp.glb' for direct Three.js runtime.
"""

import bpy
import bmesh
import math
import os
import sys

# ==============================================================================
# CONFIGURATION & COLOR PALETTES
# ==============================================================================
CONFIG = {
    "length": 18.0,            # Base chassis length
    "width": 2.4,              # Track lane width
    "roof_height": 3.8,        # Roof level for running
    "ramp_length": 8.0,        # Front incline ramp length
    
    # Stylized Municipal PBR Palette
    "dump_green_grey": (0.22, 0.30, 0.26, 1.0),   # Rusty Olive-Green Municipal Dump Body
    "rust_accent": (0.38, 0.20, 0.14, 1.0),       # Weathered Oxide Rust
    "moving_orange": (0.86, 0.44, 0.08, 1.0),     # Moving Hazard Orange Container
    "ramp_teal": (0.10, 0.38, 0.40, 1.0),         # Ramp Truck Industrial Teal
    "cab_slate": (0.16, 0.18, 0.22, 1.0),         # Heavy Industrial Driver Cab
    "metal_chrome": (0.72, 0.75, 0.80, 1.0),      # Polished Steel / Bull-Bar / Rims
    "tire_rubber": (0.08, 0.08, 0.09, 1.0),       # Heavy Duty Tire Rubber
    "glass_tint": (0.12, 0.25, 0.38, 1.0),        # Windshield Safety Tint
    "hazard_yellow": (0.96, 0.82, 0.06, 1.0),     # Chevron Hazard Yellow
    "hazard_black": (0.10, 0.10, 0.12, 1.0),      # Chevron Hazard Black
    "beacon_amber": (1.00, 0.60, 0.05, 1.0),      # Flashing Amber Warning Beacons
    "headlight_xenon": (1.00, 0.98, 0.85, 1.0),   # Xenon Headlights
    "taillight_red": (0.90, 0.06, 0.06, 1.0),     # Rear Red Brakes
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
# DIRECT BMESH PRIMITIVE HELPERS
# ==============================================================================
def add_box(name, size, location=(0, 0, 0), rotation=(0, 0, 0), material=None, parent=None):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
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


def add_cylinder(name, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0), material=None, parent=None, vertices=16):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
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


def add_wedge_ramp(name, width, length, height, location, material_deck=None, material_stripe=None, parent=None):
    """Creates a triangular wedge ramp: toe at -length/2 (height 0), top at +length/2 (height)."""
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    if parent:
        obj.parent = parent

    hw = width / 2.0
    hl = length / 2.0

    # 6 vertices for triangular prism wedge
    verts = [
        # Incline top slope
        (-hw, -hl, 0.0),      # 0 Front left toe
        ( hw, -hl, 0.0),      # 1 Front right toe
        ( hw,  hl, height),   # 2 Back right top
        (-hw,  hl, height),   # 3 Back left top
        # Bottom chassis
        (-hw,  hl, 0.0),      # 4 Back left bottom
        ( hw,  hl, 0.0),      # 5 Back right bottom
    ]

    faces = [
        (0, 1, 2, 3),   # Slope running deck
        (0, 3, 4),      # Left triangle
        (1, 5, 2),      # Right triangle
        (3, 2, 5, 4),   # Back connection face
        (0, 4, 5, 1),   # Bottom face
    ]

    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()
    if material_deck:
        obj.data.materials.append(material_deck)

    # Add diagonal yellow & black chevron caution stripes on ramp slope
    num_stripes = 6
    stripe_w = width * 0.88
    stripe_l = length / float(num_stripes * 2.2)
    ramp_angle = math.atan2(height, length)

    for s in range(num_stripes):
        t = (s + 0.5) / float(num_stripes)
        sy = -hl + t * length
        sz = t * height + 0.02
        add_box(
            f"{name}_Chevron_{s}",
            size=(stripe_w, stripe_l, 0.025),
            location=(0, sy, sz),
            rotation=(ramp_angle, 0, 0),
            material=material_stripe,
            parent=obj
        )

    return obj


# ==============================================================================
# PROCEDURAL TRUCK GENERATOR (3 VARIATIONS)
# ==============================================================================
def build_truck_variant(variant_name="standard"):
    """
    Builds one of three municipal truck variations:
    1. 'standard': Rusty green/grey dump body with driver cab & bumper
    2. 'ramp': Front metal wedge incline ramp with yellow/black chevrons
    3. 'moving': Orange container body with yellow/black chevron side stripes & beacons
    """
    root = bpy.data.objects.new(f"Truck_{variant_name.capitalize()}", None)
    bpy.context.collection.objects.link(root)

    w = CONFIG["width"]
    l = CONFIG["length"]
    h = CONFIG["roof_height"]

    # Materials setup
    mat_green_dump = create_pbr_material("Mat_DumpGreen", CONFIG["dump_green_grey"], metallic=0.18, roughness=0.55)
    mat_rust = create_pbr_material("Mat_RustOxide", CONFIG["rust_accent"], metallic=0.12, roughness=0.68)
    mat_orange = create_pbr_material("Mat_MovingOrange", CONFIG["moving_orange"], metallic=0.22, roughness=0.48)
    mat_teal = create_pbr_material("Mat_RampTeal", CONFIG["ramp_teal"], metallic=0.25, roughness=0.45)
    mat_cab = create_pbr_material("Mat_CabSlate", CONFIG["cab_slate"], metallic=0.35, roughness=0.42)
    mat_chrome = create_pbr_material("Mat_ChromeSteel", CONFIG["metal_chrome"], metallic=0.88, roughness=0.22)
    mat_tire = create_pbr_material("Mat_TireRubber", CONFIG["tire_rubber"], metallic=0.04, roughness=0.85)
    mat_glass = create_pbr_material("Mat_Windshield", CONFIG["glass_tint"], metallic=0.1, roughness=0.1)
    mat_hazard_y = create_pbr_material("Mat_HazardYellow", CONFIG["hazard_yellow"], metallic=0.1, roughness=0.35, emission=CONFIG["hazard_yellow"], emission_strength=1.5)
    mat_hazard_k = create_pbr_material("Mat_HazardBlack", CONFIG["hazard_black"], metallic=0.1, roughness=0.6)
    mat_beacon = create_pbr_material("Mat_BeaconAmber", CONFIG["beacon_amber"], metallic=0.1, roughness=0.1, emission=CONFIG["beacon_amber"], emission_strength=2.8)
    mat_headlight = create_pbr_material("Mat_HeadlightXenon", CONFIG["headlight_xenon"], metallic=0.1, roughness=0.1, emission=CONFIG["headlight_xenon"], emission_strength=3.0)
    mat_taillight = create_pbr_material("Mat_TaillightRed", CONFIG["taillight_red"], metallic=0.1, roughness=0.1, emission=CONFIG["taillight_red"], emission_strength=2.2)

    # --------------------------------------------------------------------------
    # 1. HEAVY CHASSIS & DUAL AXLE WHEELS
    # --------------------------------------------------------------------------
    # Main Chassis Longitudinal Steel Beams
    add_box(
        "Chassis_Beams",
        size=(w * 0.72, l - 1.2, 0.32),
        location=(0, 0, 0.48),
        material=mat_cab,
        parent=root
    )

    # Heavy Duty Dual Wheels (3 Axles: Front steering, Dual rear drive)
    wheel_y_positions = [-l * 0.38, l * 0.16, l * 0.36]
    wheel_radius = 0.52
    wheel_width = 0.34

    for ax_idx, wy in enumerate(wheel_y_positions):
        for side in (-1, 1):
            wheel_obj = add_cylinder(
                f"Wheel_{ax_idx}_{'R' if side > 0 else 'L'}",
                radius=wheel_radius,
                depth=wheel_width,
                location=(side * (w / 2.0 + 0.04), wy, wheel_radius),
                rotation=(0, math.radians(90), 0),
                material=mat_tire,
                parent=root
            )
            # Wheel Metallic Rim
            add_cylinder(
                f"Rim_{ax_idx}_{'R' if side > 0 else 'L'}",
                radius=wheel_radius * 0.55,
                depth=wheel_width + 0.02,
                location=(side * (w / 2.0 + 0.04), wy, wheel_radius),
                rotation=(0, math.radians(90), 0),
                material=mat_chrome,
                parent=root
            )

    # Dual Fuel / Hydraulic Tanks
    for side in (-1, 1):
        add_cylinder(
            f"HydraulicTank_{'R' if side > 0 else 'L'}",
            radius=0.26,
            depth=2.2,
            location=(side * (w / 2.0 - 0.16), -0.8, 0.62),
            rotation=(math.radians(90), 0, 0),
            material=mat_chrome,
            parent=root
        )

    # --------------------------------------------------------------------------
    # 2. MAIN TRUCK BODY (BASED ON VARIANT)
    # --------------------------------------------------------------------------
    cargo_len = l * 0.68
    cargo_y = l * 0.14
    cargo_h = h - 0.68

    if variant_name == "standard":
        # VARIANT 1: STANDARD MUNICIPAL DUMP / BLOCK TRUCK
        # Rusty olive-green dump compactor body
        add_box(
            "Compactor_Dump_Body",
            size=(w, cargo_len, cargo_h),
            location=(0, cargo_y, cargo_h / 2.0 + 0.62),
            material=mat_green_dump,
            parent=root
        )
        # Vertical industrial reinforcement ribs
        for r_idx in range(6):
            ry = cargo_y - cargo_len / 2.0 + 1.2 + r_idx * ((cargo_len - 2.4) / 5.0)
            for side in (-1, 1):
                add_box(
                    f"Dump_Rib_{r_idx}_{'R' if side > 0 else 'L'}",
                    size=(0.07, 0.22, cargo_h * 0.90),
                    location=(side * (w / 2.0 + 0.035), ry, cargo_h / 2.0 + 0.62),
                    material=mat_rust,
                    parent=root
                )

        # Rooftop Catwalk Platform (Running surface at y = 3.8m)
        add_box(
            "Roof_Catwalk",
            size=(w * 0.92, cargo_len + 0.2, 0.14),
            location=(0, cargo_y, h - 0.07),
            material=mat_cab,
            parent=root
        )

        # Rear Compactor Hopper Door
        add_box(
            "Rear_Hopper_Door",
            size=(w - 0.10, 0.40, cargo_h * 0.85),
            location=(0, cargo_y + cargo_len / 2.0 + 0.18, cargo_h / 2.0 + 0.58),
            material=mat_rust,
            parent=root
        )

    elif variant_name == "moving":
        # VARIANT 3: MOVING TRUCK (CONTAINER CARGO BODY WITH SIDE CHEVRONS)
        # Vibrant safety orange container body
        add_box(
            "Moving_Container_Body",
            size=(w, cargo_len, cargo_h),
            location=(0, cargo_y, cargo_h / 2.0 + 0.62),
            material=mat_orange,
            parent=root
        )

        # Rooftop Catwalk Platform
        add_box(
            "Roof_Catwalk",
            size=(w * 0.92, cargo_len + 0.2, 0.14),
            location=(0, cargo_y, h - 0.07),
            material=mat_cab,
            parent=root
        )

        # YELLOW AND BLACK CHEVRON SIDE PATTERNS along both lower sides
        num_side_chevrons = 8
        chevron_w = (cargo_len - 2.0) / float(num_side_chevrons)
        for c_idx in range(num_side_chevrons):
            cy = cargo_y - cargo_len / 2.0 + 1.0 + (c_idx + 0.5) * chevron_w
            mat_c = mat_hazard_y if (c_idx % 2 == 0) else mat_hazard_k
            for side in (-1, 1):
                add_box(
                    f"Side_Chevron_{c_idx}_{'R' if side > 0 else 'L'}",
                    size=(0.03, chevron_w * 0.90, 0.38),
                    location=(side * (w / 2.0 + 0.02), cy, 1.25),
                    rotation=(0, 0, math.radians(25)),
                    material=mat_c,
                    parent=root
                )

        # Dual Rooftop Flashing Amber Beacons
        for side in (-0.75, 0.75):
            add_cylinder(
                f"Roof_Beacon_{'R' if side > 0 else 'L'}",
                radius=0.15,
                depth=0.18,
                location=(side, cargo_y - cargo_len / 2.0 + 0.5, h + 0.14),
                material=mat_beacon,
                parent=root
            )

        # Dual Vertical Chrome Exhaust Stacks
        for side in (-w / 2.0 + 0.15, w / 2.0 - 0.15):
            add_cylinder(
                f"Exhaust_Stack_{'R' if side > 0 else 'L'}",
                radius=0.08,
                depth=2.4,
                location=(side, cargo_y - cargo_len / 2.0 - 0.15, h - 0.2),
                material=mat_chrome,
                parent=root
            )

    elif variant_name == "ramp":
        # VARIANT 2: RAMP TRUCK (FRONT METAL WEDGE INCLINE RAMP)
        # Industrial teal cargo box behind ramp
        add_box(
            "Ramp_Container_Body",
            size=(w, cargo_len, cargo_h),
            location=(0, cargo_y, cargo_h / 2.0 + 0.62),
            material=mat_teal,
            parent=root
        )

        # Rooftop Catwalk Platform
        add_box(
            "Roof_Catwalk",
            size=(w * 0.92, cargo_len + 0.2, 0.14),
            location=(0, cargo_y, h - 0.07),
            material=mat_cab,
            parent=root
        )

        # Front Incline Wedge Ramp
        ramp_len = CONFIG["ramp_length"]
        ramp_y_center = cargo_y - cargo_len / 2.0 - ramp_len / 2.0
        add_wedge_ramp(
            "Front_Incline_Ramp",
            width=w - 0.06,
            length=ramp_len,
            height=h - 0.07,
            location=(0, ramp_y_center, 0.0),
            material_deck=mat_cab,
            material_stripe=mat_hazard_y,
            parent=root
        )

        # Side Steel Guard Rails along the ramp slope
        ramp_angle = math.atan2(h - 0.07, ramp_len)
        rail_hyp = math.sqrt(ramp_len * ramp_len + (h - 0.07) * (h - 0.07))
        for side in (-1, 1):
            add_box(
                f"Ramp_Rail_{'R' if side > 0 else 'L'}",
                size=(0.06, rail_hyp, 0.18),
                location=(side * (w / 2.0 - 0.04), ramp_y_center, (h - 0.07) / 2.0 + 0.24),
                rotation=(ramp_angle, 0, 0),
                material=mat_hazard_y,
                parent=root
            )

        # Amber Flashing Beacon at Ramp Peak
        add_cylinder(
            "Beacon_Ramp_Peak",
            radius=0.15,
            depth=0.18,
            location=(0, cargo_y - cargo_len / 2.0 - 0.20, h + 0.12),
            material=mat_beacon,
            parent=root
        )

    # --------------------------------------------------------------------------
    # 3. DRIVER CABIN (FOR STANDARD & MOVING VARIANTS)
    # --------------------------------------------------------------------------
    if variant_name in ("standard", "moving"):
        cab_len = l * 0.28
        cab_y = -l * 0.34
        cab_h = h - 0.35

        # Driver Cab Shell
        add_box(
            "Driver_Cab_Block",
            size=(w - 0.06, cab_len, cab_h),
            location=(0, cab_y, cab_h / 2.0 + 0.48),
            material=mat_cab,
            parent=root
        )

        # Wrap-around Tinted Windshield
        add_box(
            "Windshield",
            size=(w - 0.24, 0.12, 0.95),
            location=(0, cab_y - cab_len / 2.0 - 0.02, h - 1.05),
            rotation=(math.radians(-12), 0, 0),
            material=mat_glass,
            parent=root
        )

        # Side Windows
        for side in (-1, 1):
            add_box(
                f"SideWindow_{'R' if side > 0 else 'L'}",
                size=(0.08, cab_len * 0.45, 0.75),
                location=(side * (w / 2.0 - 0.01), cab_y - 0.2, h - 1.10),
                material=mat_glass,
                parent=root
            )
            # Side Mirrors
            add_box(
                f"SideMirror_{'R' if side > 0 else 'L'}",
                size=(0.06, 0.22, 0.38),
                location=(side * (w / 2.0 + 0.18), cab_y - cab_len / 2.0 + 0.35, h - 1.0),
                material=mat_chrome,
                parent=root
            )

        # Front Heavy Bull-Bar Bumper & Grille
        add_box(
            "Front_Bumper",
            size=(w + 0.14, 0.42, 0.55),
            location=(0, cab_y - cab_len / 2.0 - 0.22, 0.72),
            material=mat_cab,
            parent=root
        )
        add_box(
            "Chrome_Grille",
            size=(w - 0.42, 0.12, 0.85),
            location=(0, cab_y - cab_len / 2.0 - 0.12, 1.15),
            material=mat_chrome,
            parent=root
        )

        # Xenon Headlights
        for side in (-w / 2.0 + 0.32, w / 2.0 - 0.32):
            add_box(
                f"Headlight_{'R' if side > 0 else 'L'}",
                size=(0.35, 0.12, 0.25),
                location=(side, cab_y - cab_len / 2.0 - 0.24, 0.95),
                material=mat_headlight,
                parent=root
            )

    # Rear Red Brake Lights
    for side in (-w / 2.0 + 0.28, w / 2.0 - 0.28):
        add_box(
            f"Taillight_{'R' if side > 0 else 'L'}",
            size=(0.32, 0.10, 0.22),
            location=(side, cargo_y + cargo_len / 2.0 + 0.22, 0.85),
            material=mat_taillight,
            parent=root
        )

    return root


# ==============================================================================
# EXPORT PIPELINE
# ==============================================================================
def export_all_trucks():
    cwd = os.getcwd()
    
    print("=" * 65)
    print("MUNICIPAL GARBAGE TRUCKS GENERATOR (3 DISTINCT VARIATIONS)")
    print("=" * 65)

    # 1. Export Standard Block Truck (and moving truck) to truck.glb
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print("-> Assembling Standard Block Truck (truck.glb)...")
    build_truck_variant("standard")
    truck_path = os.path.join(cwd, "truck.glb")
    bpy.ops.export_scene.gltf(
        filepath=truck_path,
        export_format="GLB",
        use_selection=False,
        export_materials="EXPORT",
        export_normals=True,
        export_apply=True,
        export_yup=True
    )
    if os.path.exists(truck_path):
        size_kb = os.path.getsize(truck_path) / 1024.0
        print(f"SUCCESS: truck.glb exported successfully! ({size_kb:.1f} KB)")

    # 2. Export Ramp Truck to truck_ramp.glb for direct Three.js runtime use
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print("-> Assembling Ramp Truck (truck_ramp.glb)...")
    build_truck_variant("ramp")
    ramp_path = os.path.join(cwd, "truck_ramp.glb")
    bpy.ops.export_scene.gltf(
        filepath=ramp_path,
        export_format="GLB",
        use_selection=False,
        export_materials="EXPORT",
        export_normals=True,
        export_apply=True,
        export_yup=True
    )
    if os.path.exists(ramp_path):
        size_kb = os.path.getsize(ramp_path) / 1024.0
        print(f"SUCCESS: truck_ramp.glb exported successfully! ({size_kb:.1f} KB)")

    # 3. Export Moving Truck variation
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print("-> Assembling Moving Truck Variation (truck_moving.glb)...")
    build_truck_variant("moving")
    moving_path = os.path.join(cwd, "truck_moving.glb")
    bpy.ops.export_scene.gltf(
        filepath=moving_path,
        export_format="GLB",
        use_selection=False,
        export_materials="EXPORT",
        export_normals=True,
        export_apply=True,
        export_yup=True
    )
    if os.path.exists(moving_path):
        size_kb = os.path.getsize(moving_path) / 1024.0
        print(f"SUCCESS: truck_moving.glb exported successfully! ({size_kb:.1f} KB)")


if __name__ == "__main__":
    export_all_trucks()
