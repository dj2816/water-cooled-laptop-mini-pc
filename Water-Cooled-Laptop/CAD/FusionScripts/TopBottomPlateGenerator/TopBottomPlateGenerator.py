import adsk.core
import adsk.fusion
import json
import math
import os
import traceback


SCRIPT_ID = "DJFH_RAMSidePlateGenerator"
FILE_STEM = "RAMSidePlate"

DEFAULTS = {
    "mainboardLength": 355.0,
    "mainboardWidth": 236.0,
    "acrylicThickness": 3.0,
    "assemblyClearance": 1.0,
    "sideWallThickness": 3.0,
    "cornerRadius": 3.0,
    "ventDiameter": 55.0,
    "ventOffsetTopFromBoard": 71.0,
    "ventOffsetSideFromBoard": 48.0,
    "mountHoleDiameter": 3.2,
    "accessHoleDiameter": 30.0,
    "accessHoleOffsetLeft": 22.0,
    "accessHoleOffsetBottom": 30.0,
    "topMountOffsetSide": 21.0,
    "topMountOffsetTop": 46.0,
    "newTopHoleOffsetTop": 6.0,
    "newTopHole1OffsetLeft": 95.0,
    "newTopHole2OffsetRight": 107.0,
    "bottomMountOffsetLeft": 12.0,
    "bottomMountOffsetRight": 12.0,
    "bottomMountOffsetBottom": 6.0,
    "cutQuantity": 1,
}

LENGTH_PARAMETERS = {
    "mainboardLength",
    "mainboardWidth",
    "acrylicThickness",
    "assemblyClearance",
    "sideWallThickness",
    "cornerRadius",
    "ventDiameter",
    "ventOffsetTopFromBoard",
    "ventOffsetSideFromBoard",
    "mountHoleDiameter",
    "accessHoleDiameter",
    "accessHoleOffsetLeft",
    "accessHoleOffsetBottom",
    "topMountOffsetSide",
    "topMountOffsetTop",
    "newTopHoleOffsetTop",
    "newTopHole1OffsetLeft",
    "newTopHole2OffsetRight",
    "bottomMountOffsetLeft",
    "bottomMountOffsetRight",
    "bottomMountOffsetBottom",
}


def _mm_to_cm(value):
    return value / 10.0


def _point_mm(x, y):
    return adsk.core.Point3D.create(_mm_to_cm(x), _mm_to_cm(y), 0)


def _polar_mm(cx, cy, radius, angle):
    return _point_mm(cx + radius * math.cos(angle), cy + radius * math.sin(angle))


def _read_existing_values(app):
    values = dict(DEFAULTS)
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        return values

    generated_component = None
    for index in range(design.rootComponent.occurrences.count):
        occurrence = design.rootComponent.occurrences.item(index)
        if occurrence.component.name == FILE_STEM:
            generated_component = occurrence.component
            break
    if not generated_component:
        return values

    for name in DEFAULTS:
        parameter = design.userParameters.itemByName(name)
        if not parameter:
            continue
        if name in LENGTH_PARAMETERS:
            values[name] = parameter.value * 10.0
        else:
            values[name] = int(round(parameter.value))
    return values


def _add_parameter(parameters, name, expression, units, comment):
    return parameters.add(
        name,
        adsk.core.ValueInput.createByString(expression),
        units,
        comment,
    )


