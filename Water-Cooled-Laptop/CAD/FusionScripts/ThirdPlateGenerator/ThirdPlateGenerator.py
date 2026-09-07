import adsk.core
import adsk.fusion
import importlib.util
import json
import os
import traceback


SCRIPT_ID = "DJFH_ThirdPlateGenerator"
FILE_STEM = "ThirdPlate"

PLATE_LENGTH = 363.0
PLATE_WIDTH = 244.0
PLATE_THICKNESS = 3.0
CORNER_RADIUS = 3.0
MOUNT_HOLE_DIAMETER = 3.2
HOLE_CENTERS_FROM_TOP_LEFT = (
    (95.0, 6.0),
    (256.0, 6.0),
    (12.0, 238.0),
    (125.0, 238.0),
    (238.0, 238.0),
    (351.0, 238.0),
)


def _load_shared_helpers():
    shared_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "SolidBackPlateGenerator",
            "SolidBackPlateGenerator.py",
        )
    )
    spec = importlib.util.spec_from_file_location(
        "DJFH_ThirdPlate_SharedHelpers",
        shared_path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.FILE_STEM = FILE_STEM
    return module


def _add_parameter(parameters, name, expression, units, comment):
    return parameters.add(
        name,
        adsk.core.ValueInput.createByString(expression),
        units,
        comment,
    )


def _add_user_parameters(design):
    parameters = design.userParameters
    _add_parameter(parameters, "plateLength", f"{PLATE_LENGTH} mm", "mm", "Finished plate length")
    _add_parameter(parameters, "plateWidth", f"{PLATE_WIDTH} mm", "mm", "Finished plate width")
    _add_parameter(parameters, "acrylicThickness", f"{PLATE_THICKNESS} mm", "mm", "Acrylic sheet thickness")
    _add_parameter(parameters, "cornerRadius", f"{CORNER_RADIUS} mm", "mm", "Outside corner radius")
    _add_parameter(parameters, "mountHoleDiameter", f"{MOUNT_HOLE_DIAMETER} mm", "mm", "M3 screw clearance-hole diameter")
    _add_parameter(parameters, "newTopHoleOffsetTop", "6 mm", "mm", "New M3 hole centers from top edge")
    _add_parameter(parameters, "newTopHole1OffsetLeft", "95 mm", "mm", "New left M3 hole center from left edge")
    _add_parameter(parameters, "newTopHole2OffsetRight", "107 mm", "mm", "New right M3 hole center from right edge")
    _add_parameter(parameters, "bottomMountOffsetLeft", "12 mm", "mm", "Leftmost bottom M3 center from left edge")
    _add_parameter(parameters, "bottomMountOffsetRight", "12 mm", "mm", "Rightmost bottom M3 center from right edge")
    _add_parameter(parameters, "bottomMountOffsetBottom", "6 mm", "mm", "Bottom M3 centers from bottom edge")
    _add_parameter(parameters, "bottomMountSpacing", "113 mm", "mm", "Spacing between bottom M3 centers")


def _add_holes(sketch, shared):
    circles = sketch.sketchCurves.sketchCircles
    radius_cm = shared._mm_to_cm(MOUNT_HOLE_DIAMETER / 2.0)
    for x_from_left, y_from_top in HOLE_CENTERS_FROM_TOP_LEFT:
        centered_x = x_from_left - PLATE_LENGTH / 2.0
        centered_y = PLATE_WIDTH / 2.0 - y_from_top
        circles.addByCenterRadius(shared._point_mm(centered_x, centered_y), radius_cm)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        shared = _load_shared_helpers()

        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        output_dir = os.path.join(workspace_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits

        occurrence = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = FILE_STEM
        _add_user_parameters(design)

        sketch = component.sketches.add(component.xYConstructionPlane)
        sketch.name = "Cut_Profile_1to1_QTY1"
        sketch.isComputeDeferred = True
        shared._add_rounded_rectangle(sketch, PLATE_LENGTH, PLATE_WIDTH, CORNER_RADIUS)
        _add_holes(sketch, shared)
        sketch.isComputeDeferred = False
        adsk.doEvents()

        profile, profile_area_cm2 = shared._largest_profile(sketch)
        expected_profile_count = 1 + len(HOLE_CENTERS_FROM_TOP_LEFT)
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
        extrude.bodies.item(0).name = "ThirdPlate_QTY1"

        paths = shared._export_design(design, component, sketch, output_dir, app)
        sketch.isVisible = False

        report = {
            "script": SCRIPT_ID,
            "part_name": FILE_STEM,
            "quantity": 1,
            "units": "mm",
            "plate": {
                "length": PLATE_LENGTH,
                "width": PLATE_WIDTH,
                "thickness": PLATE_THICKNESS,
                "corner_radius": CORNER_RADIUS,
            },
            "openings": {
                "fan_count": 0,
                "access_hole_count": 0,
            },
            "mount_holes": {
                "diameter": MOUNT_HOLE_DIAMETER,
                "thread": "M3 clearance",
                "count": len(HOLE_CENTERS_FROM_TOP_LEFT),
                "centers_from_top_left": [list(center) for center in HOLE_CENTERS_FROM_TOP_LEFT],
            },
            "excluded_unmarked_holes": [[21.0, 46.0], [342.0, 46.0]],
            "fusion": {
                "profile_count": sketch.profiles.count,
                "solid_body_count": component.bRepBodies.count,
                "largest_profile_area_mm2": profile_area_cm2 * 100.0,
                "user_parameter_count": design.userParameters.count,
            },
            "files": paths,
            "note": "Third plate with only the six M3 holes marked in the user's annotated image.",
        }
        report_path = os.path.join(output_dir, FILE_STEM + "_report.json")
        with open(report_path, "w", encoding="utf-8") as report_file:
            json.dump(report, report_file, indent=2, ensure_ascii=False)

        ui.messageBox(
            "Third plate generated successfully.\n\n"
            f"Plate: {PLATE_LENGTH:.1f} x {PLATE_WIDTH:.1f} x {PLATE_THICKNESS:.1f} mm\n"
            f"M3 clearance holes: diameter {MOUNT_HOLE_DIAMETER:.1f} mm, 6 marked places\n"
            "Fan and access openings: none\n"
            f"Output: {output_dir}"
        )
    except:
        if ui:
            ui.messageBox("Third-plate generation failed:\n\n" + traceback.format_exc())


def stop(context):
    pass
