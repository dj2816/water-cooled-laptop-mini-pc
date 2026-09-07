import adsk.core
import adsk.fusion
import json
import math
import os
import traceback


SCRIPT_ID = "DJFH_SolidBackPlateGenerator"
FILE_STEM = "SolidBackPlate"

DEFAULTS = {
    "mainboardLength": 355.0,
    "mainboardWidth": 236.0,
    "acrylicThickness": 3.0,
    "assemblyClearance": 1.0,
    "sideWallThickness": 3.0,
    "cornerRadius": 3.0,
    "mountHoleDiameter": 3.2,
    "topNotchWidth": 5.0,
    "topNotchDepth": 5.0,
    "topNotchRightEdgeOffsetRight": 180.0,
    "topMountOffsetSide": 21.0,
    "topMountOffsetTop": 46.0,
    "newTopHoleOffsetTop": 6.0,
    "newTopHole1OffsetLeft": 95.0,
    "newTopHole2OffsetRight": 107.0,
    "bottomMountOffsetLeft": 12.0,
    "bottomMountOffsetRight": 12.0,
    "bottomMountOffsetBottom": 6.0,
    "additionalHole1Left": 36.0,
    "additionalHole1Bottom": 4.0,
    "additionalHole2Left": 47.0,
    "additionalHole2Bottom": 11.0,
    "additionalHole3Left": 46.0,
    "additionalHole3Bottom": 19.0,
    "additionalHole4Left": 22.0,
    "additionalHole4Bottom": 46.0,
    "cutQuantity": 1,
}

LENGTH_PARAMETERS = {
    "mainboardLength",
    "mainboardWidth",
    "acrylicThickness",
    "assemblyClearance",
    "sideWallThickness",
    "cornerRadius",
    "mountHoleDiameter",
    "topNotchWidth",
    "topNotchDepth",
    "topNotchRightEdgeOffsetRight",
    "topMountOffsetSide",
    "topMountOffsetTop",
    "newTopHoleOffsetTop",
    "newTopHole1OffsetLeft",
    "newTopHole2OffsetRight",
    "bottomMountOffsetLeft",
    "bottomMountOffsetRight",
    "bottomMountOffsetBottom",
    "additionalHole1Left",
    "additionalHole1Bottom",
    "additionalHole2Left",
    "additionalHole2Bottom",
    "additionalHole3Left",
    "additionalHole3Bottom",
    "additionalHole4Left",
    "additionalHole4Bottom",
}


def _mm_to_cm(value):
    return value / 10.0


def _point_mm(x, y):
    return adsk.core.Point3D.create(_mm_to_cm(x), _mm_to_cm(y), 0)


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
    _add_parameter(parameters, "assemblyClearance", f"{values['assemblyClearance']} mm", "mm", "Clearance reserved around the motherboard")
    _add_parameter(parameters, "sideWallThickness", f"{values['sideWallThickness']} mm", "mm", "Original side-wall allowance retained in plate size")
    _add_parameter(parameters, "plateLength", "mainboardLength + 2 * (assemblyClearance + sideWallThickness)", "mm", "Finished plate length")
    _add_parameter(parameters, "plateWidth", "mainboardWidth + 2 * (assemblyClearance + sideWallThickness)", "mm", "Finished plate width")
    _add_parameter(parameters, "cornerRadius", f"{values['cornerRadius']} mm", "mm", "Outside corner radius")
    _add_parameter(parameters, "mountHoleDiameter", f"{values['mountHoleDiameter']} mm", "mm", "M3 screw clearance-hole diameter")
    _add_parameter(parameters, "topNotchWidth", f"{values['topNotchWidth']} mm", "mm", "Top-edge notch width")
    _add_parameter(parameters, "topNotchDepth", f"{values['topNotchDepth']} mm", "mm", "Top-edge notch depth")
    _add_parameter(parameters, "topNotchRightEdgeOffsetRight", f"{values['topNotchRightEdgeOffsetRight']} mm", "mm", "Notch right edge from right plate edge")
    _add_parameter(parameters, "topMountOffsetSide", f"{values['topMountOffsetSide']} mm", "mm", "Top mount centers from left/right plate edges")
    _add_parameter(parameters, "topMountOffsetTop", f"{values['topMountOffsetTop']} mm", "mm", "Top mount centers from top plate edge")
    _add_parameter(parameters, "newTopHoleOffsetTop", f"{values['newTopHoleOffsetTop']} mm", "mm", "New M3 hole centers from top plate edge")
    _add_parameter(parameters, "newTopHole1OffsetLeft", f"{values['newTopHole1OffsetLeft']} mm", "mm", "New left M3 hole center from left plate edge")
    _add_parameter(parameters, "newTopHole2OffsetRight", f"{values['newTopHole2OffsetRight']} mm", "mm", "New right M3 hole center from right plate edge")
    _add_parameter(parameters, "bottomMountOffsetLeft", f"{values['bottomMountOffsetLeft']} mm", "mm", "Leftmost bottom mount center from the left plate edge")
    _add_parameter(parameters, "bottomMountOffsetRight", f"{values['bottomMountOffsetRight']} mm", "mm", "Rightmost bottom mount center from the right plate edge")
    _add_parameter(parameters, "bottomMountOffsetBottom", f"{values['bottomMountOffsetBottom']} mm", "mm", "Four bottom mount centers from bottom plate edge")
    _add_parameter(parameters, "bottomMountSpacing", "(plateLength - bottomMountOffsetLeft - bottomMountOffsetRight) / 3", "mm", "Equal spacing between the four bottom mounts")
    for index in range(1, 5):
        _add_parameter(parameters, f"additionalHole{index}Left", f"{values[f'additionalHole{index}Left']} mm", "mm", f"Additional M3 hole {index} center from left plate edge")
        _add_parameter(parameters, f"additionalHole{index}Bottom", f"{values[f'additionalHole{index}Bottom']} mm", "mm", f"Additional M3 hole {index} center from bottom plate edge")
    _add_parameter(parameters, "cutQuantity", str(values["cutQuantity"]), "", "Cut one solid back plate")


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


