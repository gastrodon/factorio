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


class BurnerLineSegment(Blueprint):
    def __init__(self) -> None:
        super().__init__()
        self.label = "Burner Line Segment"
        self.description = "Single tileable burner drill segment with fuel and ore belts"

        # (direction, positions in flow order)
        self.belt_segments = [
            (0, [(0, 0), (0, 1)]),   # Left fuel input (North)
            (8, [(4, 0), (4, 1)]),   # Middle ore output (South)
            (8, [(8, 0), (8, 1)]),   # Right fuel passthrough (South)
        ]

        # (position, direction)
        self.drills = [
            ((3, 1), 4),   # East, outputs to middle belt
            ((6, 1), 12),  # West, outputs to middle belt
        ]

        # (position, direction)
        self.inserters = [
            ((1, 0), 12),  # West, feeds left drill
            ((7, 0), 4),   # East, feeds right drill
        ]

        self._place_belts()
        self._place_drills()
        self._place_inserters()

    def _place_belts(self) -> None:
        for direction, positions in self.belt_segments:
            for pos in positions:
                self.entities.append(TransportBelt("transport-belt", position=pos, direction=direction))

    def _place_drills(self) -> None:
        for pos, direction in self.drills:
            self.entities.append(MiningDrill("burner-mining-drill", position=pos, direction=direction))

    def _place_inserters(self) -> None:
        for pos, direction in self.inserters:
            self.entities.append(Inserter("burner-inserter", position=pos, direction=direction))


if __name__ == "__main__":
    print(BurnerLineSegment().to_string())
