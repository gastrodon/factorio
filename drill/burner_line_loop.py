#!/usr/bin/env python3
"""
Burner Line Loop - fuel return connector

Routes fuel exiting the top of the left belt (flowing North) eastward and
back down into the right belt (flowing South), closing the fuel circulation
loop for a burner-line-segment row.

Place directly above a burner-line-segment row: loop y=0 aligns with
segment y=-1. Shares the same x span (0 to 8).

Layout (normalized to origin):
  x=[0..7], y=0: Transport belts (East) — carry fuel right along the top
  x=8,      y=0: Transport belt (South) — drops fuel into right fuel column

INPUT:  (0, 0) receives from segment left belt at (0, 0) flowing North
OUTPUT: (8, 0) flowing South into segment right belt at (8, 0)
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.prototypes.transport_belt import TransportBelt


def create_blueprint() -> Blueprint:
    bp = Blueprint()
    bp.label = "Burner Line Loop"
    bp.description = "Fuel return loop connecting left North belt to right South belt"

    # East-flowing row across the top (x=0..7)
    for x in range(8):
        bp.entities.append(TransportBelt("transport-belt", position=(x, 0), direction=4))  # East

    # Turn South at the right edge to feed back down into x=8 fuel column
    bp.entities.append(TransportBelt("transport-belt", position=(8, 0), direction=8))  # South

    return bp


blueprint = create_blueprint()

if __name__ == "__main__":
    print(blueprint.to_string())
