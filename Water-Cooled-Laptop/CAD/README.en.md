# CAD Models and Generation Scripts [English]

**Language / 语言: English | [中文](README.md)**

This directory covers three 363 × 244 × 3 mm acrylic plates, each with R3 mm outer corners and a manufacturing quantity of one. All dimensions are in mm. The scripts retain their original directory names; `TopBottomPlateGenerator` actually generates only the RAM-side plate.

| Script directory | Generated part | Default holes and notch |
| --- | --- | --- |
| `FusionScripts/TopBottomPlateGenerator` | `RAMSidePlate` (RAM-side plate) | Two Ø55 ventilation holes, one Ø30 access hole, and eight Ø3.2 M3 clearance holes |
| `FusionScripts/SolidBackPlateGenerator` | `SolidBackPlate` (back plate) | Twelve Ø3.2 M3 clearance holes; a 5 × 5 notch in the top edge, with the notch's right edge 180 mm from the plate's right edge; no large ventilation holes |
| `FusionScripts/ThirdPlateGenerator` | `ThirdPlate` (third plate) | Only six Ø3.2 M3 clearance holes; no large holes or notch |

The third plate's hole centers use the finished plate's top-left corner as the origin, with positive coordinates extending rightward and downward: `(95, 6)`, `(256, 6)`, `(12, 238)`, `(125, 238)`, `(238, 238)`, and `(351, 238)`. It does not have the two holes at `(21, 46)` and `(342, 46)` that are present on the first two plates.

## Opening the Existing Models

In Autodesk Fusion, use “Open / Open from my computer” and select a released `.f3d` file in this directory. Alternatively, upload the F3D file through the Data Panel and open it there. The `.step` files are for exchanging solid models between CAD applications, and the `.dxf` files contain the 2D cutting profiles. After importing a file into manufacturing software, verify that the units are mm, the scale is 1:1, and the overall profile measures 363 × 244 mm.

## Regenerating Models from the Source Scripts

The scripts require the Python environment provided by Autodesk Fusion and the `adsk.core` and `adsk.fusion` APIs. All three `.manifest` files currently declare `supportedOS: windows`. The original files have been retained, and operation on macOS has not been verified. All other imports are from the Python standard library; no additional pip packages are required. These Fusion scripts cannot run directly in a regular Python interpreter.

1. Place the entire project in a writable local directory. Retain all three script directories under `CAD/FusionScripts`, including their respective `.py` and `.manifest` files, and keep the file and directory names unchanged.
2. In Fusion's “Scripts and Add-Ins” dialog, open the “Scripts” tab and use Add or `+` to select one of the script directories, such as `TopBottomPlateGenerator`. Select the directory, rather than just the `.py` file.
3. Select and run the corresponding script for the plate you need. The third-plate script automatically loads shared functions from the adjacent `SolidBackPlateGenerator/SolidBackPlateGenerator.py` file; you do not need to run the back-plate script first.
4. On success, the script creates a new design document and displays the generated result and output directory. Run each of the three plate scripts separately.

The third-plate script depends on the adjacent back-plate script, so its directory cannot be moved on its own. The scripts locate the output directory relative to their own location. With the repository structure preserved, files are written to `CAD/output/`, regardless of the working directory from which Fusion was launched. Write permission for this directory is required.

Each plate generates the following files, where `<part_name>` is `RAMSidePlate`, `SolidBackPlate`, or `ThirdPlate`, as listed in the table above:

- `<part_name>.f3d`: Fusion document.
- `<part_name>.step`: Solid-model exchange file.
- `<part_name>_QTY1_1to1.dxf`: Cutting sketch for one part at 1:1 scale.
- `<part_name>_preview.png`: Preview of the Fusion view.
- `<part_name>_report.json`: Parameters and information about the current export.

Rerunning a script overwrites the corresponding part's exported files with the same names in `CAD/output/`. To retain a customized version, first copy the output to a separate version directory. Manage the repository's existing released models separately from newly generated output.

## How Parameter Changes Actually Work

The main initial dimensions for the first two plates are in `DEFAULTS` near the top of their respective `.py` files. Each script checks the currently active design. It reads user parameters whose names match entries in `DEFAULTS` only if it finds a component named `RAMSidePlate` or `SolidBackPlate`, respectively; otherwise, it uses the defaults. It then rebuilds the model in a new document.

The current version has several fixed revision values. Even if you change them in Fusion's parameter table, rerunning the script restores them to the values in the source code's `DEFAULTS`:

- Common to both plates: `acrylicThickness`, `newTopHoleOffsetTop`, `newTopHole1OffsetLeft`, `newTopHole2OffsetRight`, `bottomMountOffsetLeft`, `bottomMountOffsetRight`, and `bottomMountOffsetBottom`.
- Additional values for the RAM-side plate: `accessHoleDiameter`, `accessHoleOffsetLeft`, and `accessHoleOffsetBottom`.
- Additional values for the back plate: `topNotchWidth`, `topNotchDepth`, and `topNotchRightEdgeOffsetRight`.

To change these fixed values, edit `DEFAULTS` in the source code and rerun the script. When changing other default values, you can start from a blank design to avoid reading parameters from an old model. `plateLength` and `plateWidth` are derived from the motherboard length and width, assembly clearance, and allowance for sidewall thickness; editing these two derived parameters directly does not make them inputs for the next run. The scripts draw the profiles using numerical values. Do not assume that editing any Fusion user parameter will automatically update all sketch hole positions. After making changes, rerun the script and inspect the new output.

The third plate uses the source constants `PLATE_LENGTH`, `PLATE_WIDTH`, `PLATE_THICKNESS`, `CORNER_RADIUS`, and `MOUNT_HOLE_DIAMETER`, together with the fixed list `HOLE_CENTERS_FROM_TOP_LEFT`. It does not read user parameters from the current design. Changing the plate dimensions does not automatically recalculate the six hole positions; you must also update the hole-center list. Check and update the hole-position reference values in the source function `_add_user_parameters` and the fixed descriptions in the report as needed to keep them consistent. Visible hole-position names in the parameter table do not mean that a complete set of linked parametric constraints has been established.

`cutQuantity` is used in the first two plates' parameters and reports. The scripts still generate a single solid, and the DXF filenames always use `QTY1`; multiple parts are not automatically nested. After changing the default thickness, some body names and messages still contain `3mm`. Verify the actual geometry and the numerical values in the report.

## Local Theoretical Geometry Checks

`tools/validate_geometry.py` uses Python 3.8 or later and the standard library, and can run independently of Fusion. Run the following from the repository root:

```shell
python CAD/tools/validate_geometry.py
```

The tool uses its own hard-coded dimensions and hole positions to calculate edge clearances, clearances between circular holes, and some clearances around the notch. It writes the following files to `CAD/output/`:

- `RAMSidePlate_local_preview.svg`
- `SolidBackPlate_local_preview.svg`
- `ThirdPlate_local_preview.svg`
- `RevisedPlates_local_validation.json`

The tool does not read, parse, or validate F3D, STEP, or DXF geometry, and it does not automatically read parameters from the three Fusion generation scripts. After changing the design, you must update its constants accordingly. The report fields `bounds_ok` and `no_circular_cutout_intersections` indicate only the results of the theoretical checks implemented by the tool. A normal process exit does not itself mean that the checks passed; inspect both values. The boundary check uses the enclosing rectangle. It is not a complete check of the rounded-corner boundary, solid topology, assembly interference, or manufacturability.
