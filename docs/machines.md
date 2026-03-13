# Machine Class Guide

This guide covers how to write and generate Machine files using the `lib/` framework.

## Overview

A `Machine` is a composable Factorio production unit that extends draftsman's `Blueprint`. Machines can:

- Place entities directly (leaf machines)
- Compose other machines (composite machines)
- Tile along an axis
- Connect to other machines via named I/O points

## Core Concepts

### Config Classes

Every machine type has a corresponding config dataclass. Configs flow down from parent to children during composition.

```python
from dataclasses import dataclass
from lib import MachineConfig

@dataclass
class MyMachineConfig(MachineConfig):
    """Extend base config with machine-specific parameters."""
    length: int = 4
    direction: int = 4  # East
```

Base `MachineConfig` provides:
- `belt_tier: str = "transport-belt"`
- `inserter_tier: str = "inserter"`

### Leaf Machines

Leaf machines place entities directly. Override `_render()` to add entities.

```python
from lib import Machine
from draftsman.prototypes.transport_belt import TransportBelt

class MyBelt(Machine):
    def __init__(self, config: MyBeltConfig) -> None:
        self._my_config = config  # Store typed config
        super().__init__(config)

    def _render(self) -> None:
        cfg = self._my_config
        for i in range(cfg.length):
            self.entities.append(
                TransportBelt(cfg.belt_tier, position=(i, 0), direction=cfg.direction)
            )
```

### Composite Machines

Composite machines combine children via the `children` class attribute.

```python
class ProductionLine(Machine):
    children = [
        lambda c: DrillArray(c),
        lambda c: BeltPath(c),
        lambda c: FurnaceRow(c),
    ]
```

Children are factory functions that receive the parent's config. The base `_render()` method instantiates each child and merges their entities.

## Connection Points

Define named I/O points for composition.

```python
from lib import Machine, ConnectionPoint

class Drill(Machine):
    inputs = []  # Drills have no input
    outputs = [ConnectionPoint("ore", (2, 0), direction=4)]  # East
```

Direction values:
| Value | Cardinal |
|-------|----------|
| 0     | North    |
| 4     | East     |
| 8     | South    |
| 12    | West     |

## Tiling

Enable tiling by setting class attributes:

```python
class DrillSegment(Machine):
    tile_axis = "x"   # or "y"
    tile_stride = 4   # tiles apart
```

Usage:
```python
segment = DrillSegment(config)
array = segment.tile(8)  # Creates 8 copies
```

## Connecting Machines

Use `connect_to()` to align machines by their connection points:

```python
drills = DrillArray(config)
smelters = FurnaceRow(config)

# Aligns drills.outputs["ore"] with smelters.inputs["raw"]
factory = drills.connect_to(smelters, output="ore", input="raw")

print(factory.to_string())
```

## Built-in Belt Machines

### StraightBelt

```python
from lib import StraightBelt, StraightBeltConfig

config = StraightBeltConfig(
    length=5,
    direction=4,  # East
    belt_tier="fast-transport-belt"
)
belt = StraightBelt(config)
```

### SegmentedBelt

For paths with curves:

```python
from lib import SegmentedBelt, SegmentedBeltConfig

config = SegmentedBeltConfig(
    segments=[
        (3, 4),   # 3 tiles East
        (2, 8),   # 2 tiles South (curve)
        (4, 4),   # 4 tiles East
    ],
    belt_tier="transport-belt"
)
belt = SegmentedBelt(config)
```

## Best Practices

### 1. Store Typed Config

The base class stores `self.config` as `MachineConfig`. Store your typed config separately:

```python
def __init__(self, config: MyConfig) -> None:
    self._my_config = config
    super().__init__(config)
```

### 2. Set Connection Points in _render()

For dynamic I/O positions, set `self.inputs` and `self.outputs` at the end of `_render()`:

```python
def _render(self) -> None:
    # ... place entities ...

    # Dynamic based on config
    self.inputs = [ConnectionPoint("in", (0, 0), self._my_config.direction)]
    self.outputs = [ConnectionPoint("out", (self._my_config.length, 0), self._my_config.direction)]
```

### 3. Use Direction Vectors

For directional placement:

```python
DIR_VECTORS = {
    0: (0, -1),   # North
    4: (1, 0),    # East
    8: (0, 1),    # South
    12: (-1, 0),  # West
}

dx, dy = DIR_VECTORS[direction]
for i in range(length):
    pos = (i * dx, i * dy)
```

### 4. Keep Configs Immutable

Configs should be treated as immutable. Don't modify them after construction.

### 5. Normalize to Origin

Place the logical start or center at `(0, 0)`. Use `.translate()` (inherited from Blueprint) to reposition if needed.

## Example: Complete Machine

```python
from dataclasses import dataclass
from lib import Machine, MachineConfig, ConnectionPoint
from draftsman.prototypes.mining_drill import MiningDrill
from draftsman.prototypes.transport_belt import TransportBelt

@dataclass
class DrillLineConfig(MachineConfig):
    drill_count: int = 4
    direction: int = 8  # Output south

class DrillLine(Machine):
    tile_axis = "x"
    tile_stride = 3  # Drill width

    def __init__(self, config: DrillLineConfig | None = None) -> None:
        self._drill_config = config or DrillLineConfig()
        super().__init__(self._drill_config)

    def _render(self) -> None:
        cfg = self._drill_config

        for i in range(cfg.drill_count):
            x = i * 3
            # Drill (3x3, position is center)
            self.entities.append(
                MiningDrill("electric-mining-drill", position=(x + 1, 1), direction=cfg.direction)
            )
            # Output belt below
            self.entities.append(
                TransportBelt(cfg.belt_tier, position=(x + 1, 3), direction=4)
            )

        # Connection points
        self.outputs = [
            ConnectionPoint("ore", (cfg.drill_count * 3, 3), direction=4)
        ]
```
