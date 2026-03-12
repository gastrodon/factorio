# Agent Guidelines for Factorio Blueprint Code

## Philosophy: Single Tileable Units, Not Generators

### Core Principle

**Each `.facto` file should represent ONE physical tileable unit**, not a generator function that creates N units.

❌ **WRONG:**
```facto
func burner_segments(int count) {
    for group in 0..count {
        // generate N segments
    }
}
burner_segments(5);
```

✅ **CORRECT:**
```facto
# Single segment that can be instantiated multiple times
Entity fuel_in = place("transport-belt", 0, 0);
Entity drill = place("burner-mining-drill", 2, 0);
// ... rest of single unit
```

### Rationale

1. **Composability**: Higher-level factory code can instantiate these units at different positions, rotations, and contexts
2. **Reusability**: A single unit is easier to understand, test, and reuse than a parameterized generator
3. **Separation of concerns**: The unit defines WHAT it is, the factory code defines HOW MANY and WHERE
4. **Modularity**: Units can be mixed, matched, and combined without modifying their source

## Documentation Standard for Tileable Units

Every `.facto` file representing a tileable unit MUST have comprehensive header documentation with these sections:

### Required Documentation Sections

```facto
# ============================================================================
# [UNIT NAME] - Single Tileable Unit
# ============================================================================
#
# DESCRIPTION:
# One [brief description of what this unit does and its components]
#
# DIMENSIONS:
# - Width: X tiles (x: start to end)
# - Height: Y tiles (y: start to end)
# - Depth: Z tiles (if applicable)
#
# TILING DIRECTION:
# - [Primary direction: Horizontal/Vertical/Both]
# - [How to stack: increment X by N, Y by M, etc.]
# - [Edge behavior: does right edge overlap with left edge of next unit?]
#
# INPUTS:
# - [Input type]: [Location coordinates] - [Direction/flow]
#   * [What connects here]
#   * [Special notes for first instance vs subsequent instances]
#   * [Dependencies or requirements]
#
# OUTPUTS:
# - [Output type]: [Location coordinates] - [Direction/flow]
#   * [What this produces or where it flows]
#   * [How to connect to next stage]
# - [Additional outputs if applicable]
#
# LAYOUT:
# x=N: [What's at this coordinate]
# x=M: [What's at this coordinate]
# [... complete spatial layout]
#
# USAGE IN LARGER FACTORIES:
# [How this unit should be instantiated in higher-level factory code]
# [Typical patterns: offset calculations, alignment with other units]
# [What to pair it with]
#
# ============================================================================
```

### Example: Good Documentation

See `drill/burner-line-segment.facto` and `drill/burner-line-cap.facto` for complete examples.

## Input/Output Specification

### Critical Information to Document

For each input/output, specify:

1. **Physical location**: Exact coordinates (x=N, y=M)
2. **Type**: What flows through (fuel, ore, items, fluids)
3. **Direction**: Which way belts flow (NORTH/SOUTH/EAST/WEST, direction codes)
4. **Connection requirements**:
   - What needs to connect externally
   - What is shared between tiled instances
   - Special cases (e.g., "only first instance needs external input")

### Tiling Edge Cases

**Document edge interlacing clearly:**

```
# When tiling: right edge (x=8) of instance N becomes left edge (x=0) of instance N+1
# Only the FIRST instance needs external input at x=0
# Subsequent instances reuse x=8 from previous as their x=0
```

This tells higher-level code:
- First instance: needs external connection at x=0
- Nth instance: inherits from (N-1)th instance's x=8

## Layout Section Format

Provide a **spatial map** of the unit:

```
# LAYOUT:
# x=0: Left fuel belts (input)
# x=1: Burner inserter → feeds first drill
# x=2-4: First drill (facing East) → outputs to x=4
# x=4: Middle ore belts (output, flowing South)
# x=5-7: Second drill (facing West) → outputs to x=4
# x=7: Burner inserter → feeds second drill
# x=8: Right fuel belts (passthrough for next instance)
```

This gives agents (human or AI) an immediate spatial understanding without parsing code.

## Usage Section: Composition Hints

The USAGE section should explain:

1. **Typical instantiation pattern**: "Instantiate at X offsets (0, 8, 16, 24...)"
2. **Coordinate alignment**: "Place 2 tiles South of burner-line-segment"
3. **Pairing with other units**: "Pair with burner-line-cap instances below"
4. **Common parameters**: Offset calculations, rotation needs

This bridges the gap between "what this unit is" and "how to build with it."

## Directory Organization

```
drill/
├── burner-line-segment.facto  # Single 8x2 drill segment
├── burner-line-cap.facto      # Single 8x2 ore collection cap
└── README-facto.md            # Directory-level overview

furnace/
├── [future furnace units]
```

- One file = one tileable unit
- Keep obsolete generator-style files OUT of the repo
- Group by factory subsystem (drill, furnace, smelting, etc.)

## Working with Existing Code

If you encounter generator-style code:

1. **Extract the single unit** from inside the loop
2. **Remove the loop and function wrapper**
3. **Add comprehensive documentation** following the standard above
4. **Update variable names** to remove loop indices (e.g., `x_base + 1` → just `1`)
5. **Document tiling behavior** that was previously implicit in the loop

## Future Factory Generation

Higher-level factory code will:

```python
# Pseudocode example
for i in range(num_segments):
    instantiate("drill/burner-line-segment.facto", x_offset=i*8, y_offset=0)

for i in range(num_segments):
    instantiate("drill/burner-line-cap.facto", x_offset=i*8, y_offset=2)
```

The `.facto` units remain clean and focused. The composition logic lives elsewhere.

## Key Takeaways for Agents

1. **One file = one physical unit**, not a generator
2. **Document exhaustively**: inputs, outputs, dimensions, tiling, usage
3. **Think spatially**: provide coordinate maps and flow directions
4. **Enable composition**: explain how to instantiate multiple times
5. **Interlacing matters**: document edge-sharing behavior clearly
6. **Separation of concerns**: unit definition vs. factory layout logic

---

When in doubt, ask: "If I gave this file to someone building a larger factory, would they know EXACTLY how to use it without reading the code?" If not, add more documentation.
