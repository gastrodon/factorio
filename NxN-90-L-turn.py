#!/usr/bin/env python3
# ─── NxN 90° Left Turn ──────────────────────────────────────────
# Generates a width×width block of transport belts forming a smooth
# 90-degree left turn.
#
# Input belts flow east (→), output belts flow north (↑).
# The turn cascades from the outermost lane inward:
#
#   --width 1:  ^       --width 2:  ^^      --width 3:  ^^^
#                                   =^                  =^^
#                                                       ==^
#
#   --width 4:  ^^^^    --width 5:  ^^^^^
#               =^^^                =^^^^
#               ==^^                ==^^^
#               ===^                ===^^
#                                   ====^
#
# Algorithm: For each row y (0..width), the belt at column x faces:
#   - East  (dir=4) if x < y            (straight segment)
#   - North (dir=0) if x >= y           (turned segment)
#
# Usage:
#   python3 NxN-90-L-turn.py                        # default width=3 blueprint
#   python3 NxN-90-L-turn.py --width 5              # 5-lane left turn
#   python3 NxN-90-L-turn.py --belt-type fast-transport-belt
#   python3 NxN-90-L-turn.py --width 4 --facto      # print .facto source
# ──────────────────────────────────────────────────────────────────

import argparse
import subprocess
import sys


def generate_facto(
    width: int = 3,
    belt_type: str = "transport-belt",
) -> str:
    """Generate .facto source for an NxN 90° left turn."""
    lines = [
        f"# ─── {width}x{width} 90° Left Turn (generated) ──────────────────────",
        "",
    ]
    for y in range(width):
        lines.append(f"# ─── Row {y} ─────────────────────────────────────────────────")
        # East-facing belts: columns 0 to (y - 1)
        for x in range(y):
            lines.append(
                f'Entity belt_{y}_{x} = place("{belt_type}", {x}, {y}, {{direction: 4}});'
            )
        # North-facing belts: columns y to (width - 1)
        for x in range(y, width):
            lines.append(
                f'Entity belt_{y}_{x} = place("{belt_type}", {x}, {y}, {{direction: 0}});'
            )
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an NxN 90° left turn of Factorio transport belts (east→north)."
    )
    parser.add_argument(
        "--width",
        type=int,
        default=3,
        help="Number of lanes / side length of the turn square (default: 3)",
    )
    parser.add_argument(
        "--belt-type",
        default="transport-belt",
        help="Belt prototype name (default: transport-belt)",
    )
    parser.add_argument(
        "--facto",
        action="store_true",
        help="Print generated .facto source instead of compiling to blueprint",
    )
    args = parser.parse_args()

    source = generate_facto(
        width=args.width,
        belt_type=args.belt_type,
    )

    if args.facto:
        print(source)
    else:
        result = subprocess.run(
            ["factompile", "-i", source, "--name", "NxN-90-L-turn"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)
        print(result.stdout, end="")


if __name__ == "__main__":
    main()
