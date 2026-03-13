"""Core type definitions for Machine composition."""

from dataclasses import dataclass


@dataclass
class ConnectionPoint:
    """A named I/O point on the machine boundary."""

    name: str
    position: tuple[float, float]
    direction: int  # 0=N, 4=E, 8=S, 12=W


@dataclass
class BeltPath:
    """A linear belt segment. Splitters break continuity into separate paths."""

    id: str
    positions: list[tuple[float, float]]  # Ordered by flow direction
    direction: int  # Overall flow direction
