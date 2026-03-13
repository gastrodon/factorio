"""Belt machine types for straight and curved belt paths."""

from dataclasses import dataclass, field

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
class StraightBeltConfig(MachineConfig):
    """
    Config for StraightBelt.

    length: number of belt tiles to place (>= 1)
    direction: belt facing direction (0=N, 4=E, 8=S, 12=W)
    belt_tier: belt entity name (inherited from MachineConfig)
    """

    length: int = 1
    direction: int = 4


class StraightBelt(Machine):
    """
    Straight belt segment of configurable length and direction.

    Places a contiguous line of belt tiles starting at origin and
    extending in the configured direction. Items flow toward that
    direction.

    Layout (direction=4, length=3):
        x=0: belt facing east
        x=1: belt facing east
        x=2: belt facing east

    Inputs:  "in" at (0, 0)
    Outputs: "out" at (length, 0) — one tile past last belt

    Example:
        belt = StraightBelt(StraightBeltConfig(length=5, direction=4))

        config = StraightBeltConfig(
            belt_tier="fast-transport-belt",
            length=10,
            direction=8  # South
        )
        belt = StraightBelt(config)
        print(belt.to_string())
    """

    def __init__(self, config: StraightBeltConfig | None = None) -> None:
        self._cfg = config or StraightBeltConfig()
        super().__init__(self._cfg)

    def _render(self) -> None:
        cfg = self._cfg
        dx, dy = _DIR_VECTORS[cfg.direction]

        for i in range(cfg.length):
            pos = (i * dx, i * dy)
            self.entities.append(
                TransportBelt(cfg.belt_tier, position=pos, direction=cfg.direction)
            )

        end_pos = ((cfg.length - 1) * dx, (cfg.length - 1) * dy)
        out_pos = (end_pos[0] + dx, end_pos[1] + dy)

        self.inputs = [ConnectionPoint("in", (0, 0), cfg.direction)]
        self.outputs = [ConnectionPoint("out", out_pos, cfg.direction)]


@dataclass
class SegmentedBeltConfig(MachineConfig):
    """
    Config for SegmentedBelt.

    segments: list of (length, direction) tuples defining the path;
        each tuple places `length` belts facing `direction`;
        segments connect sequentially; direction changes create curves
    belt_tier: belt entity name (inherited from MachineConfig)
    """

    segments: list[tuple[int, int]] = field(default_factory=list)


class SegmentedBelt(Machine):
    """
    Belt path with multiple segments, allowing curves.

    Composes multiple straight runs into a single belt path. Each
    segment specifies length and direction; the belt curves where
    direction changes. Starts at origin and extends per segment list.

    Layout (segments=[(3, 4), (4, 8)]):
        (0,0)→(1,0)→(2,0)
                      ↓
                    (2,1)
                      ↓
                    (2,2)
                      ↓
                    (2,3)

    Inputs:  "in" at (0, 0), direction from first segment
    Outputs: "out" one tile past last belt, direction from last segment

    Example:
        # L-shaped: 3 east, then 4 south
        belt = SegmentedBelt(SegmentedBeltConfig(
            segments=[(3, 4), (4, 8)]
        ))

        # U-shaped with fast belts
        config = SegmentedBeltConfig(
            belt_tier="fast-transport-belt",
            segments=[(2, 4), (3, 0), (2, 12)]  # East, North, West
        )
        belt = SegmentedBelt(config)
        print(belt.to_string())
    """

    def __init__(self, config: SegmentedBeltConfig | None = None) -> None:
        self._cfg = config or SegmentedBeltConfig()
        super().__init__(self._cfg)

    def _render(self) -> None:
        cfg = self._cfg
        if not cfg.segments:
            return

        x, y = 0.0, 0.0

        for seg_idx, (length, direction) in enumerate(cfg.segments):
            dx, dy = _DIR_VECTORS[direction]

            for i in range(length):
                self.entities.append(
                    TransportBelt(cfg.belt_tier, position=(x, y), direction=direction)
                )
                if not (seg_idx == len(cfg.segments) - 1 and i == length - 1):
                    x += dx
                    y += dy

        self._setup_connection_points()

    def _setup_connection_points(self) -> None:
        cfg = self._cfg
        if not cfg.segments:
            return

        first_dir = cfg.segments[0][1]
        last_dir = cfg.segments[-1][1]

        x, y = 0.0, 0.0
        for length, direction in cfg.segments:
            dx, dy = _DIR_VECTORS[direction]
            x += (length - 1) * dx
            y += (length - 1) * dy
            if (length, direction) != cfg.segments[-1]:
                x += dx
                y += dy

        dx, dy = _DIR_VECTORS[last_dir]
        out_pos = (x + dx, y + dy)

        self.inputs = [ConnectionPoint("in", (0, 0), first_dir)]
        self.outputs = [ConnectionPoint("out", out_pos, last_dir)]


