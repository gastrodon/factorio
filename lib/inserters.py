"""Inserter machine types."""

from dataclasses import dataclass, field

from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.transport_belt import TransportBelt

from lib.config import MachineConfig
from lib.machine import Machine
from lib.types import ConnectionPoint


_DIR_VECTORS = {
    0: (0, -1),   # North
    4: (1, 0),    # East
    8: (0, 1),    # South
    12: (-1, 0),  # West
}


@dataclass
class InserterSegmentConfig(MachineConfig):
    """
    Config for InserterSegment.

    inserter_tier: inserter entity name (default from MachineConfig)
    direction: inserter facing direction, items flow this way (0=N, 4=E, 8=S, 12=W)
    filters: list of item names to filter (requires filterable inserter)
    """

    direction: int = 0
    filters: list[str] = field(default_factory=list)


class InserterSegment(Machine):
    """
    Single inserter with configurable direction and filters.

    Places one inserter at origin facing the configured direction.
    Items flow FROM the opposite side TO the direction side.

    Layout (direction=0 North):
        (0, 0): inserter facing north
        Picks from (0, 1), drops to (0, -1)

    Inputs:  "pickup" at opposite of direction
    Outputs: "drop" at direction side

    Example:
        inserter = InserterSegment()

        config = InserterSegmentConfig(
            inserter_tier="fast-inserter",
            direction=4,  # East
            filters=["iron-plate", "copper-plate"]
        )
        inserter = InserterSegment(config)
        print(inserter.to_string())
    """

    def __init__(self, config: InserterSegmentConfig | None = None) -> None:
        self._cfg = config or InserterSegmentConfig()
        super().__init__(self._cfg)

    def _render(self) -> None:
        cfg = self._cfg
        dx, dy = _DIR_VECTORS[cfg.direction]

        inserter = Inserter(cfg.inserter_tier, position=(0, 0), direction=cfg.direction)

        # Apply filters if specified
        for i, item in enumerate(cfg.filters):
            inserter.set_item_filter(i, item)

        self.entities.append(inserter)

        # Connection points: pickup is opposite direction, drop is direction
        pickup_pos = (-dx, -dy)
        drop_pos = (dx, dy)

        self.inputs = [ConnectionPoint("pickup", pickup_pos, cfg.direction)]
        self.outputs = [ConnectionPoint("drop", drop_pos, cfg.direction)]


@dataclass
class InserterBeltSegmentConfig(MachineConfig):
    """
    Config for InserterBeltSegment.

    inserter_tier: inserter entity name (inherited from MachineConfig)
    belt_tier: belt entity name (inherited from MachineConfig)
    direction: inserter facing direction (0=N, 4=E, 8=S, 12=W)
    belt_direction: belt flow direction; default perpendicular left-to-right
    filters: list of item names to filter
    """

    direction: int = 0
    belt_direction: int | None = None
    filters: list[str] = field(default_factory=list)


class InserterBeltSegment(Machine):
    """
    Inserter with belt at pickup position.

    Places an inserter at origin with a belt tile at the pickup side.
    Belt flows perpendicular to inserter by default (left-to-right
    relative to inserter direction).

    Layout (direction=0 North, default belt):
        (0, -1): drop position (empty)
        (0,  0): inserter facing north
        (0,  1): belt flowing east (perpendicular L-to-R)

    Perpendicular belt directions:
        Inserter North (0)  -> Belt East (4)
        Inserter East (4)   -> Belt South (8)
        Inserter South (8)  -> Belt West (12)
        Inserter West (12)  -> Belt North (0)

    Inputs:  "in" at belt position, belt direction
    Outputs: "drop" at drop position, inserter direction

    tile_axis: perpendicular to inserter direction
    tile_stride: 1

    Example:
        segment = InserterBeltSegment()

        config = InserterBeltSegmentConfig(
            inserter_tier="fast-inserter",
            belt_tier="fast-transport-belt",
            direction=4,  # East
        )
        row = InserterBeltSegment(config).tile(8)
        print(row.to_string())
    """

    tile_stride = 1

    def __init__(self, config: InserterBeltSegmentConfig | None = None) -> None:
        self._cfg = config or InserterBeltSegmentConfig()
        # Set tile_axis based on direction (perpendicular)
        if self._cfg.direction in (0, 8):  # North/South
            self.tile_axis = "x"
        else:  # East/West
            self.tile_axis = "y"
        super().__init__(self._cfg)

    def _render(self) -> None:
        cfg = self._cfg
        dx, dy = _DIR_VECTORS[cfg.direction]

        # Default belt direction: perpendicular, left-to-right
        belt_dir = cfg.belt_direction
        if belt_dir is None:
            belt_dir = (cfg.direction + 4) % 16

        # Inserter at origin
        inserter = Inserter(cfg.inserter_tier, position=(0, 0), direction=cfg.direction)
        for i, item in enumerate(cfg.filters):
            inserter.set_item_filter(i, item)
        self.entities.append(inserter)

        # Belt at pickup position (opposite of inserter direction)
        belt_pos = (-dx, -dy)
        self.entities.append(
            TransportBelt(cfg.belt_tier, position=belt_pos, direction=belt_dir)
        )

        # Connection points
        drop_pos = (dx, dy)
        self.inputs = [ConnectionPoint("in", belt_pos, belt_dir)]
        self.outputs = [ConnectionPoint("drop", drop_pos, cfg.direction)]
