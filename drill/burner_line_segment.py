#!/usr/bin/env python3
"""
Burner Line Segment - single tileable unit

Two burner mining drills facing each other with interlaced fuel belts.
Tile horizontally by stacking at X+8 offsets.

Layout (normalized to origin):
  x=0, y=[0,1]: Fuel input belts (South)
  x=1, y=0:     Burner inserter facing West (feeds drill 1)
  x=2, y=0:     Burner mining drill facing East (outputs to x=4)
  x=4, y=[0,1]: Middle ore belts (South) — ore output
  x=5, y=0:     Burner mining drill facing West (outputs to x=4)
  x=7, y=0:     Burner inserter facing East (feeds drill 2)
  x=8, y=[0,1]: Fuel passthrough belts (South)

INPUT:  Fuel belts at (0, 0) and (0, 1), flowing South
OUTPUT: Ore belts at (4, 0) and (4, 1), flowing South
        Fuel passthrough at (8, 0) and (8, 1), flowing South
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.prototypes.mining_drill import MiningDrill
from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.transport_belt import TransportBelt


def create_blueprint() -> Blueprint:
    bp = Blueprint()
    bp.label = "Burner Line Segment"
    bp.description = "Single tileable burner drill segment with fuel and ore belts"

    # Left fuel input belts (flowing South)
    bp.entities.append(TransportBelt("transport-belt", position=(0, 0), direction=0))  # North
    bp.entities.append(TransportBelt("transport-belt", position=(0, 1), direction=0))  # North

    # First burner inserter (feeds drill 1 from left fuel belt)
    bp.entities.append(Inserter("burner-inserter", position=(1, 0), direction=12))  # West

    # First drill (facing East, outputs ore to middle belt at x=4)
    bp.entities.append(MiningDrill("burner-mining-drill", position=(3, 1), direction=4))  # East

    # Middle ore belts (flowing South)
    bp.entities.append(TransportBelt("transport-belt", position=(4, 0), direction=8))  # South
    bp.entities.append(TransportBelt("transport-belt", position=(4, 1), direction=8))  # South

    # Second drill (facing West, outputs ore to middle belt at x=4)
    bp.entities.append(MiningDrill("burner-mining-drill", position=(6, 1), direction=12))  # West

    # Second burner inserter (feeds drill 2 from right fuel belt)
    bp.entities.append(Inserter("burner-inserter", position=(7, 0), direction=4))  # East

    # Right fuel passthrough belts (flowing South)
    bp.entities.append(TransportBelt("transport-belt", position=(8, 0), direction=8))  # South
    bp.entities.append(TransportBelt("transport-belt", position=(8, 1), direction=8))  # South

    return bp


blueprint = create_blueprint()

if __name__ == "__main__":
    print(blueprint.to_string())
