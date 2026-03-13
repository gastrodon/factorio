"""Tests for belt machines."""

import json
import pytest

from lib import (
    CurveBelt,
    CurveBeltConfig,
    DiagonalBelt,
    DiagonalBeltConfig,
    SegmentedBelt,
    SegmentedBeltConfig,
    StraightBelt,
    StraightBeltConfig,
)


class TestStraightBelt:
    """Tests for StraightBelt machine."""

    def test_default_config(self) -> None:
        """Default config creates single belt facing east."""
        belt = StraightBelt()
        assert len(belt.entities) == 1
        assert belt.entities[0].name == "transport-belt"
        assert belt.entities[0].direction == 4

    def test_length(self) -> None:
        """Belt has correct number of entities for given length."""
        belt = StraightBelt(StraightBeltConfig(length=5))
        assert len(belt.entities) == 5

    def test_length_one(self) -> None:
        """Single tile belt works."""
        belt = StraightBelt(StraightBeltConfig(length=1))
        assert len(belt.entities) == 1
        assert tuple(belt.entities[0].position) == (0.0, 0.0)

    def test_direction_north(self) -> None:
        """North-facing belt extends in -Y direction."""
        belt = StraightBelt(StraightBeltConfig(length=3, direction=0))
        positions = [tuple(e.position) for e in belt.entities]
        assert positions == [(0.0, 0.0), (0.0, -1.0), (0.0, -2.0)]
        assert all(e.direction == 0 for e in belt.entities)

    def test_direction_east(self) -> None:
        """East-facing belt extends in +X direction."""
        belt = StraightBelt(StraightBeltConfig(length=3, direction=4))
        positions = [tuple(e.position) for e in belt.entities]
        assert positions == [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]

    def test_direction_south(self) -> None:
        """South-facing belt extends in +Y direction."""
        belt = StraightBelt(StraightBeltConfig(length=3, direction=8))
        positions = [tuple(e.position) for e in belt.entities]
        assert positions == [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0)]

    def test_direction_west(self) -> None:
        """West-facing belt extends in -X direction."""
        belt = StraightBelt(StraightBeltConfig(length=3, direction=12))
        positions = [tuple(e.position) for e in belt.entities]
        assert positions == [(0.0, 0.0), (-1.0, 0.0), (-2.0, 0.0)]

    def test_belt_tier(self) -> None:
        """Belt tier from config is used."""
        belt = StraightBelt(StraightBeltConfig(
            length=2,
            belt_tier="fast-transport-belt"
        ))
        assert all(e.name == "fast-transport-belt" for e in belt.entities)

    def test_express_belt_tier(self) -> None:
        """Express belt tier works."""
        belt = StraightBelt(StraightBeltConfig(
            length=2,
            belt_tier="express-transport-belt"
        ))
        assert all(e.name == "express-transport-belt" for e in belt.entities)

    def test_input_connection_point(self) -> None:
        """Input connection point is at origin."""
        belt = StraightBelt(StraightBeltConfig(length=5, direction=4))
        assert len(belt.inputs) == 1
        assert belt.inputs[0].name == "in"
        assert belt.inputs[0].position == (0, 0)
        assert belt.inputs[0].direction == 4

    def test_output_connection_point_east(self) -> None:
        """Output is one tile past last belt (east)."""
        belt = StraightBelt(StraightBeltConfig(length=5, direction=4))
        assert len(belt.outputs) == 1
        assert belt.outputs[0].name == "out"
        assert belt.outputs[0].position == (5, 0)
        assert belt.outputs[0].direction == 4

    def test_output_connection_point_south(self) -> None:
        """Output is one tile past last belt (south)."""
        belt = StraightBelt(StraightBeltConfig(length=3, direction=8))
        assert belt.outputs[0].position == (0, 3)

    def test_to_string_valid(self) -> None:
        """Blueprint string can be generated."""
        belt = StraightBelt(StraightBeltConfig(length=3))
        s = belt.to_string()
        assert isinstance(s, str)
        assert len(s) > 0

    def test_to_json_valid(self) -> None:
        """JSON export is valid JSON."""
        belt = StraightBelt(StraightBeltConfig(length=2))
        j = belt.to_json()
        parsed = json.loads(j)
        assert "blueprint" in parsed
        assert len(parsed["blueprint"]["entities"]) == 2


