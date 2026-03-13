"""Machine class library for compositional Factorio blueprints."""

from lib.belts import (
    CurveBelt,
    CurveBeltConfig,
    DiagonalBelt,
    DiagonalBeltConfig,
    SegmentedBelt,
    SegmentedBeltConfig,
    StraightBelt,
    StraightBeltConfig,
)
from lib.config import MachineConfig
from lib.inserters import (
    InserterBeltSegment,
    InserterBeltSegmentConfig,
    InserterSegment,
    InserterSegmentConfig,
)
from lib.machine import Machine
from lib.types import BeltPath, ConnectionPoint

__all__ = [
    "BeltPath",
    "ConnectionPoint",
    "CurveBelt",
    "CurveBeltConfig",
    "DiagonalBelt",
    "DiagonalBeltConfig",
    "InserterBeltSegment",
    "InserterBeltSegmentConfig",
    "InserterSegment",
    "InserterSegmentConfig",
    "Machine",
    "MachineConfig",
    "SegmentedBelt",
    "SegmentedBeltConfig",
    "StraightBelt",
    "StraightBeltConfig",
]
