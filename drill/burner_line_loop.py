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

from dataclasses import dataclass

from draftsman.classes.blueprint import Blueprint
from draftsman.prototypes.transport_belt import TransportBelt


@dataclass
class BurnerLineLoopParams:
    width: int = 8


class BurnerLineLoop(Blueprint):
    def __init__(self, params: BurnerLineLoopParams = BurnerLineLoopParams()) -> None:
        super().__init__()
        self.label = "Burner Line Loop"
        self.description = "Fuel return loop connecting left North belt to right South belt"

        # (direction, positions in flow order)
        self.belt_segments = [
            (4, [(0, 0)]),                                      # First bend
            *[(4, [(x, 0)]) for x in range(1, params.width)],   # East across top
            (8, [(params.width, 0)]),                            # South turn at end
        ]

        self._place_belts()

    def _place_belts(self) -> None:
        for direction, positions in self.belt_segments:
            for pos in positions:
                self.entities.append(TransportBelt("transport-belt", position=pos, direction=direction))


if __name__ == "__main__":
    print(BurnerLineLoop().to_string())
