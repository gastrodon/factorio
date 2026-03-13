# Machine Style Guide

Code style conventions for Machine classes.

## Minimal Segments

Design machines as the smallest tileable unit. One drill, one furnace, one assembler — not arrays of them. Use `tile()` to create multiples.

```python
# Good: single furnace segment
class FurnaceSegment(Machine):
    tile_axis = "y"
    tile_stride = 3

# Usage: tile to desired count
row = FurnaceSegment(config).tile(12)
```

```python
# Bad: hardcoded array inside machine
class FurnaceRow(Machine):
    def _render(self):
        for i in range(12):  # Don't do this
            ...
```

This keeps machines composable and flexible. The caller decides quantity.

## Module Structure

Each file defines one or more related `Machine` subclasses with their configs. Define each config immediately before its machine:

```python
from lib import Machine, MachineConfig

@dataclass
class FurnaceConfig(MachineConfig):
    fuel: str = "coal"

class Furnace(Machine):
    ...

@dataclass
class DrillConfig(MachineConfig):
    direction: int = 8

class Drill(Machine):
    ...
```

Always annotate return types on all functions.

## Type Hints

Store typed configs before calling `super().__init__()`:

```python
def __init__(self, config: MyConfig | None = None) -> None:
    self._cfg = config or MyConfig()
    super().__init__(self._cfg)
```

## Layout Conventions

- Normalize coordinates to the origin. The logical start or center should sit at `(0, 0)`.
- Use `.5` offsets for 1×1 entities when they tile on a 2-tile grid (e.g. `position=(-0.5, 0.5)`).
- Set `tile_axis` and `tile_stride` class attributes for tileable machines.
- Define `inputs` and `outputs` connection points for composable machines.

## Direction Reference

Factorio directions are multiples of 2 (0–14):

| Value | Cardinal |
|-------|----------|
| 0     | North    |
| 4     | East     |
| 8     | South    |
| 12    | West     |

Always write the numeric value in code and note the cardinal name in a comment:

```python
direction=4  # East
```

## Config Conventions

- Inherit from `MachineConfig` to get `belt_tier` and `inserter_tier`
- Use sensible defaults for all fields
- Keep configs immutable after construction
- Name config classes with `Config` suffix matching the machine: `DrillLine` → `DrillLineConfig`

## Entity Placement

In `_render()`, reference config values rather than hardcoding:

```python
def _render(self) -> None:
    cfg = self._cfg
    for i in range(cfg.length):
        self.entities.append(
            TransportBelt(cfg.belt_tier, position=(i, 0), direction=cfg.direction)
        )
```

## Connection Points

Set connection points at the end of `_render()` when positions depend on config:

```python
def _render(self) -> None:
    # ... place entities ...

    self.inputs = [ConnectionPoint("in", (0, 0), cfg.direction)]
    self.outputs = [ConnectionPoint("out", (cfg.length, 0), cfg.direction)]
```

Use class attributes when positions are fixed:

```python
class Drill(Machine):
    outputs = [ConnectionPoint("ore", (2, 0), direction=4)]
```

## Naming

- Machine classes: `PascalCase` describing the unit (`DrillLine`, `FurnaceColumn`)
- Config classes: Machine name + `Config` suffix
- Connection point names: lowercase, short (`"in"`, `"out"`, `"ore"`, `"plates"`)
