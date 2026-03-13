# Machine Quick Reference

## Class Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `children` | `list[Callable[[MachineConfig], Machine]]` | `[]` | Child machine factories |
| `inputs` | `list[ConnectionPoint]` | `[]` | Input connection points |
| `outputs` | `list[ConnectionPoint]` | `[]` | Output connection points |
| `belt_paths` | `list[BeltPath]` | `[]` | Belt path definitions |
| `tile_axis` | `"x" \| "y" \| None` | `None` | Tiling direction |
| `tile_stride` | `int` | `0` | Distance between tiled copies |
| `padding` | `tuple[int,int,int,int]` | `(0,0,0,0)` | Internal spacing (TRBL) |
| `margin` | `tuple[int,int,int,int]` | `(0,0,0,0)` | External spacing (TRBL) |

## Instance Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `tile(count)` | `Machine` | Create tiled copies |
| `connect_to(other, output, input)` | `Machine` | Connect by named I/O |
| `to_string()` | `str` | Export blueprint string |
| `translate(x, y)` | `None` | Move all entities |
| `get_world_bounding_box()` | `AABB` | Get bounds |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `box` | `AABB` | Bounding box shorthand |
| `config` | `MachineConfig` | Current config |
| `entities` | `EntityList` | All entities |

## Directions

```
     0 (North)
         ↑
12 (W) ←   → 4 (East)
         ↓
     8 (South)
```

## Direction Vectors

```python
{0: (0,-1), 4: (1,0), 8: (0,1), 12: (-1,0)}
```

## Built-in Configs

### MachineConfig
```python
belt_tier: str = "transport-belt"
inserter_tier: str = "inserter"
```

### StraightBeltConfig
```python
length: int = 1
direction: int = 4
belt_tier: str = "transport-belt"
```

### SegmentedBeltConfig
```python
segments: list[tuple[int, int]] = []  # [(length, direction), ...]
belt_tier: str = "transport-belt"
```

## Imports

```python
# Core
from lib import Machine, MachineConfig, ConnectionPoint, BeltPath

# Belts
from lib import StraightBelt, StraightBeltConfig
from lib import SegmentedBelt, SegmentedBeltConfig

# Draftsman entities
from draftsman.prototypes.transport_belt import TransportBelt
from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.furnace import Furnace
from draftsman.prototypes.mining_drill import MiningDrill
from draftsman.prototypes.assembling_machine import AssemblingMachine
```

## Minimal Machine Template

```python
from dataclasses import dataclass
from lib import Machine, MachineConfig, ConnectionPoint

@dataclass
class MyConfig(MachineConfig):
    param: int = 1

class MyMachine(Machine):
    def __init__(self, config: MyConfig | None = None) -> None:
        self._cfg = config or MyConfig()
        super().__init__(self._cfg)

    def _render(self) -> None:
        # Place entities using self._cfg
        # Set self.inputs / self.outputs
        pass
```
