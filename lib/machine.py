"""Machine base class for compositional Factorio production units."""

import copy
import json
from typing import ClassVar, Callable, Literal

from draftsman.classes.blueprint import Blueprint
from draftsman.utils import AABB

from lib.config import MachineConfig
from lib.types import ConnectionPoint, BeltPath


class Machine(Blueprint):
    """Base class for compositional Factorio production units."""

    # === Class Attributes (override in subclasses) ===

    # Composition: list of factories that create child machines
    children: ClassVar[list[Callable[[MachineConfig], "Machine"]]] = []

    # I/O interface
    inputs: ClassVar[list[ConnectionPoint]] = []
    outputs: ClassVar[list[ConnectionPoint]] = []

    # Belt connectivity (for path tracing)
    belt_paths: ClassVar[list[BeltPath]] = []

    # Tiling
    tile_axis: ClassVar[Literal["x", "y"] | None] = None
    tile_stride: ClassVar[int] = 0

    # Spacing
    padding: ClassVar[tuple[int, int, int, int]] = (0, 0, 0, 0)  # TRBL
    margin: ClassVar[tuple[int, int, int, int]] = (0, 0, 0, 0)

    # === Instance Methods ===

    def __init__(self, config: MachineConfig | None = None) -> None:
        super().__init__()
        self.config = config or MachineConfig()
        self._render()

    def _render(self) -> None:
        """Render all children, merging their entities into self."""
        for child_factory in self.children:
            child = child_factory(self.config)
            for entity in child.entities:
                self.entities.append(entity)

    # === Properties ===

    @property
    def box(self) -> AABB:
        """Bounding box (delegates to draftsman)."""
        return self.get_world_bounding_box()

    # === Public Methods ===

    def to_json(self) -> str:
        """Export blueprint as JSON string."""
        return json.dumps(self.to_dict())

    def tile(self, count: int) -> "Machine":
        """
        Create a new Machine with `count` copies tiled along tile_axis.
        Each copy is offset by tile_stride.
        Returns a new Machine instance.
        """
        if self.tile_axis is None or self.tile_stride == 0:
            raise ValueError("tile_axis and tile_stride must be set")

        result = Machine(self.config)
        result.label = f"{self.label} x{count}" if self.label else None

        for i in range(count):
            offset_x = i * self.tile_stride if self.tile_axis == "x" else 0
            offset_y = i * self.tile_stride if self.tile_axis == "y" else 0

            for entity in self.entities:
                entity_copy = copy.deepcopy(entity)
                entity_copy.position = (
                    entity_copy.position[0] + offset_x,
                    entity_copy.position[1] + offset_y,
                )
                result.entities.append(entity_copy)

        return result

    def connect_to(self, other: "Machine", output: str, input: str) -> "Machine":
        """
        Connect this machine's named output to another's named input.
        Returns a new Machine containing both with appropriate offset.
        """
        # Find connection points
        out_point = next((p for p in self.outputs if p.name == output), None)
        in_point = next((p for p in other.inputs if p.name == input), None)

        if not out_point or not in_point:
            raise ValueError(f"Connection points not found: {output}, {input}")

        # Calculate offset to align points
        offset_x = out_point.position[0] - in_point.position[0]
        offset_y = out_point.position[1] - in_point.position[1]

        # Create combined machine
        result = Machine(self.config)

        for entity in self.entities:
            result.entities.append(copy.deepcopy(entity))

        for entity in other.entities:
            entity_copy = copy.deepcopy(entity)
            entity_copy.position = (
                entity_copy.position[0] + offset_x,
                entity_copy.position[1] + offset_y,
            )
            result.entities.append(entity_copy)

        return result