def _add_rounded_rectangle_with_top_notch(
    sketch,
    length,
    width,
    radius,
    notch_width,
    notch_depth,
    notch_right_edge_offset_right,
):
    curves = sketch.sketchCurves
    lines = curves.sketchLines
    arcs = curves.sketchArcs
    half_l = length / 2.0
    half_w = width / 2.0
    quarter_turn = math.pi / 2.0
    notch_right_x = half_l - notch_right_edge_offset_right
    notch_left_x = notch_right_x - notch_width
    notch_bottom_y = half_w - notch_depth

    if notch_width <= 0 or notch_depth <= 0:
        raise ValueError("Top notch width and depth must be positive")
    if notch_left_x <= -half_l + radius or notch_right_x >= half_l - radius:
        raise ValueError("Top notch must stay within the straight portion of the top edge")

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
    lines.addByTwoPoints(_point_mm(half_l - radius, half_w), _point_mm(notch_right_x, half_w))
    lines.addByTwoPoints(_point_mm(notch_right_x, half_w), _point_mm(notch_right_x, notch_bottom_y))
    lines.addByTwoPoints(_point_mm(notch_right_x, notch_bottom_y), _point_mm(notch_left_x, notch_bottom_y))
    lines.addByTwoPoints(_point_mm(notch_left_x, notch_bottom_y), _point_mm(notch_left_x, half_w))
    lines.addByTwoPoints(_point_mm(notch_left_x, half_w), _point_mm(-half_l + radius, half_w))
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


def _add_additional_holes(sketch, plate_length, plate_width, values):
    circles = sketch.sketchCurves.sketchCircles
    radius = values["mountHoleDiameter"] / 2.0
    hole_positions_from_bottom_left = tuple(
        (
            values[f"additionalHole{index}Left"],
            values[f"additionalHole{index}Bottom"],
        )
        for index in range(1, 5)
    )
    for x_from_left, y_from_bottom in hole_positions_from_bottom_left:
        centered_x = x_from_left - plate_length / 2.0
        centered_y = y_from_bottom - plate_width / 2.0
        circles.addByCenterRadius(_point_mm(centered_x, centered_y), _mm_to_cm(radius))

    return hole_positions_from_bottom_left


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
            "topNotchWidth",
            "topNotchDepth",
            "topNotchRightEdgeOffsetRight",
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

        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
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

        sketch = component.sketches.add(component.xYConstructionPlane)
        sketch.name = "Cut_Profile_1to1_QTY1"
        sketch.isComputeDeferred = True
        _add_rounded_rectangle_with_top_notch(
            sketch,
            plate_length,
            plate_width,
            values["cornerRadius"],
            values["topNotchWidth"],
            values["topNotchDepth"],
            values["topNotchRightEdgeOffsetRight"],
        )
        mount_hole_positions = _add_mount_holes(sketch, plate_length, plate_width, values)
        additional_hole_positions = _add_additional_holes(sketch, plate_length, plate_width, values)
        sketch.isComputeDeferred = False
        adsk.doEvents()

        profile, profile_area_cm2 = _largest_profile(sketch)
        expected_profile_count = 1 + len(mount_hole_positions) + len(additional_hole_positions)
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
        body.name = "SolidBackPlate_QTY1"

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
                "count": 0,
                "description": "No ventilation openings on the solid back plate",
            },
            "top_edge_notch": {
                "width": values["topNotchWidth"],
                "depth": values["topNotchDepth"],
                "right_edge_from_right": values["topNotchRightEdgeOffsetRight"],
                "left_edge_from_left": plate_length - values["topNotchRightEdgeOffsetRight"] - values["topNotchWidth"],
                "right_edge_from_left": plate_length - values["topNotchRightEdgeOffsetRight"],
                "through_thickness": True,
            },
            "mount_holes": {
                "diameter": values["mountHoleDiameter"],
                "thread": "M3 clearance",
                "centers_from_top_left": [list(position) for position in mount_hole_positions],
            },
            "additional_m3_holes": {
                "diameter": values["mountHoleDiameter"],
                "thread": "M3 clearance",
                "centers_from_bottom_left": [list(position) for position in additional_hole_positions],
            },
            "fusion": {
                "profile_count": sketch.profiles.count,
                "solid_body_count": component.bRepBodies.count,
                "largest_profile_area_mm2": profile_area_cm2 * 100.0,
                "user_parameter_count": design.userParameters.count,
            },
            "files": paths,
            "note": "Solid back plate with twelve M3 holes and one 5 x 5 mm top-edge notch whose right edge is 180 mm from the right plate edge.",
        }
        report_path = os.path.join(output_dir, FILE_STEM + "_report.json")
        with open(report_path, "w", encoding="utf-8") as report_file:
            json.dump(report, report_file, indent=2, ensure_ascii=False)

        ui.messageBox(
            "Solid back plate generated successfully.\n\n"
            f"Plate: {plate_length:.1f} x {plate_width:.1f} x {values['acrylicThickness']:.1f} mm\n"
            "Vent openings: none\n"
            "Top-edge notch: 5 x 5 mm, right edge 180 mm from right plate edge\n"
            f"M3 clearance holes: diameter {values['mountHoleDiameter']:.1f} mm, 12 places (8 shared + 4 additional)\n"
            f"Output: {output_dir}"
        )
    except:
        if ui:
            ui.messageBox("Generation failed:\n\n" + traceback.format_exc())


def stop(context):
    pass
