import json
import math
import os


PLATE_LENGTH = 363.0
PLATE_WIDTH = 244.0
PLATE_THICKNESS = 3.0
CORNER_RADIUS = 3.0
VENT_DIAMETER = 55.0
VENT_CENTERS = ((52.0, 75.0), (311.0, 75.0))
MOUNT_HOLE_DIAMETER = 3.2
ACCESS_HOLE_DIAMETER = 30.0
ACCESS_HOLE_CENTER = (22.0, 214.0)
BOTH_PLATES_MOUNT_HOLE_CENTERS = (
    (95.0, 6.0),
    (256.0, 6.0),
    (21.0, 46.0),
    (342.0, 46.0),
    (12.0, 238.0),
    (125.0, 238.0),
    (238.0, 238.0),
    (351.0, 238.0),
)
BACK_ADDITIONAL_HOLE_CENTERS_FROM_BOTTOM_LEFT = (
    (36.0, 4.0),
    (47.0, 11.0),
    (46.0, 19.0),
    (22.0, 46.0),
)
BACK_ADDITIONAL_HOLE_CENTERS = tuple(
    (x, PLATE_WIDTH - y) for x, y in BACK_ADDITIONAL_HOLE_CENTERS_FROM_BOTTOM_LEFT
)
BACK_TOP_NOTCH_WIDTH = 5.0
BACK_TOP_NOTCH_DEPTH = 5.0
BACK_TOP_NOTCH_RIGHT_EDGE_FROM_RIGHT = 180.0
BACK_TOP_NOTCH_RIGHT_EDGE_FROM_LEFT = PLATE_LENGTH - BACK_TOP_NOTCH_RIGHT_EDGE_FROM_RIGHT
BACK_TOP_NOTCH_LEFT_EDGE_FROM_LEFT = BACK_TOP_NOTCH_RIGHT_EDGE_FROM_LEFT - BACK_TOP_NOTCH_WIDTH
THIRD_PLATE_MOUNT_HOLE_CENTERS = (
    (95.0, 6.0),
    (256.0, 6.0),
    (12.0, 238.0),
    (125.0, 238.0),
    (238.0, 238.0),
    (351.0, 238.0),
)
THIRD_PLATE_EXCLUDED_UNMARKED_HOLES = ((21.0, 46.0), (342.0, 46.0))
REMOVED_MOUNT_HOLE_CENTERS = ((12.0, 186.0), (351.0, 186.0))


def edge_clearance(center, diameter):
    radius = diameter / 2.0
    x, y = center
    return min(x - radius, PLATE_LENGTH - x - radius, y - radius, PLATE_WIDTH - y - radius)


def circular_clearance(first_center, first_diameter, second_center, second_diameter):
    return math.dist(first_center, second_center) - first_diameter / 2.0 - second_diameter / 2.0


def circle_to_rectangle_clearance(center, diameter, left, top, right, bottom):
    x, y = center
    dx = max(left - x, 0.0, x - right)
    dy = max(top - y, 0.0, y - bottom)
    return math.hypot(dx, dy) - diameter / 2.0


