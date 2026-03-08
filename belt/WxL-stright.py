#!/usr/bin/env python3
# ─── NxM Belt Block ──────────────────────────────────────────────
# Generates a rectangular block of east-flowing transport belts:
# N lanes wide (rows) by M tiles long (columns).
#
# All belts face east (direction: 4).
#
# Layout examples:
#
#   --width 1 --length 1:   =
#
#   --width 2 --length 3:   ===
#                           ===
#
#   --width 5 --length 4:   ====
#                           ====
#                           ====
#                           ====
#                           ====
#
# Usage:
#   python3 NxM-belt.py                          # default 5×4 blueprint
#   python3 NxM-belt.py --width 8 --length 10    # 8-lane, 10-long bus
#   python3 NxM-belt.py --belt-type fast-transport-belt
#   python3 NxM-belt.py --width 3 --length 6 --facto   # print .facto source
# ──────────────────────────────────────────────────────────────────

import argparse
import subprocess
import sys


def generate_facto(
    width: int = 5,
    length: int = 4,
    belt_type: str = "transport-belt",
) -> str:
    """Generate .facto source for an NxM belt block."""
    lines = [
        f"# ─── {width}x{length} Belt Block (generated) ──────────────────────────",
        "",
    ]
    for row in range(width):
        lines.append(f"# ─── Row {row} ─────────────────────────────────────────────────")
        for col in range(length):
            lines.append(
                f'Entity belt_{row}_{col} = place("{belt_type}", {col}, {row}, {{direction: 4}});'
            )
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an NxM block of east-flowing Factorio transport belts."
    )
    parser.add_argument(
        "--width",
        type=int,
        default=5,
        help="Number of parallel lanes / rows (default: 5)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=4,
        help="Number of belt tiles per lane / columns (default: 4)",
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
        length=args.length,
        belt_type=args.belt_type,
    )

    if args.facto:
        print(source)
    else:
        result = subprocess.run(
            ["factompile", "-i", source, "--name", "NxM-belt"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)
        print(result.stdout, end="")


if __name__ == "__main__":
    main()
