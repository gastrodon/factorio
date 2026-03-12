# Blueprint Python File Guide

This document describes conventions for writing Factorio blueprint Python files
using the `draftsman` library.

## Blueprint file formats

| Extension | Description |
|-----------|-------------|
| `.bp`     | Base64-encoded, zlib-compressed blueprint string — the raw "Export to string" format from the game |
| `.json`   | Decoded contents of a `.bp`; the same blueprint data as a human-readable JSON object |
| `.facto`  | Factompile source format; primarily useful for specifying electric/circuit conditions but also describes entity placement |

**Python files are the source of truth.** `.bp`, `.json`, and `.facto` files are
either reference material (used to understand a design) or build artefacts
(generated output). Never treat them as canonical.

## Source cleanup rule

When you create a Python blueprint file from a reference `.bp`, `.json`, or
`.facto` file, delete the corresponding source file(s) for that blueprint only.
For example, creating `foo.py` means you should delete `foo.bp`, `foo.json`,
and/or `foo.facto` if they exist — but leave all other `.bp`/`.json`/`.facto`
files untouched. Bulk cleanup of unrelated files is a `./script/clean` task, not
something to do ad-hoc.

## Module structure

Each file represents **one blueprint** — a single, fixed layout with no
parameters. The top-level export is the `Blueprint` object itself, assigned at
module level:

```python
blueprint = create_blueprint()
```

Always annotate return types on all functions.

The `create_blueprint()` function exists only to keep construction readable; the
result is always assigned at module scope so other tools can import it directly:

```python
from furnace.stone_segment import blueprint
```

Do not accept arguments in `create_blueprint()`. If variation is needed, write a
separate file.

## File permissions

Always run `chmod +x` on generated Python files.

## CLI

Include a minimal `__main__` block that prints the blueprint string and nothing
else:

```python
if __name__ == "__main__":
    print(blueprint.to_string())
```

Do not add argument parsing, `--help`, flags, or any other CLI surface. Tooling
that wraps these files handles parameterization externally.

## What to include

Place only the entities that are the direct subject of the blueprint:

- The machines performing the work (furnaces, drills, assemblers, etc.)
- Inserters and belts that are structurally part of the segment's I/O
- Underground belts where they are an intrinsic part of the segment interface

Do **not** include:

- Electric poles, substations, or any power infrastructure
- Roboports, lamps, speakers, or other support infrastructure
- Entities that belong to an adjacent segment or connection layer

If an entity would be shared between two tiled instances, it does not belong in
the segment file.

## Layout conventions

- Normalize coordinates to the origin. The logical center or top-left of the
  segment should sit at or near `(0, 0)`.
- Use `.5` offsets for 1×1 entities when they tile on a 2-tile grid (e.g.
  `position=(-0.5, 0.5)`). This is normal and correct in draftsman.
- Document the bounding box, tiling axis, and tiling stride in the module
  docstring.
- Document named I/O points (belt entry/exit positions) in the docstring so
  callers know where to connect adjacent segments.

## Docstring format

```
<Entity name> - <one-line description>

<Paragraph describing what the segment does and how it tiles.>

Layout (normalized to origin):
  x=N, y=M: <entity> (<direction/role>)
  ...

INPUT:  <description of input connection point(s)>
OUTPUT: <description of output connection point(s)>
```

## Direction reference

Factorio directions are multiples of 2 (0–14):

| Value | Cardinal |
|-------|----------|
| 0     | North    |
| 4     | East     |
| 8     | South    |
| 12    | West     |

Always write the numeric value in code and note the cardinal name in a comment.

## Example skeleton

```python
#!/usr/bin/env python3
"""
Widget Segment - single tileable unit

<description>

Layout (normalized to origin):
  x=0, y=0: <entity>
  ...

INPUT:  <position and direction>
OUTPUT: <position and direction>
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.prototypes.furnace import Furnace
from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.transport_belt import TransportBelt


def create_blueprint() -> Blueprint:
    bp = Blueprint()
    bp.label = "Widget Segment"
    bp.description = "Single tileable widget segment"

    bp.entities.append(Furnace("stone-furnace", position=(0, 0)))
    # ... remaining entities ...

    return bp


blueprint = create_blueprint()

if __name__ == "__main__":
    print(blueprint.to_string())
```
