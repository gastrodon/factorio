#!/usr/bin/env python3
"""
Burner Line Cap - Single Tileable Ore Collection Unit

One cap structure with splitters for ore collection and routing. Designed to
sit below burner-line-segment units to collect mined ore and route it
horizontally. This is a single tileable unit for building larger collection
systems.

DIMENSIONS:
- Width: 8 tiles (x: 0 to 8)
- Height: 2 tiles (y: 0 to 1)

TILING DIRECTION:
- Horizontal (X-axis, East/West)
- Stack multiple instances by incrementing X by 8 tiles per instance
- Align horizontally with burner-line-segment instances above

INPUTS:
- Top ore belts at x=4, y=[0,1] from segments above (flowing SOUTH into cap)
  * Place this cap 2+ tiles South of burner-line-segment instances
  * Ore from segment middle belts flows down into this cap
- Left fuel passthrough at x=0, y=[0,1]
  * Continues fuel flow from segments above for multi-row configurations

OUTPUTS:
- Right output belts at x=[7-8], y=[0,1] - flowing EAST (direction 4)
  * Collected ore flows horizontally to the right
  * Chain multiple cap instances to merge ore from entire line
- Right fuel passthrough at x=8, y=[0,1]
  * Can feed into next tiled cap instance

FLOW PATTERN:
The cap uses splitters and underground belts to:
1. Accept ore from above (middle belts from segments)
2. Route ore horizontally using splitter pair
3. Merge ore into right-flowing output belts
4. Pass through fuel belts for potential multi-row setups

LAYOUT:
x=0: Left input belts (fuel passthrough from segments)
x=1: Pre-splitter belt connection
x=2: Underground belt inputs
x=3-4: Left splitter (splits ore flow)
x=4: Middle belts receiving ore from segments above
x=5: Underground belt outputs
x=6-7: Right splitter (merges ore flow)
x=7-8: Right output belts (ore flowing East)

USAGE IN LARGER FACTORIES:
Place 2+ tiles South of burner-line-segment row at same X alignment.
Instantiate multiple times at X offsets (0, 8, 16...) to collect from
corresponding segment instances. Ore merges and flows East for collection.
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.prototypes.transport_belt import TransportBelt
from draftsman.prototypes.underground_belt import UndergroundBelt
from draftsman.prototypes.splitter import Splitter


def create_blueprint() -> Blueprint:
    """Create and return the burner line cap blueprint."""
    bp = Blueprint()
    bp.label = "Burner Line Cap"
    bp.description = "Ore collection cap for burner drill line segments"

    # Left input belts - connect to fuel belts from segments above
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(0, 1),
            direction=0,  # North (default)
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(0, 0),
            direction=4,  # East
        )
    )

    # Pre-splitter belt - connects fuel vertically
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(1, 1),
            direction=0,  # North (default)
        )
    )

    # Underground belt inputs
    bp.entities.append(
        UndergroundBelt(
            "underground-belt",
            position=(2, 1),
            direction=4,  # East
            io_type="input",
        )
    )
    bp.entities.append(
        UndergroundBelt(
            "underground-belt",
            position=(2, 0),
            direction=12,  # West
            io_type="input",
        )
    )

    # Left splitter (splits the flow)
    bp.entities.append(
        Splitter(
            "splitter",
            position=(3, 0),
            direction=12,  # West
        )
    )

    # Middle belts
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(4, 1),
            direction=12,  # West
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(4, 0),
            direction=12,  # West
        )
    )

    # Underground outputs
    bp.entities.append(
        UndergroundBelt(
            "underground-belt",
            position=(5, 0),
            direction=12,  # West
            io_type="output",
        )
    )
    bp.entities.append(
        UndergroundBelt(
            "underground-belt",
            position=(5, 1),
            direction=4,  # East
            io_type="output",
        )
    )

    # Right splitter (merges the flow)
    bp.entities.append(
        Splitter(
            "splitter",
            position=(6, 0),
            direction=4,  # East
        )
    )

    # Right output belts
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(7, 0),
            direction=4,  # East
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(7, 1),
            direction=4,  # East
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(8, 0),
            direction=4,  # East
        )
    )
    bp.entities.append(
        TransportBelt(
            "transport-belt",
            position=(8, 1),
            direction=0,  # North (default)
        )
    )

    return bp


if __name__ == "__main__":
    blueprint = create_blueprint()
    print(blueprint.to_string())
