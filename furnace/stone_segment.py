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


class StoneFurnaceSegment(Blueprint):
    def __init__(self) -> None:
        super().__init__()
        self.label = "Stone Furnace Segment"
        self.description = "Single tileable stone furnace segment with belt I/O"

        # (position,)
        self.furnaces = [
            ((-3, 0),),
        ]

        # (name, position, direction)
        self.inserters = [
            ("long-handed-inserter", (-1.5, 0.5), 12),  # West, feeds furnace
            ("inserter", (-1.5, -0.5), 4),               # East, pulls output
        ]

        # (direction, positions in flow order)
        self.belt_segments = [
            (8, [(-0.5, -0.5)]),  # South
            (8, [(-0.5, 0.5)]),   # South
            (8, [(0.5, -0.5)]),   # South
            (8, [(0.5, 0.5)]),    # South
        ]

        self._place_furnaces()
        self._place_inserters()
        self._place_belts()

    def _place_furnaces(self) -> None:
        for (pos,) in self.furnaces:
            self.entities.append(Furnace("stone-furnace", position=pos))

    def _place_inserters(self) -> None:
        for name, pos, direction in self.inserters:
            self.entities.append(Inserter(name, position=pos, direction=direction))

    def _place_belts(self) -> None:
        for direction, positions in self.belt_segments:
            for pos in positions:
                self.entities.append(TransportBelt("transport-belt", position=pos, direction=direction))


if __name__ == "__main__":
    print(StoneFurnaceSegment().to_string())
