# REV10 Acrylic Plate Fabrication Instructions [English]

**Language / 语言: English | [中文](MANUFACTURING.md)**

Version date: 2026-09-01. Material: clear acrylic. Thickness: 3 mm. Fabricate 1 of each of the three different plates.

## Common Specifications

- Overall dimensions: 363 × 244 mm.
- Four outer corners: R3 mm.
- M3 through-holes: Ø3.2 mm.
- DXF units: mm. Scale: 1:1. Do not rescale.
- Use `CAD/*_QTY1_1to1.dxf` as the preferred cutting files; use STEP files for 3D verification.
- Cutting compensation, manufacturing tolerances, and surface finish have not yet been specified and must be confirmed for the fabrication equipment being used.

Unless otherwise specified, hole coordinates below are given as “distance from the left edge, distance from the top edge,” in mm. The DXF files use the center of the plate as their origin; coordinate conversion gives the same hole positions as the tables below.

## RAMSidePlate — Plate with Fan Openings

- Quantity: 1.
- Two complete Ø55 mm circular cutouts, with no grille or ribs left in place.
- Fan opening centers: (52, 75), (311, 75).
- Ø30 mm access hole center: (22, 214), which is 22 mm from the left edge and 30 mm from the bottom edge.
- 8 Ø3.2 mm through-holes:

| X (from Left) | Y (from Top) |
| ---: | ---: |
| 95 | 6 |
| 256 | 6 |
| 21 | 46 |
| 342 | 46 |
| 12 | 238 |
| 125 | 238 |
| 238 | 238 |
| 351 | 238 |

## SolidBackPlate — Back Plate

- Quantity: 1. No fan openings or access hole.
- Includes the same 8 through-holes as RAMSidePlate, plus the 4 additional through-holes in the table below, for a total of 12.
- A rectangular notch extends down from the top edge, 5 mm wide and 5 mm deep, through the full 3 mm plate thickness.
- The **right edge** of the notch is 180 mm from the right edge of the plate. Measured from the left edge, the notch spans x = 178–183 mm and extends 0–5 mm from the top edge.

| X (from Left) | Y (from Top) | Corresponding Distance from Bottom |
| ---: | ---: | ---: |
| 36 | 240 | 4 |
| 47 | 233 | 11 |
| 46 | 225 | 19 |
| 22 | 198 | 46 |

## ThirdPlate — Third Plate

- Quantity: 1. No fan openings, access hole, or top-edge notch.
- Only 6 Ø3.2 mm through-holes: (95, 6), (256, 6), (12, 238), (125, 238), (238, 238), (351, 238).
- Does not include the holes at (21, 46) and (342, 46) found on the other two plates, or the four additional holes in the back plate.

## Version and Verification

This directory provides only the finished REV10 design. The historical 4 mm version, the shared plate for two parts, and REV1–REV9 archives are not included in this release.

The [parameter report](reports/RAMSidePlate_report.json), [back plate report](reports/SolidBackPlate_report.json), and [third plate report](reports/ThirdPlate_report.json) record the dimensions and solid counts exported from the model. The [theoretical geometry validation results](reports/RevisedPlates_local_validation.json) are used to check the specified hole spacing; they do not replace physical assembly or load testing.