@dataclass
class CurveBeltConfig(MachineConfig):
    """
    Config for CurveBelt.

    radius: curve size; first segment is radius-1 tiles, second is radius tiles
    direction: entry direction (0=N, 4=E, 8=S, 12=W)
    turn: "left" or "right" for turn direction (screen-relative)
    belt_tier: belt entity name (inherited from MachineConfig)
    """

    radius: int = 2
    direction: int = 4
    turn: str = "left"


class CurveBelt(Machine):
    """
    90-degree belt curve with configurable radius.

    Places a curved belt path: radius-1 tiles in the entry direction,
    then radius tiles perpendicular (turning left or right). The curve
    tile is the last of the first segment / first of the second.

    Turn direction is screen-relative: "right" from South goes East,
    "left" from East goes South.

    Layout (radius=3, direction=4 East, turn="left" to South):
        (0,0)→(1,0)→(2,0)
                      ↓
                    (2,1)
                      ↓
                    (2,2)

    Inputs:  "in" at (0, 0), entry direction
    Outputs: "out" at (2, 3), exit direction

    Layout (radius=2, direction=8 South, turn="right" to East):
        (0,0)
          ↓
        (0,1)→(1,1)

    Inputs:  "in" at (0, 0), entry direction
    Outputs: "out" at (2, 1), exit direction

    Example:
        # Left turn from East to South
        curve = CurveBelt(CurveBeltConfig(radius=3, direction=4, turn="left"))

        # Right turn from South to East with fast belts
        config = CurveBeltConfig(
            radius=2,
            direction=8,  # South entry
            turn="right",  # Exit East
            belt_tier="fast-transport-belt"
        )
        curve = CurveBelt(config)
        print(curve.to_string())
    """

    def __init__(self, config: CurveBeltConfig | None = None) -> None:
        self._cfg = config or CurveBeltConfig()
        super().__init__(self._cfg)

    def _render(self) -> None:
        cfg = self._cfg

        # Calculate exit direction based on turn (screen-relative)
        # "left" = clockwise (+4), "right" = counter-clockwise (-4)
        if cfg.turn == "left":
            exit_dir = (cfg.direction + 4) % 16
        else:  # right
            exit_dir = (cfg.direction - 4) % 16

        # Build as two segments
        segments = [
            (cfg.radius - 1, cfg.direction),
            (cfg.radius, exit_dir),
        ]

        # Place belts
        x, y = 0.0, 0.0
        for seg_idx, (length, direction) in enumerate(segments):
            dx, dy = _DIR_VECTORS[direction]

            for i in range(length):
                self.entities.append(
                    TransportBelt(cfg.belt_tier, position=(x, y), direction=direction)
                )
                if not (seg_idx == len(segments) - 1 and i == length - 1):
                    x += dx
                    y += dy

        # Connection points
        dx, dy = _DIR_VECTORS[exit_dir]
        out_pos = (x + dx, y + dy)

        self.inputs = [ConnectionPoint("in", (0, 0), cfg.direction)]
        self.outputs = [ConnectionPoint("out", out_pos, exit_dir)]


