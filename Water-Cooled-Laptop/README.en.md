# Water-Cooled-Laptop [English]

**Language / 语言: English | [中文](README.md)**

A water-cooled laptop project with an open-frame enclosure made from clear acrylic. This release includes build photos and the manufacturing files, native Fusion files, and generator scripts for the **three REV10 acrylic plates (2026-09-01)**.

![Completed build, front view](images/Final%20build%20front.jpg)

## Documentation languages

Every document has a Chinese and an English edition. Files ending in `.en.md` are the English editions; the original `.md` documents are labeled **中文**. Each page has a language switch at the top. CAD files, source code, photos, and JSON reports are shared by both editions.

| Document | 中文 | English |
| --- | --- | --- |
| Project overview | [中文](README.md) | [English](README.en.md) |
| CAD and generator guide | [中文](CAD/README.md) | [English](CAD/README.en.md) |
| Bill of materials | [中文](docs/BOM.md) | [English](docs/BOM.en.md) |
| Manufacturing instructions | [中文](docs/MANUFACTURING.md) | [English](docs/MANUFACTURING.en.md) |
| Build photos | [中文](docs/BUILD-PHOTOS.md) | [English](docs/BUILD-PHOTOS.en.md) |
| Release notes | [中文](docs/RELEASE-NOTES.md) | [English](docs/RELEASE-NOTES.en.md) |
| Outstanding information | [中文](docs/TODO.md) | [English](docs/TODO.en.md) |
| ESP32 control | [中文](electronics/ESP32-control/README.md) | [English](electronics/ESP32-control/README.en.md) |

## Current contents

| Item | Status |
| --- | --- |
| CAD for three acrylic plates | DXF, STEP, and F3D for each plate; manufacture one of each |
| Model generator source | Three Fusion Python scripts and a geometry checking tool |
| Build photos | Six existing photos, plus three CAD previews |
| Bill of materials | Three plates confirmed; other component specifications still needed |
| ESP32 control | Placeholder directory; its use and related information remain unconfirmed |
| Complete assembly model and PDF engineering drawings | Not yet provided |
| Temperature, power, and noise measurements | Not yet provided |
| Open-source license | Awaiting the project owner's selection; no LICENSE file has been added |

The physical build photos document the construction process. Their hole patterns have not been checked point by point against REV10.

## Repository structure

```text
Water-Cooled-Laptop/
├── README.md                   # 中文
├── README.en.md                # English
├── .gitignore
├── .gitattributes
├── images/                     # Build photos and three CAD previews
├── CAD/
│   ├── README.md / README.en.md
│   ├── RAMSidePlate.*          # Fan-opening plate; also QTY1_1to1.dxf
│   ├── SolidBackPlate.*        # Back plate with a 5 × 5 mm top-edge notch
│   ├── ThirdPlate.*            # Third plate with only six M3 clearance holes
│   ├── FusionScripts/          # Three model generator scripts
│   └── tools/                  # Theoretical geometry checks
├── electronics/
│   └── ESP32-control/
│       └── README.md / README.en.md
└── docs/
    ├── BOM.md / BOM.en.md
    ├── MANUFACTURING.md / MANUFACTURING.en.md
    ├── BUILD-PHOTOS.md / BUILD-PHOTOS.en.md
    ├── RELEASE-NOTES.md / RELEASE-NOTES.en.md
    ├── TODO.md / TODO.en.md
    └── reports/                # Parameter reports and geometry check results
```

Original part names are retained so they match the manufacturing files. A complete `enclosure.step` assembly has not been provided; none of the individual plate files represents the complete assembly.

## Download and manufacture

All three plates are clear acrylic, **363 × 244 mm**, **3 mm thick**, with **R3 mm outer corners**. The clearance holes are **3.2 mm in diameter**, for M3 fasteners.

| Part (one of each) | Laser-cutting DXF (mm, 1:1) | 3D STEP | Native Fusion file |
| --- | --- | --- | --- |
| RAMSidePlate | [DXF](CAD/RAMSidePlate_QTY1_1to1.dxf) | [STEP](CAD/RAMSidePlate.step) | [F3D](CAD/RAMSidePlate.f3d) |
| SolidBackPlate | [DXF](CAD/SolidBackPlate_QTY1_1to1.dxf) | [STEP](CAD/SolidBackPlate.step) | [F3D](CAD/SolidBackPlate.f3d) |
| ThirdPlate | [DXF](CAD/ThirdPlate_QTY1_1to1.dxf) | [STEP](CAD/ThirdPlate.step) | [F3D](CAD/ThirdPlate.f3d) |

- RAMSidePlate: two Ø55 mm fan openings, one Ø30 mm access opening, and eight M3 clearance holes.
- SolidBackPlate: twelve M3 clearance holes and a 5 × 5 mm notch cut downward from the top edge. The notch's right edge is 180 mm from the plate's right edge.
- ThirdPlate: six M3 clearance holes, with no fan or access openings.

Read the [manufacturing instructions](docs/MANUFACTURING.en.md) before fabrication. Import DXF files in **mm at 1:1 scale**; do not take dimensions from photos or preview images. The hole patterns were designed for this project. The exact laptop model and assembly spacing still need to be documented, so compatibility with other models has not been established.

## Modeling and build records

- [Open and regenerate the models](CAD/README.en.md)
- [Bill of materials](docs/BOM.en.md)
- [Build photos](docs/BUILD-PHOTOS.en.md)
- [REV10 release notes](docs/RELEASE-NOTES.en.md)
- [Outstanding information](docs/TODO.en.md)

### CAD previews

| RAMSidePlate | SolidBackPlate | ThirdPlate |
| --- | --- | --- |
| ![RAM-side plate CAD preview](images/ram-side-plate-cad.png) | ![Back plate CAD preview](images/solid-back-plate-cad.png) | ![Third plate CAD preview](images/third-plate-cad.png) |

## License

A license has not yet been selected. No licensing terms have been added on behalf of the project owner during this preparation. Before publication, confirm the licensing scope for the CAD files, code, documentation, and photos, and add the official LICENSE file.
