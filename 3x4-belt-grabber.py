#!/usr/bin/env python3
# ─── 3x4 Belt Grabber Layout ─────────────────────────────────────
# Generates a 3-wide, 4-tall layout with two rows of east-flowing
# belts and mirrored inserters pulling items off the belts.
#
# Layout (3 columns x 4 rows):
#
#      x=0  x=1  x=2
# y=0:  g    G    .     ← inserters (facing north, pick from y=1)
# y=1:  =    =    =     ← belts going east (→)
# y=2:  =    =    =     ← belts going east (→)
# y=3:  G    g    .     ← inserters (facing south, pick from y=2)
#
# Key: g = short inserter, G = long-handed inserter
#      = = transport-belt (east), . = empty
#
# Usage:
#   python3 3x4-belt-grabber.py                        # default blueprint
#   python3 3x4-belt-grabber.py --belt-type fast-transport-belt
#   python3 3x4-belt-grabber.py --short-inserter fast-inserter
#   python3 3x4-belt-grabber.py --facto                # print .facto source
# ──────────────────────────────────────────────────────────────────

import argparse
import subprocess
import sys


def generate_facto(
    belt_type: str = "transport-belt",
    short_inserter: str = "inserter",
    long_inserter: str = "long-handed-inserter",
) -> str:
    """Generate .facto source for the 3x4 belt grabber layout."""
    lines = [
        "# ─── 3x4 Belt Grabber Layout (generated) ──────────────────────",
        "",
        "# ─── Row 0: Inserters pulling from top belt row ──────────────────",
        f'Entity top_short = place("{short_inserter}", 0, 0, {{direction: 0}});',
        f'Entity top_long = place("{long_inserter}", 1, 0, {{direction: 0}});',
        "# x=2 y=0 is empty",
        "",
        "# ─── Row 1: Top belt row (east-flowing) ─────────────────────────",
    ]
    for x in range(3):
        lines.append(
            f'Entity belt_1_{x} = place("{belt_type}", {x}, 1, {{direction: 4}});'
        )
    lines += [
        "",
        "# ─── Row 2: Bottom belt row (east-flowing) ──────────────────────",
    ]
    for x in range(3):
        lines.append(
            f'Entity belt_2_{x} = place("{belt_type}", {x}, 2, {{direction: 4}});'
        )
    lines += [
        "",
        "# ─── Row 3: Inserters pulling from bottom belt row ──────────────",
        f'Entity bot_long = place("{long_inserter}", 0, 3, {{direction: 8}});',
        f'Entity bot_short = place("{short_inserter}", 1, 3, {{direction: 8}});',
        "# x=2 y=3 is empty",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a 3x4 belt grabber Factorio blueprint."
    )
    parser.add_argument(
        "--belt-type",
        default="transport-belt",
        help="Belt prototype name (default: transport-belt)",
    )
    parser.add_argument(
        "--short-inserter",
        default="inserter",
        help="Short inserter prototype name (default: inserter)",
    )
    parser.add_argument(
        "--long-inserter",
        default="long-handed-inserter",
        help="Long inserter prototype name (default: long-handed-inserter)",
    )
    parser.add_argument(
        "--facto",
        action="store_true",
        help="Print generated .facto source instead of compiling to blueprint",
    )
    args = parser.parse_args()

    source = generate_facto(
        belt_type=args.belt_type,
        short_inserter=args.short_inserter,
        long_inserter=args.long_inserter,
    )

    if args.facto:
        print(source)
    else:
        result = subprocess.run(
            ["factompile", "-i", source, "--name", "3x4-belt-grabber"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)
        print(result.stdout, end="")


if __name__ == "__main__":
    main()