def _add_user_parameters(design, values):
    parameters = design.userParameters

    _add_parameter(parameters, "mainboardLength", f"{values['mainboardLength']} mm", "mm", "Motherboard envelope length")
    _add_parameter(parameters, "mainboardWidth", f"{values['mainboardWidth']} mm", "mm", "Motherboard envelope width")
    _add_parameter(parameters, "acrylicThickness", f"{values['acrylicThickness']} mm", "mm", "Acrylic sheet thickness")
    _add_parameter(parameters, "assemblyClearance", f"{values['assemblyClearance']} mm", "mm", "Clearance between motherboard and side wall")
    _add_parameter(parameters, "sideWallThickness", f"{values['sideWallThickness']} mm", "mm", "Reserved side-wall thickness")
    _add_parameter(parameters, "plateLength", "mainboardLength + 2 * (assemblyClearance + sideWallThickness)", "mm", "Finished plate length")
    _add_parameter(parameters, "plateWidth", "mainboardWidth + 2 * (assemblyClearance + sideWallThickness)", "mm", "Finished plate width")
    _add_parameter(parameters, "cornerRadius", f"{values['cornerRadius']} mm", "mm", "Portable-safe outside corner radius")
    _add_parameter(parameters, "ventDiameter", f"{values['ventDiameter']} mm", "mm", "Diameter of each fully open fan cutout")
    _add_parameter(parameters, "ventOffsetTopFromBoard", f"{values['ventOffsetTopFromBoard']} mm", "mm", "Vent center offset from motherboard top edge")
    _add_parameter(parameters, "ventOffsetSideFromBoard", f"{values['ventOffsetSideFromBoard']} mm", "mm", "Vent center offset from motherboard left/right edge")
    _add_parameter(parameters, "ventCenterOffsetX", "plateLength / 2 - (ventOffsetSideFromBoard + assemblyClearance + sideWallThickness)", "mm", "Absolute X offset of either vent center")
    _add_parameter(parameters, "ventCenterOffsetY", "plateWidth / 2 - (ventOffsetTopFromBoard + assemblyClearance + sideWallThickness)", "mm", "Y offset of both vent centers")
    _add_parameter(parameters, "mountHoleDiameter", f"{values['mountHoleDiameter']} mm", "mm", "M3 screw clearance-hole diameter")
    _add_parameter(parameters, "accessHoleDiameter", f"{values['accessHoleDiameter']} mm", "mm", "Diameter of the lower-left access opening")
    _add_parameter(parameters, "accessHoleOffsetLeft", f"{values['accessHoleOffsetLeft']} mm", "mm", "Access-opening center from the left plate edge")
    _add_parameter(parameters, "accessHoleOffsetBottom", f"{values['accessHoleOffsetBottom']} mm", "mm", "Access-opening center from the bottom plate edge")
    _add_parameter(parameters, "topMountOffsetSide", f"{values['topMountOffsetSide']} mm", "mm", "Top mount centers from left/right plate edges")
    _add_parameter(parameters, "topMountOffsetTop", f"{values['topMountOffsetTop']} mm", "mm", "Top mount centers from top plate edge")
    _add_parameter(parameters, "newTopHoleOffsetTop", f"{values['newTopHoleOffsetTop']} mm", "mm", "New M3 hole centers from top plate edge")
    _add_parameter(parameters, "newTopHole1OffsetLeft", f"{values['newTopHole1OffsetLeft']} mm", "mm", "New left M3 hole center from left plate edge")
    _add_parameter(parameters, "newTopHole2OffsetRight", f"{values['newTopHole2OffsetRight']} mm", "mm", "New right M3 hole center from right plate edge")
    _add_parameter(parameters, "bottomMountOffsetLeft", f"{values['bottomMountOffsetLeft']} mm", "mm", "Leftmost bottom mount center from the left plate edge")
    _add_parameter(parameters, "bottomMountOffsetRight", f"{values['bottomMountOffsetRight']} mm", "mm", "Rightmost bottom mount center from the right plate edge")
    _add_parameter(parameters, "bottomMountOffsetBottom", f"{values['bottomMountOffsetBottom']} mm", "mm", "Four bottom mount centers from bottom plate edge")
    _add_parameter(parameters, "bottomMountSpacing", "(plateLength - bottomMountOffsetLeft - bottomMountOffsetRight) / 3", "mm", "Equal spacing between the four bottom mounts")
    _add_parameter(parameters, "cutQuantity", str(values["cutQuantity"]), "", "Cut one RAM-side plate")


