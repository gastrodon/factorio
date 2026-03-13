"""Machine configuration dataclasses."""

from dataclasses import dataclass


@dataclass
class MachineConfig:
    """Base config - subclass for specific machines."""

    belt_tier: str = "transport-belt"
    inserter_tier: str = "inserter"