@dataclass
class DiagonalBeltConfig(MachineConfig):
    """
    Config for DiagonalBelt.

    length: number of zigzag units (each unit moves +1 in both directions)
    heading: tuple of two perpendicular directions defining the diagonal;
        e.g., (4, 8) for southeast, (0, 12) for northwest
    belt_tier: belt entity name (inherited from MachineConfig)
    """

    length: int = 4
    heading: tuple[int, int] = (4, 8)


class DiagonalBelt(Machine):
    """
    Diagonal belt using alternating radius-1 curves.

    Creates a zigzag pattern that moves diagonally by alternating
    between two perpendicular directions. Each zigzag unit is one
    tile in each direction, creating a 45-degree diagonal path.

    The heading tuple specifies two perpendicular directions. The
    belt alternates: dir1 → curve → dir2 → curve → dir1 → ...

    Layout (length=3, heading=(4, 8) for southeast):
        (0,0)→(1,0)
                ↓
              (1,1)→(2,1)
                      ↓
                    (2,2)→(3,2)

    Inputs:  "in" at (0, 0), first heading direction
    Outputs: "out" past last belt, second heading direction

    Example:
        # Southeast diagonal, 5 units
        diag = DiagonalBelt(DiagonalBeltConfig(length=5, heading=(4, 8)))

        # Northwest diagonal with fast belts
        config = DiagonalBeltConfig(
            length=8,
            heading=(0, 12),  # North + West = northwest
            belt_tier="fast-transport-belt"
        )
        diag = DiagonalBelt(config)
        print(diag.to_string())

    Headings:
        (4, 8)  = Southeast (right-down)
        (4, 0)  = Northeast (right-up)
        (12, 8) = Southwest (left-down)
        (12, 0) = Northwest (left-up)
    """

    tile_axis = None  # Diagonal belts don't tile simply

    def __init__(self, config: DiagonalBeltConfig | None = None) -> None:
        self._cfg = config or DiagonalBeltConfig()
        super().__init__(self._cfg)

    def _render(self) -> None:
        cfg = self._cfg
        dir1, dir2 = cfg.heading

        # Validate perpendicular directions
        if abs(dir1 - dir2) not in (4, 12):
            raise ValueError(f"Heading directions must be perpendicular: {cfg.heading}")

        # Build zigzag pattern: alternating single tiles with curves
        x, y = 0.0, 0.0
        dx1, dy1 = _DIR_VECTORS[dir1]
        dx2, dy2 = _DIR_VECTORS[dir2]

        for i in range(cfg.length):
            # Place belt in first direction
            self.entities.append(
                TransportBelt(cfg.belt_tier, position=(x, y), direction=dir1)
            )
            x += dx1
            y += dy1

            # Place belt in second direction (curve happens automatically)
            self.entities.append(
                TransportBelt(cfg.belt_tier, position=(x, y), direction=dir2)
            )

            # Move to next zigzag unit (except on last iteration)
            if i < cfg.length - 1:
                x += dx2
                y += dy2

        self._setup_connection_points()

    def _setup_connection_points(self) -> None:
        cfg = self._cfg
        dir1, dir2 = cfg.heading
        dx1, dy1 = _DIR_VECTORS[dir1]
        dx2, dy2 = _DIR_VECTORS[dir2]

        # End position: length units in each direction, minus one step in dir2
        end_x = cfg.length * dx1 + (cfg.length - 1) * dx2
        end_y = cfg.length * dy1 + (cfg.length - 1) * dy2

        # Output is one tile past the last belt in dir2
        out_pos = (end_x + dx2, end_y + dy2)

        self.inputs = [ConnectionPoint("in", (0, 0), dir1)]
        self.outputs = [ConnectionPoint("out", out_pos, dir2)]
