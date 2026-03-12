#!/usr/bin/env python3
"""
Electric Mining Drill Segment

A 2x2 arrangement of electric mining drills with integrated belt system
for collecting ore. Drills face south and output onto a belt line that
runs east through the middle of the segment. Includes power connection.

Layout (normalized to origin):
  Drill  Drill        (facing down)
  Belt line (with underground segments)
 Drill  Drill         (facing up, shifted 1 tile left)
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.prototypes.mining_drill import MiningDrill
from draftsman.prototypes.transport_belt import TransportBelt
from draftsman.prototypes.underground_belt import UndergroundBelt
from draftsman.prototypes.electric_pole import ElectricPole


def create_blueprint() -> Blueprint:
    """Create and return the electric drill segment blueprint."""
    bp = Blueprint()
    bp.label = "Electric Drill Segment"
    bp.description = "2x2 electric drill mining segment with belt collection"

    # Top row of drills (facing south = direction 8)
    bp.entities.append(
        MiningDrill(
            "electric-mining-drill",
            position=(1, 0),
            direction=8,
        )
    )
    bp.entities.append(
        MiningDrill(
            "electric-mining-drill",
            position=(4, 0),
            direction=8,
        )
    )

    # Belt system (running east through the middle = direction 4)
    bp.entities.append(
        UndergroundBelt(
            "underground-belt",
            position=(0, 2),
            direction=4,
            io_type="output",
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(1, 2),
            direction=4,
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(2, 2),
            direction=4,
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(3, 2),
            direction=4,
        )
    )
    bp.entities.append(
        UndergroundBelt(
            "underground-belt",
            position=(4, 2),
            direction=4,
            io_type="input",
        )
    )

    # Power connection
    bp.entities.append(
        ElectricPole(
            "small-electric-pole",
            position=(5, 2),
        )
    )

    # Bottom row of drills (facing north = direction 0, outputting to belt above)
    bp.entities.append(
        MiningDrill(
            "electric-mining-drill",
            position=(0, 4),
            direction=0,
        )
    )
    bp.entities.append(
        MiningDrill(
            "electric-mining-drill",
            position=(3, 4),
            direction=0,
        )
    )

    return bp


if __name__ == "__main__":
    blueprint = create_blueprint()
    print(blueprint.to_string())