def _add_rounded_rectangle(sketch, length, width, radius):
    curves = sketch.sketchCurves
    lines = curves.sketchLines
    arcs = curves.sketchArcs
    half_l = length / 2.0
    half_w = width / 2.0
    quarter_turn = math.pi / 2.0

    lines.addByTwoPoints(_point_mm(-half_l + radius, -half_w), _point_mm(half_l - radius, -half_w))
    arcs.addByCenterStartSweep(
        _point_mm(half_l - radius, -half_w + radius),
        _point_mm(half_l - radius, -half_w),
        quarter_turn,
    )
    lines.addByTwoPoints(_point_mm(half_l, -half_w + radius), _point_mm(half_l, half_w - radius))
    arcs.addByCenterStartSweep(
        _point_mm(half_l - radius, half_w - radius),
        _point_mm(half_l, half_w - radius),
        quarter_turn,
    )
    lines.addByTwoPoints(_point_mm(half_l - radius, half_w), _point_mm(-half_l + radius, half_w))
    arcs.addByCenterStartSweep(
        _point_mm(-half_l + radius, half_w - radius),
        _point_mm(-half_l + radius, half_w),
        quarter_turn,
    )
    lines.addByTwoPoints(_point_mm(-half_l, half_w - radius), _point_mm(-half_l, -half_w + radius))
    arcs.addByCenterStartSweep(
        _point_mm(-half_l + radius, -half_w + radius),
        _point_mm(-half_l, -half_w + radius),
        quarter_turn,
    )


def _try_coincident(constraints, first, second):
    try:
        constraints.addCoincident(first, second)
    except:
        pass


def _add_swirl_openings(sketch, cx, cy, diameter, hub_diameter, rib_width, blade_count, twist_angle_deg):
    arcs = sketch.sketchCurves.sketchArcs
    constraints = sketch.geometricConstraints
    outer_radius = diameter / 2.0
    inner_radius = hub_diameter / 2.0
    sector_angle = 2.0 * math.pi / blade_count
    twist_angle = math.radians(twist_angle_deg)

    if inner_radius <= rib_width / 2.0:
        raise ValueError("grilleHubDiameter must be larger than grilleRibWidth")
    if outer_radius <= inner_radius + rib_width:
        raise ValueError("ventDiameter is too small for the selected hub and rib width")

    blade_angle_inner = 2.0 * math.asin(min(0.999, rib_width / (2.0 * inner_radius)))
    blade_angle_outer = 2.0 * math.asin(min(0.999, rib_width / (2.0 * outer_radius)))
    gap_angle_inner = sector_angle - blade_angle_inner
    gap_angle_outer = sector_angle - blade_angle_outer
    if gap_angle_inner <= 0 or gap_angle_outer <= 0:
        raise ValueError("Rib width leaves no open airflow region")

    middle_radius = (inner_radius + outer_radius) / 2.0
    for index in range(blade_count):
        inner_center_angle = index * sector_angle
        outer_center_angle = inner_center_angle + twist_angle

        inner_start_angle = inner_center_angle - gap_angle_inner / 2.0
        inner_end_angle = inner_center_angle + gap_angle_inner / 2.0
        outer_start_angle = outer_center_angle - gap_angle_outer / 2.0
        outer_end_angle = outer_center_angle + gap_angle_outer / 2.0

        inner_start = _polar_mm(cx, cy, inner_radius, inner_start_angle)
        inner_end = _polar_mm(cx, cy, inner_radius, inner_end_angle)
        outer_start = _polar_mm(cx, cy, outer_radius, outer_start_angle)
        outer_end = _polar_mm(cx, cy, outer_radius, outer_end_angle)

        side_one_middle = _polar_mm(
            cx,
            cy,
            middle_radius,
            (inner_start_angle + outer_start_angle) / 2.0,
        )
        side_two_middle = _polar_mm(
            cx,
            cy,
            middle_radius,
            (inner_end_angle + outer_end_angle) / 2.0,
        )

        inner_arc = arcs.addByCenterStartSweep(
            _point_mm(cx, cy),
            inner_start,
            gap_angle_inner,
        )
        outer_arc = arcs.addByCenterStartSweep(
            _point_mm(cx, cy),
            outer_start,
            gap_angle_outer,
        )
        side_one = arcs.addByThreePoints(inner_start, side_one_middle, outer_start)
        side_two = arcs.addByThreePoints(inner_end, side_two_middle, outer_end)

        _try_coincident(constraints, inner_arc.startSketchPoint, side_one.startSketchPoint)
        _try_coincident(constraints, inner_arc.endSketchPoint, side_two.startSketchPoint)
        _try_coincident(constraints, outer_arc.startSketchPoint, side_one.endSketchPoint)
        _try_coincident(constraints, outer_arc.endSketchPoint, side_two.endSketchPoint)