def build_svg(include_front_cutouts):
    circles = []
    if include_front_cutouts:
        circles.extend(
            f'<circle cx="{x}" cy="{y}" r="{VENT_DIAMETER / 2.0}"/>'
            for x, y in VENT_CENTERS
        )
        circles.append(
            f'<circle cx="{ACCESS_HOLE_CENTER[0]}" cy="{ACCESS_HOLE_CENTER[1]}" r="{ACCESS_HOLE_DIAMETER / 2.0}"/>'
        )
    circles.extend(
        f'<circle cx="{x}" cy="{y}" r="{MOUNT_HOLE_DIAMETER / 2.0}"/>'
        for x, y in BOTH_PLATES_MOUNT_HOLE_CENTERS
    )
    if not include_front_cutouts:
        circles.extend(
            f'<circle cx="{x}" cy="{y}" r="{MOUNT_HOLE_DIAMETER / 2.0}"/>'
            for x, y in BACK_ADDITIONAL_HOLE_CENTERS
        )
    if include_front_cutouts:
        outline = f'<rect width="{PLATE_LENGTH}" height="{PLATE_WIDTH}" rx="{CORNER_RADIUS}" fill="#d9eef4" stroke="#276276" stroke-width="0.7"/>'
    else:
        outline = (
            f'<path d="M {CORNER_RADIUS},0 H {BACK_TOP_NOTCH_LEFT_EDGE_FROM_LEFT} '
            f'V {BACK_TOP_NOTCH_DEPTH} H {BACK_TOP_NOTCH_RIGHT_EDGE_FROM_LEFT} V 0 '
            f'H {PLATE_LENGTH - CORNER_RADIUS} A {CORNER_RADIUS},{CORNER_RADIUS} 0 0 1 {PLATE_LENGTH},{CORNER_RADIUS} '
            f'V {PLATE_WIDTH - CORNER_RADIUS} A {CORNER_RADIUS},{CORNER_RADIUS} 0 0 1 {PLATE_LENGTH - CORNER_RADIUS},{PLATE_WIDTH} '
            f'H {CORNER_RADIUS} A {CORNER_RADIUS},{CORNER_RADIUS} 0 0 1 0,{PLATE_WIDTH - CORNER_RADIUS} '
            f'V {CORNER_RADIUS} A {CORNER_RADIUS},{CORNER_RADIUS} 0 0 1 {CORNER_RADIUS},0 Z" '
            'fill="#d9eef4" stroke="#276276" stroke-width="0.7"/>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="807" viewBox="0 0 {PLATE_LENGTH} {PLATE_WIDTH}">
  {outline}
  <g fill="#ffffff" stroke="#276276" stroke-width="0.35">{' '.join(circles)}</g>
</svg>'''


def build_third_plate_svg():
    circles = " ".join(
        f'<circle cx="{x}" cy="{y}" r="{MOUNT_HOLE_DIAMETER / 2.0}"/>'
        for x, y in THIRD_PLATE_MOUNT_HOLE_CENTERS
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="807" viewBox="0 0 {PLATE_LENGTH} {PLATE_WIDTH}">
  <rect width="{PLATE_LENGTH}" height="{PLATE_WIDTH}" rx="{CORNER_RADIUS}" fill="#d9eef4" stroke="#276276" stroke-width="0.7"/>
  <g fill="#ffffff" stroke="#276276" stroke-width="0.35">{circles}</g>
</svg>'''


def main():
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output = os.path.join(workspace, "output")
    os.makedirs(output, exist_ok=True)

    with open(os.path.join(output, "RAMSidePlate_local_preview.svg"), "w", encoding="ascii") as stream:
        stream.write(build_svg(True))
    with open(os.path.join(output, "SolidBackPlate_local_preview.svg"), "w", encoding="ascii") as stream:
        stream.write(build_svg(False))
    with open(os.path.join(output, "ThirdPlate_local_preview.svg"), "w", encoding="ascii") as stream:
        stream.write(build_third_plate_svg())

    mount_edge_clearances = [
        edge_clearance(center, MOUNT_HOLE_DIAMETER) for center in BOTH_PLATES_MOUNT_HOLE_CENTERS
    ]
    mount_pair_clearances = [
        circular_clearance(first, MOUNT_HOLE_DIAMETER, second, MOUNT_HOLE_DIAMETER)
        for index, first in enumerate(BOTH_PLATES_MOUNT_HOLE_CENTERS)
        for second in BOTH_PLATES_MOUNT_HOLE_CENTERS[index + 1 :]
    ]
    mount_to_vent_clearances = [
        circular_clearance(mount, MOUNT_HOLE_DIAMETER, vent, VENT_DIAMETER)
        for mount in BOTH_PLATES_MOUNT_HOLE_CENTERS
        for vent in VENT_CENTERS
    ]
    mount_to_access_clearances = [
        circular_clearance(mount, MOUNT_HOLE_DIAMETER, ACCESS_HOLE_CENTER, ACCESS_HOLE_DIAMETER)
        for mount in BOTH_PLATES_MOUNT_HOLE_CENTERS
    ]
    additional_to_existing_clearances = [
        circular_clearance(
            additional,
            MOUNT_HOLE_DIAMETER,
            (existing[0], PLATE_WIDTH - existing[1]),
            MOUNT_HOLE_DIAMETER,
        )
        for additional in BACK_ADDITIONAL_HOLE_CENTERS_FROM_BOTTOM_LEFT
        for existing in BOTH_PLATES_MOUNT_HOLE_CENTERS
    ]
    additional_pair_clearances = [
        circular_clearance(first, MOUNT_HOLE_DIAMETER, second, MOUNT_HOLE_DIAMETER)
        for index, first in enumerate(BACK_ADDITIONAL_HOLE_CENTERS_FROM_BOTTOM_LEFT)
        for second in BACK_ADDITIONAL_HOLE_CENTERS_FROM_BOTTOM_LEFT[index + 1 :]
    ]
    back_hole_centers = BOTH_PLATES_MOUNT_HOLE_CENTERS + BACK_ADDITIONAL_HOLE_CENTERS
    back_notch_to_hole_clearances = [
        circle_to_rectangle_clearance(
            center,
            MOUNT_HOLE_DIAMETER,
            BACK_TOP_NOTCH_LEFT_EDGE_FROM_LEFT,
            0.0,
            BACK_TOP_NOTCH_RIGHT_EDGE_FROM_LEFT,
            BACK_TOP_NOTCH_DEPTH,
        )
        for center in back_hole_centers
    ]
    vent_to_access_clearances = [
        circular_clearance(vent, VENT_DIAMETER, ACCESS_HOLE_CENTER, ACCESS_HOLE_DIAMETER)
        for vent in VENT_CENTERS
    ]
    third_plate_edge_clearances = [
        edge_clearance(center, MOUNT_HOLE_DIAMETER)
        for center in THIRD_PLATE_MOUNT_HOLE_CENTERS
    ]
    third_plate_pair_clearances = [
        circular_clearance(first, MOUNT_HOLE_DIAMETER, second, MOUNT_HOLE_DIAMETER)
        for index, first in enumerate(THIRD_PLATE_MOUNT_HOLE_CENTERS)
        for second in THIRD_PLATE_MOUNT_HOLE_CENTERS[index + 1 :]
    ]

    report = {
        "plate_mm": [PLATE_LENGTH, PLATE_WIDTH, PLATE_THICKNESS],
        "corner_radius_mm": CORNER_RADIUS,
        "front_plate": {
            "vent_centers_from_top_left_mm": [list(center) for center in VENT_CENTERS],
            "vent_diameter_mm": VENT_DIAMETER,
            "vent_opening_type": "fully open circles",
            "access_hole": {
                "diameter_mm": ACCESS_HOLE_DIAMETER,
                "radius_mm": ACCESS_HOLE_DIAMETER / 2.0,
                "center_from_top_left_mm": list(ACCESS_HOLE_CENTER),
                "center_from_bottom_left_mm": [ACCESS_HOLE_CENTER[0], PLATE_WIDTH - ACCESS_HOLE_CENTER[1]],
            },
            "mount_hole_centers_from_top_left_mm": [
                list(center) for center in BOTH_PLATES_MOUNT_HOLE_CENTERS
            ],
        },
        "back_plate": {
            "vent_count": 0,
            "power_hole_count": 0,
            "top_edge_notch": {
                "width_mm": BACK_TOP_NOTCH_WIDTH,
                "depth_mm": BACK_TOP_NOTCH_DEPTH,
                "right_edge_from_right_mm": BACK_TOP_NOTCH_RIGHT_EDGE_FROM_RIGHT,
                "left_edge_from_left_mm": BACK_TOP_NOTCH_LEFT_EDGE_FROM_LEFT,
                "right_edge_from_left_mm": BACK_TOP_NOTCH_RIGHT_EDGE_FROM_LEFT,
                "minimum_hole_clearance_mm": min(back_notch_to_hole_clearances),
            },
            "mount_hole_centers_from_top_left_mm": [
                list(center) for center in BOTH_PLATES_MOUNT_HOLE_CENTERS
            ],
            "mount_hole_centers_from_bottom_left_mm": [
                [x, PLATE_WIDTH - y] for x, y in BOTH_PLATES_MOUNT_HOLE_CENTERS
            ],
            "additional_m3_hole_centers_from_bottom_left_mm": [
                list(center) for center in BACK_ADDITIONAL_HOLE_CENTERS_FROM_BOTTOM_LEFT
            ],
        },
        "third_plate": {
            "vent_count": 0,
            "access_hole_count": 0,
            "mount_hole_centers_from_top_left_mm": [
                list(center) for center in THIRD_PLATE_MOUNT_HOLE_CENTERS
            ],
            "excluded_unmarked_hole_centers_from_top_left_mm": [
                list(center) for center in THIRD_PLATE_EXCLUDED_UNMARKED_HOLES
            ],
            "minimum_edge_clearance_mm": min(third_plate_edge_clearances),
            "minimum_pair_clearance_mm": min(third_plate_pair_clearances),
        },
        "mount_hole_diameter_mm": MOUNT_HOLE_DIAMETER,
        "removed_old_bottom_mounts_mm": [list(center) for center in REMOVED_MOUNT_HOLE_CENTERS],
        "minimum_mount_edge_clearance_mm": min(mount_edge_clearances),
        "minimum_mount_pair_clearance_mm": min(mount_pair_clearances),
        "minimum_front_mount_to_vent_clearance_mm": min(mount_to_vent_clearances),
        "minimum_front_mount_to_access_clearance_mm": min(mount_to_access_clearances),
        "minimum_front_vent_to_access_clearance_mm": min(vent_to_access_clearances),
        "minimum_back_additional_to_existing_clearance_mm": min(additional_to_existing_clearances),
        "minimum_back_additional_pair_clearance_mm": min(additional_pair_clearances),
        "bounds_ok": min(mount_edge_clearances) >= 0
        and all(edge_clearance(center, VENT_DIAMETER) >= 0 for center in VENT_CENTERS)
        and edge_clearance(ACCESS_HOLE_CENTER, ACCESS_HOLE_DIAMETER) >= 0
        and all(edge_clearance(center, MOUNT_HOLE_DIAMETER) >= 0 for center in BOTH_PLATES_MOUNT_HOLE_CENTERS)
        and 0 <= BACK_TOP_NOTCH_LEFT_EDGE_FROM_LEFT < BACK_TOP_NOTCH_RIGHT_EDGE_FROM_LEFT <= PLATE_LENGTH
        and 0 < BACK_TOP_NOTCH_DEPTH < PLATE_WIDTH
        and min(third_plate_edge_clearances) >= 0,
        "no_circular_cutout_intersections": min(
            mount_pair_clearances
            + mount_to_vent_clearances
            + mount_to_access_clearances
            + vent_to_access_clearances
            + additional_to_existing_clearances
            + additional_pair_clearances
            + back_notch_to_hole_clearances
            + third_plate_pair_clearances
        ) >= 0,
    }
    report_path = os.path.join(output, "RevisedPlates_local_validation.json")
    with open(report_path, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
