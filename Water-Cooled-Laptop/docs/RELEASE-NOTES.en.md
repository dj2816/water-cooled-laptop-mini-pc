# REV10 Release Notes [English]

**Language / 语言: English | [中文](RELEASE-NOTES.md)**

- Model revision: REV10.
- Modeling completion date: 2026-09-01.
- Repository preparation date: 2026-09-07.
- Verification sources: `Acrylic_ThreePlates_363x244x3_REV10_2026-09-01.zip` and the final local exports.
- The original F3D, STEP, and DXF files for all three plates were retained. The models and hole positions were not changed during repository preparation.

## Latest change

Compared with the previous revision, SolidBackPlate adds a 5 × 5 mm top-edge notch whose right edge is 180 mm from the plate's right edge. RAMSidePlate and ThirdPlate retain their previously completed final exports.

All three plates are 363 × 244 × 3 mm, with R3 outer corners. They have eight, twelve, and six M3 clearance holes, respectively. Manufacture one of each plate.

## Public repository organization

- Files are organized under `images/`, `CAD/`, `electronics/`, and `docs/`.
- The six existing build photos and the original CAD previews for all three parts are retained.
- Fusion generator scripts and a theoretical geometry checking tool are included.
- The `files` fields in the parameter reports use paths relative to the repository root. Geometry data remains unchanged.
- Generator scripts match the original workspace copies. Running them from this repository writes exports to `CAD/output/`.
- Historical revisions, cache files, and local runtime outputs are excluded from the public directory.

Verification covered the existing files and recorded parameters. Fusion was not restarted to regenerate the models, and no new physical assembly or performance tests were performed.

## File verification

- The original REV10 archive contains 17 files and passed its integrity check. Every file's SHA-256 hash matches its corresponding final local export.
- All three DXF files use mm. Parsed circular opening counts, R3 outer corners, and the back-plate notch match the documentation.
- Each STEP file contains one solid. Its internal length unit is cm; the converted overall dimensions are 363 × 244 × 3 mm.
- The three generator scripts, three manifests, and geometry checking tool were copied from the originals. Python syntax checks and manifest JSON checks passed.
- The original F3D files are included. They were not reopened in Fusion during this verification.