def _add_mount_holes(sketch, plate_length, plate_width, values):
    circles = sketch.sketchCurves.sketchCircles
    radius = values["mountHoleDiameter"] / 2.0
    bottom_spacing = (
        plate_length - values["bottomMountOffsetLeft"] - values["bottomMountOffsetRight"]
    ) / 3.0
    bottom_y_from_top = plate_width - values["bottomMountOffsetBottom"]
    hole_positions_from_top_left = [
        (values["newTopHole1OffsetLeft"], values["newTopHoleOffsetTop"]),
        (plate_length - values["newTopHole2OffsetRight"], values["newTopHoleOffsetTop"]),
        (values["topMountOffsetSide"], values["topMountOffsetTop"]),
        (plate_length - values["topMountOffsetSide"], values["topMountOffsetTop"]),
    ]
    hole_positions_from_top_left.extend(
        (values["bottomMountOffsetLeft"] + index * bottom_spacing, bottom_y_from_top)
        for index in range(4)
    )
    for x_from_left, y_from_top in hole_positions_from_top_left:
        centered_x = x_from_left - plate_length / 2.0
        centered_y = plate_width / 2.0 - y_from_top
        circles.addByCenterRadius(_point_mm(centered_x, centered_y), _mm_to_cm(radius))

    return tuple(hole_positions_from_top_left)


def _largest_profile(sketch):
    largest = None
    largest_area = -1.0
    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        try:
            properties = profile.areaProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
        except:
            properties = profile.areaProperties()
        if properties.area > largest_area:
            largest_area = properties.area
            largest = profile
    return largest, largest_area


