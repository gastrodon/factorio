# Generating Machine Files

Guidelines for writing prompts and generating Machine files with LLMs.

## Prompt Structure

When asking an LLM to generate a Machine, provide:

1. **What it produces** - The machine's purpose
2. **Entity layout** - Rough sketch or coordinates
3. **Config parameters** - What should be configurable
4. **I/O points** - Where it connects to other machines
5. **Tiling behavior** - If applicable

## Example Prompts

### Simple Leaf Machine

> Create a `StoneFurnace` machine that places a single stone furnace with an input inserter on the north and output inserter on the south. Config should include inserter tier.

### Parameterized Machine

> Create a `BeltBalancer` machine for 4-to-4 balancing. Config: belt tier. Should have 4 input connection points on the west and 4 output points on the east.

### Tileable Machine

> Create a `SmelterColumn` machine: one furnace with input belt on west, output belt on east. Tileable on Y axis with stride 3. Config: furnace type (stone/steel), belt tier, inserter tier.

### Composite Machine

> Create a `MiningOutpost` that composes:
> - 8x DrillRow (tileable drill segments)
> - BeltCollector (gathers outputs to single belt)
> - OutputBus (belt leading away)
>
> Config: drill count, belt tier. Output connection point "ore" at the end of the output bus.

## Generation Checklist

When generating, ensure the output includes:

- [ ] Module docstring with description, layout, and examples
- [ ] Config dataclass with sensible defaults
- [ ] Proper `__init__` storing typed config before `super().__init__()`
- [ ] `_render()` placing all entities
- [ ] Connection points set (as class attrs or in `_render()`)
- [ ] Direction comments (e.g., `direction=4  # East`)
- [ ] Type hints on all functions

## Class Docstrings

Config dataclasses have docstrings describing their fields:

```python
@dataclass
class FurnaceSegmentConfig(MachineConfig):
    """
    Config for FurnaceSegment.

    furnace_type: "stone-furnace" or "steel-furnace"
    direction: output direction (default 8 = south)
    """
    furnace_type: str = "stone-furnace"
    direction: int = 8
```

No inline comments on fields — put all documentation in the docstring.

Machine classes have docstrings with layout info and usage examples:

```python
class FurnaceSegment(Machine):
    """
    Single smelting unit with belt I/O.

    Minimal tileable furnace with input belt on west, output belt
    on east, inserters handling material flow.

    Layout (tile_stride=3 on y-axis):
        x=-1: input belt
        x=0,1: furnace (2x2)
        x=2: output belt

    Inputs:  "in" at (-1, 0), direction=8
    Outputs: "out" at (2, 2), direction=8

    Example:
        furnace = FurnaceSegment()

        config = FurnaceSegmentConfig(belt_tier="fast-transport-belt")
        row = FurnaceSegment(config).tile(12)
        print(row.to_string())
    """
```

## Common Patterns

### Direction Handling

Always include the direction lookup table when the machine uses directions:

```python
_DIR_VECTORS = {
    0: (0, -1),   # North
    4: (1, 0),    # East
    8: (0, 1),    # South
    12: (-1, 0),  # West
}
```

### Grid Placement

For machines with grid-aligned entities:

```python
def _render(self) -> None:
    for row in range(self.rows):
        for col in range(self.cols):
            x = col * self.cell_width
            y = row * self.cell_height
            # Place entities at (x, y)
```

### Inserter Pairs

Furnaces/assemblers typically need inserter pairs:

```python
# Input inserter (grabs from belt, puts in machine)
self.entities.append(
    Inserter(cfg.inserter_tier, position=(x-1, y), direction=4)  # Facing east into machine
)
# Output inserter (grabs from machine, puts on belt)
self.entities.append(
    Inserter(cfg.inserter_tier, position=(x+1, y), direction=4)  # Facing east onto belt
)
```

### Entity Sizes

Common entity dimensions (for spacing calculations):

| Entity | Size | Position Point |
|--------|------|----------------|
| Transport belt | 1×1 | Center |
| Inserter | 1×1 | Center |
| Stone furnace | 2×2 | Center |
| Steel furnace | 2×2 | Center |
| Electric mining drill | 3×3 | Center |
| Assembling machine 1 | 3×3 | Center |
| Assembling machine 2/3 | 3×3 | Center |

### Half-Tile Positions

1×1 entities on a 2-tile grid often use `.5` offsets:

```python
# Belt at (0.5, 0.5) aligns to tile grid when tiling by 2
TransportBelt("transport-belt", position=(0.5, 0.5), direction=4)
```

## Validation

After generation, verify:

1. **Import test**: `python -c "from lib.my_machine import MyMachine"`
2. **Instantiation**: `m = MyMachine(MyConfig())`
3. **Export**: `print(m.to_string())` produces valid blueprint
4. **Game test**: Paste into Factorio, verify layout

## Anti-Patterns

### Don't: Hardcode tiers

```python
# Bad
TransportBelt("fast-transport-belt", ...)

# Good
TransportBelt(cfg.belt_tier, ...)
```

### Don't: Forget connection points

Machines without I/O points can't compose. Always define at least outputs for producers, inputs for consumers.

### Don't: Mix concerns

A leaf machine should either:
- Place entities directly, OR
- Compose children via `children` list

Not both. If you need both, extract the entity placement into a child machine.

### Don't: Use magic numbers

```python
# Bad
position=(7, 3)

# Good
end_x = cfg.length * tile_stride
position=(end_x, belt_y)
```
