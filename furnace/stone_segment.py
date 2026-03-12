#!/usr/bin/env python3
"""
Stone Furnace Segment - single tileable unit

A stone furnace fed by a long-handed inserter from the right belt, with a
regular inserter pulling output back to the right belt. Belt runs vertically
(south) on the right side. Tile vertically by stacking at Y+2 offsets.

Layout (normalized to origin, y_center = 0):
  x=-3:   Stone furnace (2x2)
  x=-1.5, y=-0.5: Regular inserter facing East (pulls from furnace to belt)
  x=-1.5, y=+0.5: Long-handed inserter facing West (feeds furnace from belt)
  x=-0.5, y=-0.5: Transport belt (South)
  x=-0.5, y=+0.5: Transport belt (South)
  x=+0.5, y=-0.5: Transport belt (South)
  x=+0.5, y=+0.5: Transport belt (South)
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.prototypes.furnace import Furnace
from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.transport_belt import TransportBelt


def create_blueprint() -> Blueprint:
    """Create and return the stone furnace segment blueprint."""
    bp = Blueprint()
    bp.label = "Stone Furnace Segment"
    bp.description = "Single tileable stone furnace segment with belt I/O"

    bp.entities.append(
        Furnace("stone-furnace", position=(-3, 0))
    )

    # Long-handed inserter feeds furnace from right belt (facing West = 12)
    bp.entities.append(
        Inserter("long-handed-inserter", position=(-1.5, 0.5), direction=12)
    )

    # Regular inserter pulls output from furnace to belt (facing East = 4)
    bp.entities.append(
        Inserter("inserter", position=(-1.5, -0.5), direction=4)
    )

    # Belt column at x=-0.5 (flowing South = direction 8)
    bp.entities.append(
        TransportBelt("transport-belt", position=(-0.5, -0.5), direction=8)
    )
    bp.entities.append(
        TransportBelt("transport-belt", position=(-0.5, 0.5), direction=8)
    )

    # Belt column at x=0.5 (flowing South = direction 8)
    bp.entities.append(
        TransportBelt("transport-belt", position=(0.5, -0.5), direction=8)
    )
    bp.entities.append(
        TransportBelt("transport-belt", position=(0.5, 0.5), direction=8)
    )

    return bp


if __name__ == "__main__":
    blueprint = create_blueprint()
    print(blueprint.to_string())