def _export_design(design, component, sketch, output_dir, app):
    export_manager = design.exportManager
    f3d_path = os.path.join(output_dir, FILE_STEM + ".f3d")
    step_path = os.path.join(output_dir, FILE_STEM + ".step")
    dxf_path = os.path.join(output_dir, FILE_STEM + "_QTY1_1to1.dxf")
    preview_path = os.path.join(output_dir, FILE_STEM + "_preview.png")

    for path in (f3d_path, step_path, dxf_path, preview_path):
        if os.path.exists(path):
            os.remove(path)

    dxf_options = export_manager.createDXFSketchExportOptions(dxf_path, sketch)
    if not dxf_options or not export_manager.execute(dxf_options):
        raise RuntimeError("DXF export failed")

    step_options = export_manager.createSTEPExportOptions(step_path, component)
    if not export_manager.execute(step_options):
        raise RuntimeError("STEP export failed")

    f3d_options = export_manager.createFusionArchiveExportOptions(f3d_path)
    if not export_manager.execute(f3d_options):
        raise RuntimeError("F3D export failed")

    viewport = app.activeViewport
    viewport.fit()
    adsk.doEvents()
    viewport.saveAsImageFile(preview_path, 1600, 1100)

    return {
        "f3d": f3d_path,
        "step": step_path,
        "dxf": dxf_path,
        "preview": preview_path,
    }


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        values = _read_existing_values(app)
        for revised_name in (
            "acrylicThickness",
            "accessHoleDiameter",
            "accessHoleOffsetLeft",
            "accessHoleOffsetBottom",
            "newTopHoleOffsetTop",
            "newTopHole1OffsetLeft",
            "newTopHole2OffsetRight",
            "bottomMountOffsetLeft",
            "bottomMountOffsetRight",
            "bottomMountOffsetBottom",
        ):
            values[revised_name] = DEFAULTS[revised_name]

        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        output_dir = os.path.join(workspace_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        root = design.rootComponent
        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = FILE_STEM

        _add_user_parameters(design, values)

        plate_length = values["mainboardLength"] + 2.0 * (values["assemblyClearance"] + values["sideWallThickness"])
        plate_width = values["mainboardWidth"] + 2.0 * (values["assemblyClearance"] + values["sideWallThickness"])
        extra_per_side = values["assemblyClearance"] + values["sideWallThickness"]
        center_x = plate_length / 2.0 - (values["ventOffsetSideFromBoard"] + extra_per_side)
        center_y = plate_width / 2.0 - (values["ventOffsetTopFromBoard"] + extra_per_side)

        sketch = component.sketches.add(component.xYConstructionPlane)
        sketch.name = "Cut_Profile_1to1_QTY1"
        sketch.isComputeDeferred = True
        _add_rounded_rectangle(sketch, plate_length, plate_width, values["cornerRadius"])
        circles = sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(_point_mm(-center_x, center_y), _mm_to_cm(values["ventDiameter"] / 2.0))
        circles.addByCenterRadius(_point_mm(center_x, center_y), _mm_to_cm(values["ventDiameter"] / 2.0))
        access_center_x = values["accessHoleOffsetLeft"] - plate_length / 2.0
        access_center_y = values["accessHoleOffsetBottom"] - plate_width / 2.0
        circles.addByCenterRadius(
            _point_mm(access_center_x, access_center_y),
            _mm_to_cm(values["accessHoleDiameter"] / 2.0),
        )
        mount_hole_positions = _add_mount_holes(sketch, plate_length, plate_width, values)
        sketch.isComputeDeferred = False
        adsk.doEvents()

        profile, profile_area_cm2 = _largest_profile(sketch)
        expected_profile_count = 1 + 2 + 1 + len(mount_hole_positions)
        if not profile or sketch.profiles.count < expected_profile_count:
            raise RuntimeError(
                f"Expected at least {expected_profile_count} closed profiles, found {sketch.profiles.count}"
            )

        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extent = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString("acrylicThickness")
        )
        extrude_input.setOneSideExtent(extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extrude = extrudes.add(extrude_input)
        extrude.name = "Acrylic_Plate_3mm"
        body = extrude.bodies.item(0)
        body.name = "RAMSidePlate_QTY1"

        paths = _export_design(design, component, sketch, output_dir, app)
        sketch.isVisible = False

        report = {
            "script": SCRIPT_ID,
            "part_name": FILE_STEM,
            "quantity": values["cutQuantity"],
            "units": "mm",
            "plate": {
                "length": plate_length,
                "width": plate_width,
                "thickness": values["acrylicThickness"],
                "corner_radius": values["cornerRadius"],
            },
            "vents": {
                "diameter": values["ventDiameter"],
                "opening_type": "fully open circular cutout",
                "left_center_from_left": values["ventOffsetSideFromBoard"] + extra_per_side,
                "right_center_from_right": values["ventOffsetSideFromBoard"] + extra_per_side,
                "center_from_top": values["ventOffsetTopFromBoard"] + extra_per_side,
            },
            "mount_holes": {
                "diameter": values["mountHoleDiameter"],
                "thread": "M3 clearance",
                "centers_from_top_left": [list(position) for position in mount_hole_positions],
            },
            "access_hole": {
                "diameter": values["accessHoleDiameter"],
                "radius": values["accessHoleDiameter"] / 2.0,
                "center_from_left": values["accessHoleOffsetLeft"],
                "center_from_bottom": values["accessHoleOffsetBottom"],
            },
            "fusion": {
                "profile_count": sketch.profiles.count,
                "solid_body_count": component.bRepBodies.count,
                "largest_profile_area_mm2": profile_area_cm2 * 100.0,
                "user_parameter_count": design.userParameters.count,
            },
            "files": paths,
            "note": "RAM-side plate with two fully open fan cutouts, one 30 mm lower-left access opening, eight shared M3 holes including two new top-edge holes, and four evenly spaced bottom M3 holes.",
        }
        report_path = os.path.join(output_dir, FILE_STEM + "_report.json")
        with open(report_path, "w", encoding="utf-8") as report_file:
            json.dump(report, report_file, indent=2, ensure_ascii=False)

        ui.messageBox(
            "RAM-side plate generated successfully.\n\n"
            f"Plate: {plate_length:.1f} x {plate_width:.1f} x {values['acrylicThickness']:.1f} mm\n"
            f"Full-open vent centers: 52 mm from left/right, 75 mm from top\n"
            "Lower-left access opening: diameter 30 mm, center 22 mm from left and 30 mm from bottom\n"
            f"M3 clearance holes: diameter {values['mountHoleDiameter']:.1f} mm, 8 places\n"
            f"Output: {output_dir}"
        )
    except:
        if ui:
            ui.messageBox("Generation failed:\n\n" + traceback.format_exc())


def stop(context):
    pass