class TestSegmentedBelt:
    """Tests for SegmentedBelt machine."""

    def test_empty_segments(self) -> None:
        """Empty segments list creates no entities."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[]))
        assert len(belt.entities) == 0

    def test_single_segment(self) -> None:
        """Single segment behaves like StraightBelt."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[(3, 4)]))
        assert len(belt.entities) == 3
        positions = [tuple(e.position) for e in belt.entities]
        assert positions == [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]

    def test_l_shape_east_south(self) -> None:
        """L-shape: east then south."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[(3, 4), (2, 8)]))
        assert len(belt.entities) == 5

        # First 3 go east
        assert tuple(belt.entities[0].position) == (0.0, 0.0)
        assert belt.entities[0].direction == 4
        assert tuple(belt.entities[1].position) == (1.0, 0.0)
        assert tuple(belt.entities[2].position) == (2.0, 0.0)

        # Next 2 go south (starting from where first segment ended)
        assert tuple(belt.entities[3].position) == (3.0, 0.0)
        assert belt.entities[3].direction == 8
        assert tuple(belt.entities[4].position) == (3.0, 1.0)

    def test_l_shape_south_east(self) -> None:
        """L-shape: south then east."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[(2, 8), (3, 4)]))
        positions = [tuple(e.position) for e in belt.entities]
        directions = [e.direction for e in belt.entities]

        # First segment places 2 south, moves to y=2, then east segment starts there
        assert positions == [
            (0.0, 0.0), (0.0, 1.0),  # South segment
            (0.0, 2.0), (1.0, 2.0), (2.0, 2.0)  # East segment
        ]
        assert directions == [8, 8, 4, 4, 4]

    def test_u_shape(self) -> None:
        """U-shape: east, south, west."""
        belt = SegmentedBelt(SegmentedBeltConfig(
            segments=[(2, 4), (2, 8), (2, 12)]
        ))
        assert len(belt.entities) == 6

        directions = [e.direction for e in belt.entities]
        assert directions == [4, 4, 8, 8, 12, 12]

    def test_snake_pattern(self) -> None:
        """Snake: alternating east/west with south turns."""
        belt = SegmentedBelt(SegmentedBeltConfig(
            segments=[
                (3, 4),   # East
                (1, 8),   # South
                (3, 12),  # West
            ]
        ))
        assert len(belt.entities) == 7

        # 3 east ends at x=2, moves to x=3; 1 south at x=3; 3 west ends at x=1
        last_pos = tuple(belt.entities[-1].position)
        assert last_pos == (1.0, 1.0)

    def test_belt_tier(self) -> None:
        """Belt tier is applied to all segments."""
        belt = SegmentedBelt(SegmentedBeltConfig(
            belt_tier="fast-transport-belt",
            segments=[(2, 4), (2, 8)]
        ))
        assert all(e.name == "fast-transport-belt" for e in belt.entities)

    def test_input_connection_point(self) -> None:
        """Input is at origin with first segment's direction."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[(2, 8), (3, 4)]))
        assert belt.inputs[0].position == (0, 0)
        assert belt.inputs[0].direction == 8

    def test_output_connection_point_l_shape(self) -> None:
        """Output is past last belt with last segment's direction."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[(3, 4), (2, 8)]))
        # Last belt at (3, 1), direction south, so output at (3, 2)
        assert belt.outputs[0].direction == 8
        assert belt.outputs[0].position == (3.0, 2.0)

    def test_180_degree_turn(self) -> None:
        """180° reversal is valid (though unusual)."""
        belt = SegmentedBelt(SegmentedBeltConfig(
            segments=[(2, 4), (2, 12)]  # East then West
        ))
        assert len(belt.entities) == 4
        directions = [e.direction for e in belt.entities]
        assert directions == [4, 4, 12, 12]

    def test_no_connection_points_when_empty(self) -> None:
        """Empty belt has no connection points."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[]))
        assert belt.inputs == []
        assert belt.outputs == []

    def test_to_json_valid(self) -> None:
        """JSON export works for segmented belt."""
        belt = SegmentedBelt(SegmentedBeltConfig(segments=[(2, 4), (2, 8)]))
        j = belt.to_json()
        parsed = json.loads(j)
        assert len(parsed["blueprint"]["entities"]) == 4


class TestCurveBelt:
    """Tests for CurveBelt machine."""

    def test_default_config(self) -> None:
        """Default: radius=2, east entry, left turn to south."""
        curve = CurveBelt()
        assert len(curve.entities) == 3  # (radius-1) + radius = 1 + 2

    def test_entity_count_by_radius(self) -> None:
        """Entity count is 2*radius - 1."""
        for radius in [2, 3, 4, 5]:
            curve = CurveBelt(CurveBeltConfig(radius=radius))
            assert len(curve.entities) == 2 * radius - 1

    def test_left_turn_east_to_south(self) -> None:
        """Left turn from east goes to south."""
        curve = CurveBelt(CurveBeltConfig(radius=2, direction=4, turn="left"))
        directions = [e.direction for e in curve.entities]
        assert directions[0] == 4  # East entry
        assert directions[-1] == 8  # South exit

    def test_left_turn_south_to_west(self) -> None:
        """Left turn from south goes to west."""
        curve = CurveBelt(CurveBeltConfig(radius=2, direction=8, turn="left"))
        directions = [e.direction for e in curve.entities]
        assert directions[0] == 8  # South entry
        assert directions[-1] == 12  # West exit

    def test_right_turn_east_to_north(self) -> None:
        """Right turn from east goes to north."""
        curve = CurveBelt(CurveBeltConfig(radius=2, direction=4, turn="right"))
        directions = [e.direction for e in curve.entities]
        assert directions[0] == 4  # East entry
        assert directions[-1] == 0  # North exit

    def test_right_turn_south_to_east(self) -> None:
        """Right turn from south goes to east."""
        curve = CurveBelt(CurveBeltConfig(radius=2, direction=8, turn="right"))
        directions = [e.direction for e in curve.entities]
        assert directions[0] == 8  # South entry
        assert directions[-1] == 4  # East exit

    def test_positions_radius_2_left(self) -> None:
        """Correct positions for radius=2 left turn from east."""
        curve = CurveBelt(CurveBeltConfig(radius=2, direction=4, turn="left"))
        positions = [tuple(e.position) for e in curve.entities]
        # 1 tile east, then 2 tiles south
        assert positions == [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]

    def test_positions_radius_3(self) -> None:
        """Correct positions for radius=3 left turn from east."""
        curve = CurveBelt(CurveBeltConfig(radius=3, direction=4, turn="left"))
        positions = [tuple(e.position) for e in curve.entities]
        # 2 tiles east, then 3 tiles south
        assert positions == [
            (0.0, 0.0), (1.0, 0.0),  # East segment
            (2.0, 0.0), (2.0, 1.0), (2.0, 2.0)  # South segment
        ]

    def test_belt_tier(self) -> None:
        """Belt tier is applied."""
        curve = CurveBelt(CurveBeltConfig(belt_tier="fast-transport-belt"))
        assert all(e.name == "fast-transport-belt" for e in curve.entities)

    def test_input_connection_point(self) -> None:
        """Input is at origin with entry direction."""
        curve = CurveBelt(CurveBeltConfig(direction=8, turn="right"))
        assert curve.inputs[0].position == (0, 0)
        assert curve.inputs[0].direction == 8

    def test_output_connection_point(self) -> None:
        """Output is past last belt with exit direction."""
        curve = CurveBelt(CurveBeltConfig(radius=2, direction=4, turn="left"))
        # Last belt at (1, 1), exit direction south, so output at (1, 2)
        assert curve.outputs[0].position == (1.0, 2.0)
        assert curve.outputs[0].direction == 8

    def test_all_entry_directions_left(self) -> None:
        """Left turns work from all cardinal directions."""
        expected_exits = {0: 4, 4: 8, 8: 12, 12: 0}  # N->E, E->S, S->W, W->N
        for entry, expected_exit in expected_exits.items():
            curve = CurveBelt(CurveBeltConfig(direction=entry, turn="left"))
            assert curve.outputs[0].direction == expected_exit

    def test_all_entry_directions_right(self) -> None:
        """Right turns work from all cardinal directions."""
        expected_exits = {0: 12, 4: 0, 8: 4, 12: 8}  # N->W, E->N, S->E, W->S
        for entry, expected_exit in expected_exits.items():
            curve = CurveBelt(CurveBeltConfig(direction=entry, turn="right"))
            assert curve.outputs[0].direction == expected_exit


class TestDiagonalBelt:
    """Tests for DiagonalBelt machine."""

    def test_default_config(self) -> None:
        """Default: length=4, heading=(4,8) southeast."""
        diag = DiagonalBelt()
        # 2 belts per zigzag unit
        assert len(diag.entities) == 8

    def test_entity_count(self) -> None:
        """Entity count is 2 * length."""
        for length in [1, 3, 5, 10]:
            diag = DiagonalBelt(DiagonalBeltConfig(length=length))
            assert len(diag.entities) == 2 * length

    def test_southeast_positions(self) -> None:
        """Southeast diagonal has correct zigzag positions."""
        diag = DiagonalBelt(DiagonalBeltConfig(length=2, heading=(4, 8)))
        positions = [tuple(e.position) for e in diag.entities]
        # E at (0,0), S at (1,0), E at (1,1), S at (2,1)
        assert positions == [
            (0.0, 0.0), (1.0, 0.0),
            (1.0, 1.0), (2.0, 1.0)
        ]

    def test_northeast_positions(self) -> None:
        """Northeast diagonal goes up-right."""
        diag = DiagonalBelt(DiagonalBeltConfig(length=2, heading=(4, 0)))
        positions = [tuple(e.position) for e in diag.entities]
        # E at (0,0), N at (1,0), E at (1,-1), N at (2,-1)
        assert positions == [
            (0.0, 0.0), (1.0, 0.0),
            (1.0, -1.0), (2.0, -1.0)
        ]

    def test_southwest_positions(self) -> None:
        """Southwest diagonal goes down-left."""
        diag = DiagonalBelt(DiagonalBeltConfig(length=2, heading=(12, 8)))
        positions = [tuple(e.position) for e in diag.entities]
        # W at (0,0), S at (-1,0), W at (-1,1), S at (-2,1)
        assert positions == [
            (0.0, 0.0), (-1.0, 0.0),
            (-1.0, 1.0), (-2.0, 1.0)
        ]

    def test_northwest_positions(self) -> None:
        """Northwest diagonal goes up-left."""
        diag = DiagonalBelt(DiagonalBeltConfig(length=2, heading=(0, 12)))
        positions = [tuple(e.position) for e in diag.entities]
        # N at (0,0), W at (0,-1), N at (-1,-1), W at (-1,-2)
        assert positions == [
            (0.0, 0.0), (0.0, -1.0),
            (-1.0, -1.0), (-1.0, -2.0)
        ]

    def test_alternating_directions(self) -> None:
        """Directions alternate between heading components."""
        diag = DiagonalBelt(DiagonalBeltConfig(length=3, heading=(4, 8)))
        directions = [e.direction for e in diag.entities]
        assert directions == [4, 8, 4, 8, 4, 8]

    def test_belt_tier(self) -> None:
        """Belt tier is applied to all tiles."""
        diag = DiagonalBelt(DiagonalBeltConfig(
            length=2,
            belt_tier="fast-transport-belt"
        ))
        assert all(e.name == "fast-transport-belt" for e in diag.entities)

    def test_input_connection_point(self) -> None:
        """Input is at origin with first heading direction."""
        diag = DiagonalBelt(DiagonalBeltConfig(heading=(4, 8)))
        assert diag.inputs[0].position == (0, 0)
        assert diag.inputs[0].direction == 4

    def test_output_connection_point(self) -> None:
        """Output is past last belt with second heading direction."""
        diag = DiagonalBelt(DiagonalBeltConfig(length=3, heading=(4, 8)))
        # 3 units: ends at (3, 2), output at (3, 3)
        assert diag.outputs[0].direction == 8
        assert diag.outputs[0].position == (3, 3)

    def test_invalid_heading_raises(self) -> None:
        """Non-perpendicular heading raises error."""
        with pytest.raises(ValueError, match="perpendicular"):
            DiagonalBelt(DiagonalBeltConfig(heading=(0, 8)))  # Opposite, not perpendicular

    def test_length_one(self) -> None:
        """Single zigzag unit works."""
        diag = DiagonalBelt(DiagonalBeltConfig(length=1, heading=(4, 8)))
        assert len(diag.entities) == 2
        positions = [tuple(e.position) for e in diag.entities]
        assert positions == [(0.0, 0.0), (1.0, 0.0)]


class TestBeltComposition:
    """Tests for composing belts together."""

    def test_connect_straight_belts(self) -> None:
        """Two straight belts connect end-to-end."""
        belt1 = StraightBelt(StraightBeltConfig(length=3, direction=4))
        belt2 = StraightBelt(StraightBeltConfig(length=2, direction=4))

        combined = belt1.connect_to(belt2, output="out", input="in")

        assert len(combined.entities) == 5
        positions = sorted([tuple(e.position) for e in combined.entities])
        assert positions == [
            (0.0, 0.0), (1.0, 0.0), (2.0, 0.0),  # First belt
            (3.0, 0.0), (4.0, 0.0)  # Second belt
        ]

    def test_connect_straight_to_segmented(self) -> None:
        """Straight belt connects to segmented belt."""
        straight = StraightBelt(StraightBeltConfig(length=2, direction=4))
        curved = SegmentedBelt(SegmentedBeltConfig(segments=[(2, 4), (2, 8)]))

        combined = straight.connect_to(curved, output="out", input="in")

        assert len(combined.entities) == 6

    def test_connect_preserves_directions(self) -> None:
        """Connected belts maintain their original directions."""
        belt1 = StraightBelt(StraightBeltConfig(length=2, direction=4))
        belt2 = StraightBelt(StraightBeltConfig(length=2, direction=8))

        # This creates an L-shape at the connection point
        combined = belt1.connect_to(belt2, output="out", input="in")

        directions = [e.direction for e in combined.entities]
        assert directions.count(4) == 2
        assert directions.count(8) == 2

    def test_connect_invalid_output(self) -> None:
        """Invalid output name raises error."""
        belt1 = StraightBelt(StraightBeltConfig(length=2))
        belt2 = StraightBelt(StraightBeltConfig(length=2))

        with pytest.raises(ValueError, match="Connection points not found"):
            belt1.connect_to(belt2, output="nonexistent", input="in")

    def test_connect_invalid_input(self) -> None:
        """Invalid input name raises error."""
        belt1 = StraightBelt(StraightBeltConfig(length=2))
        belt2 = StraightBelt(StraightBeltConfig(length=2))

        with pytest.raises(ValueError, match="Connection points not found"):
            belt1.connect_to(belt2, output="out", input="nonexistent")


class TestEdgeCases:
    """Edge case tests."""

    def test_very_long_belt(self) -> None:
        """Long belt creates correct number of entities."""
        belt = StraightBelt(StraightBeltConfig(length=100))
        assert len(belt.entities) == 100

    def test_many_segments(self) -> None:
        """Many small segments work correctly."""
        segments = [(1, d) for d in [4, 8, 12, 0] * 5]  # 20 segments
        belt = SegmentedBelt(SegmentedBeltConfig(segments=segments))
        assert len(belt.entities) == 20

    def test_single_tile_segments(self) -> None:
        """Each segment can be length 1."""
        belt = SegmentedBelt(SegmentedBeltConfig(
            segments=[(1, 4), (1, 8), (1, 12)]
        ))
        assert len(belt.entities) == 3
        directions = [e.direction for e in belt.entities]
        assert directions == [4, 8, 12]

    def test_box_property(self) -> None:
        """Bounding box is calculated correctly."""
        belt = StraightBelt(StraightBeltConfig(length=5, direction=4))
        box = belt.box
        # Belt from (0,0) to (4,0), each tile is 1x1
        assert box is not None

    def test_config_immutability_after_creation(self) -> None:
        """Modifying config after creation doesn't affect belt."""
        config = StraightBeltConfig(length=3, direction=4)
        belt = StraightBelt(config)

        # Modify config
        config.length = 10

        # Belt should still have 3 entities
        assert len(belt.entities) == 3
