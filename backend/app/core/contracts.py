from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class TraceEventKind(StrEnum):
    OPEN = "OPEN"
    EXPAND = "EXPAND"
    RELAX = "RELAX"
    CLOSE = "CLOSE"
    GOAL = "GOAL"
    FAIL = "FAIL"


@dataclass(frozen=True, slots=True)
class TraceEvent:
    step: int
    kind: TraceEventKind
    node_id: str
    parent_id: str | None = None
    g_cost: float | None = None
    h_cost: float | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RouteMetrics:
    distance_m: float
    estimated_time_min: float
    total_cost: float
    explored_nodes: int
    processing_time_ms: float


@dataclass(frozen=True, slots=True)
class SearchResult:
    path: tuple[str, ...]
    metrics: RouteMetrics
    trace: tuple[TraceEvent, ...]
    guarantee: str
    explanation: str

