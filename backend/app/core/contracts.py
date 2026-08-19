from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, TypeVar
from enum import Enum
from pydantic import BaseModel, Field


_T = TypeVar("_T")


def _freeze_value(value: Any) -> Any:
    """Return a recursively immutable representation of a model attribute."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_value(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze_value(item) for item in value)
    return value


class _ReadOnlyTuple(tuple[_T, ...]):
    """Tuple that supports both ``graph.nodes`` and ``graph.nodes()`` access."""

    def __call__(self) -> tuple[_T, ...]:
        return tuple(self)


class NodeNotFoundError(KeyError):
    """Raised when a graph query references a node that is not in the graph."""


class EdgeNotFoundError(KeyError):
    """Raised when a graph query references an edge that is not in the graph."""


class ScenarioNotFoundError(KeyError):
    """Raised when a graph query references an unknown scenario."""


class GraphFormatError(ValueError):
    """Raised when graph input violates the graph data contract."""


class CostModelError(ValueError):
    """Raised when a scenario or cost input violates the cost contract."""


class AlgorithmNotFoundError(ValueError):
    """Raised when a search request names an unsupported algorithm."""


class RouteNotFoundError(LookupError):
    """Raised when no directed path exists for the active scenario."""


@dataclass(frozen=True, slots=True)
class Node:
    """Immutable graph node with standard coordinates and extensible metadata."""

    node_id: str
    latitude: float | None = None
    longitude: float | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id.strip():
            raise GraphFormatError("Node node_id must be a non-empty string")
        object.__setattr__(self, "node_id", self.node_id.strip())
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise GraphFormatError(f"Node {self.node_id} latitude is outside [-90, 90]")
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise GraphFormatError(f"Node {self.node_id} longitude is outside [-180, 180]")
        object.__setattr__(self, "attributes", _freeze_value(dict(self.attributes)))

    @property
    def data(self) -> Mapping[str, Any]:
        """Alias for metadata consumers that use the conventional ``data`` name."""
        return self.attributes

    def __getattr__(self, name: str) -> Any:
        attributes = object.__getattribute__(self, "attributes")
        try:
            return attributes[name]
        except KeyError as error:
            raise AttributeError(name) from error


@dataclass(frozen=True, slots=True)
class Edge:
    """Immutable directed edge and its routing attributes."""

    edge_id: str
    from_node_id: str
    to_node_id: str
    distance_m: float
    free_flow_time_min: float
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("edge_id", "from_node_id", "to_node_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise GraphFormatError(f"Edge {field_name} must be a non-empty string")
            object.__setattr__(self, field_name, value.strip())
        if self.distance_m <= 0:
            raise GraphFormatError(f"Edge {self.edge_id} distance_m must be positive")
        if self.free_flow_time_min <= 0:
            raise GraphFormatError(
                f"Edge {self.edge_id} free_flow_time_min must be positive"
            )
        object.__setattr__(self, "attributes", _freeze_value(dict(self.attributes)))

    @property
    def node_id(self) -> str:
        """Target node alias useful when iterating over outgoing neighbors."""
        return self.to_node_id

    @property
    def data(self) -> Mapping[str, Any]:
        return self.attributes

    def __getattr__(self, name: str) -> Any:
        attributes = object.__getattribute__(self, "attributes")
        try:
            return attributes[name]
        except KeyError as error:
            raise AttributeError(name) from error


@dataclass(frozen=True, slots=True)
class Scenario:
    """Immutable scenario metadata, including the directed edges it closes."""

    scenario_id: str
    closed_edge_ids: tuple[str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.scenario_id, str) or not self.scenario_id.strip():
            raise GraphFormatError("Scenario scenario_id must be a non-empty string")
        object.__setattr__(self, "scenario_id", self.scenario_id.strip())
        closed_edges = tuple(sorted({str(edge_id).strip() for edge_id in self.closed_edge_ids}))
        if any(not edge_id for edge_id in closed_edges):
            raise GraphFormatError(
                f"Scenario {self.scenario_id} contains an empty closed edge id"
            )
        object.__setattr__(self, "closed_edge_ids", closed_edges)
        object.__setattr__(self, "attributes", _freeze_value(dict(self.attributes)))

    @property
    def data(self) -> Mapping[str, Any]:
        return self.attributes


_COST_COMPONENTS = ("distance", "freeflow_time", "congestion", "flood_risk")


@dataclass(frozen=True, slots=True)
class CostPreset:
    """Immutable non-negative weights used to score one edge."""

    preset_id: str
    weights: Mapping[str, float]
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.preset_id, str) or not self.preset_id.strip():
            raise CostModelError("Cost preset preset_id must be a non-empty string")
        object.__setattr__(self, "preset_id", self.preset_id.strip())
        weights = {str(key): float(value) for key, value in dict(self.weights).items()}
        missing = set(_COST_COMPONENTS) - weights.keys()
        unknown = weights.keys() - set(_COST_COMPONENTS)
        if missing:
            raise CostModelError(
                f"Cost preset {self.preset_id} is missing weights: {sorted(missing)}"
            )
        if unknown:
            raise CostModelError(
                f"Cost preset {self.preset_id} has unknown weights: {sorted(unknown)}"
            )
        if any(value < 0 for value in weights.values()):
            raise CostModelError(f"Cost preset {self.preset_id} cannot contain negative weights")
        if abs(sum(weights.values()) - 1.0) > 1e-9:
            raise CostModelError(f"Cost preset {self.preset_id} weights must sum to 1")
        object.__setattr__(self, "weights", _freeze_value(weights))


@dataclass(frozen=True, slots=True)
class EdgeCostBreakdown:
    """Reproducible metric and weighted component breakdown for one edge."""

    edge_id: str
    scenario_id: str
    cost_preset: str
    distance_km: float
    free_flow_time_min: float
    travel_time_min: float
    congestion_level_1_5: float
    traffic_penalty: float
    flood_risk: float
    weighted_components: Mapping[str, float]
    total_cost: float | None
    is_closed: bool
    data_status: str

    def __post_init__(self) -> None:
        for field_name in (
            "distance_km",
            "free_flow_time_min",
            "travel_time_min",
            "congestion_level_1_5",
            "traffic_penalty",
            "flood_risk",
        ):
            value = float(getattr(self, field_name))
            if value < 0:
                raise CostModelError(f"Edge cost {field_name} cannot be negative")
            object.__setattr__(self, field_name, value)
        if self.distance_km <= 0 or self.free_flow_time_min <= 0 or self.travel_time_min <= 0:
            raise CostModelError("Edge cost distance and time must be positive")
        if self.congestion_level_1_5 > 5:
            raise CostModelError("Edge cost congestion level must be between 0 and 5")
        if self.flood_risk > 1:
            raise CostModelError("Edge cost flood risk must be between 0 and 1")
        if self.total_cost is not None:
            total_cost = float(self.total_cost)
            if total_cost < 0:
                raise CostModelError("Edge total cost cannot be negative")
            object.__setattr__(self, "total_cost", total_cost)
        components = {str(key): float(value) for key, value in dict(self.weighted_components).items()}
        if any(value < 0 for value in components.values()):
            raise CostModelError("Weighted cost components cannot be negative")
        object.__setattr__(self, "weighted_components", _freeze_value(components))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation without exposing mutable state."""
        return {
            "edge_id": self.edge_id,
            "scenario_id": self.scenario_id,
            "cost_preset": self.cost_preset,
            "distance_km": self.distance_km,
            "free_flow_time_min": self.free_flow_time_min,
            "travel_time_min": self.travel_time_min,
            "congestion_level_1_5": self.congestion_level_1_5,
            "traffic_penalty": self.traffic_penalty,
            "flood_risk": self.flood_risk,
            "weighted_components": dict(self.weighted_components),
            "total_cost": self.total_cost,
            "is_closed": self.is_closed,
            "data_status": self.data_status,
        }


@dataclass(frozen=True, slots=True)
class RouteCostBreakdown:
    """Aggregate cost breakdown whose total is the sum of open edge costs."""

    scenario_id: str
    edge_costs: tuple[EdgeCostBreakdown, ...]
    total_cost: float | None
    is_available: bool
    data_status: str

    def __post_init__(self) -> None:
        if any(not isinstance(edge_cost, EdgeCostBreakdown) for edge_cost in self.edge_costs):
            raise TypeError("Route edge_costs must contain EdgeCostBreakdown values")
        if self.total_cost is not None and self.total_cost < 0:
            raise CostModelError("Route total cost cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "edges": [edge_cost.to_dict() for edge_cost in self.edge_costs],
            "total_cost": self.total_cost,
            "is_available": self.is_available,
            "data_status": self.data_status,
        }


class Graph:
    """Immutable directed graph contract shared by loaders and algorithms.

    ``nodes`` and ``edges`` are read-only tuple views. ``neighbors`` returns
    outgoing directed edges, while ``neighbor_nodes`` returns the corresponding
    node models. A scenario is applied as a view, so the base graph is unchanged.
    """

    __slots__ = (
        "_nodes",
        "_edges",
        "_node_by_id",
        "_edge_by_id",
        "_outgoing",
        "_scenarios",
        "_scenario_by_id",
        "_metadata",
        "_directed",
        "_locked",
    )

    def __init__(
        self,
        nodes: Iterable[Node],
        edges: Iterable[Edge],
        scenarios: Iterable[Scenario] = (),
        *,
        metadata: Mapping[str, Any] | None = None,
        directed: bool = True,
    ) -> None:
        if not directed:
            raise GraphFormatError("Graph loader supports directed graphs only")

        node_values = tuple(nodes)
        edge_values = tuple(edges)
        scenario_values = tuple(scenarios)
        node_by_id: dict[str, Node] = {}
        for node in node_values:
            if not isinstance(node, Node):
                raise TypeError("Graph nodes must be Node instances")
            if node.node_id in node_by_id:
                raise GraphFormatError(f"Duplicate node_id: {node.node_id}")
            node_by_id[node.node_id] = node

        edge_by_id: dict[str, Edge] = {}
        outgoing: dict[str, list[Edge]] = {node_id: [] for node_id in node_by_id}
        for edge in edge_values:
            if not isinstance(edge, Edge):
                raise TypeError("Graph edges must be Edge instances")
            if edge.edge_id in edge_by_id:
                raise GraphFormatError(f"Duplicate edge_id: {edge.edge_id}")
            if edge.from_node_id not in node_by_id or edge.to_node_id not in node_by_id:
                raise GraphFormatError(
                    f"Edge {edge.edge_id} references a missing node: "
                    f"{edge.from_node_id}->{edge.to_node_id}"
                )
            edge_by_id[edge.edge_id] = edge
            outgoing[edge.from_node_id].append(edge)

        scenario_by_id: dict[str, Scenario] = {}
        for scenario in scenario_values:
            if not isinstance(scenario, Scenario):
                raise TypeError("Graph scenarios must be Scenario instances")
            if scenario.scenario_id in scenario_by_id:
                raise GraphFormatError(f"Duplicate scenario_id: {scenario.scenario_id}")
            unknown_edges = set(scenario.closed_edge_ids) - edge_by_id.keys()
            if unknown_edges:
                raise GraphFormatError(
                    f"Scenario {scenario.scenario_id} closes missing edges: "
                    f"{sorted(unknown_edges)}"
                )
            scenario_by_id[scenario.scenario_id] = scenario

        sorted_nodes = tuple(sorted(node_values, key=lambda node: node.node_id))
        sorted_edges = tuple(
            sorted(edge_values, key=lambda edge: (edge.from_node_id, edge.to_node_id, edge.edge_id))
        )
        sorted_outgoing = {
            node_id: tuple(sorted(edges_for_node, key=lambda edge: (edge.to_node_id, edge.edge_id)))
            for node_id, edges_for_node in outgoing.items()
        }

        object.__setattr__(self, "_nodes", _ReadOnlyTuple(sorted_nodes))
        object.__setattr__(self, "_edges", _ReadOnlyTuple(sorted_edges))
        object.__setattr__(self, "_node_by_id", MappingProxyType(dict(node_by_id)))
        object.__setattr__(self, "_edge_by_id", MappingProxyType(dict(edge_by_id)))
        object.__setattr__(self, "_outgoing", MappingProxyType(sorted_outgoing))
        sorted_scenarios = tuple(sorted(scenario_values, key=lambda scenario: scenario.scenario_id))
        object.__setattr__(self, "_scenarios", _ReadOnlyTuple(sorted_scenarios))
        object.__setattr__(self, "_scenario_by_id", MappingProxyType(dict(scenario_by_id)))
        object.__setattr__(self, "_metadata", _freeze_value(dict(metadata or {})))
        object.__setattr__(self, "_directed", True)
        object.__setattr__(self, "_locked", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_locked", False):
            raise AttributeError("Graph is immutable")
        object.__setattr__(self, name, value)

    @property
    def directed(self) -> bool:
        return self._directed

    @property
    def is_directed(self) -> bool:
        return self._directed

    @property
    def nodes(self) -> tuple[Node, ...]:
        return self._nodes

    @property
    def edges(self) -> tuple[Edge, ...]:
        return self._edges

    @property
    def scenarios(self) -> tuple[Scenario, ...]:
        return self._scenarios

    @property
    def metadata(self) -> Mapping[str, Any]:
        return self._metadata

    def list_nodes(self) -> tuple[Node, ...]:
        return tuple(self._nodes)

    def list_edges(self, scenario_id: str | None = None) -> tuple[Edge, ...]:
        closed_edge_ids = self._closed_edge_ids(scenario_id)
        return tuple(edge for edge in self._edges if edge.edge_id not in closed_edge_ids)

    def has_node(self, node_id: str) -> bool:
        return node_id in self._node_by_id

    def get_node(self, node_id: str) -> Node:
        try:
            return self._node_by_id[node_id]
        except KeyError as error:
            raise NodeNotFoundError(f"Unknown node: {node_id}") from error

    def node(self, node_id: str) -> Node:
        return self.get_node(node_id)

    def node_exists(self, node_id: str) -> bool:
        return self.has_node(node_id)

    def neighbors(self, node_id: str, scenario_id: str | None = None) -> tuple[Edge, ...]:
        self.get_node(node_id)
        closed_edge_ids = self._closed_edge_ids(scenario_id)
        return tuple(
            edge for edge in self._outgoing[node_id] if edge.edge_id not in closed_edge_ids
        )

    def outgoing_edges(self, node_id: str, scenario_id: str | None = None) -> tuple[Edge, ...]:
        return self.neighbors(node_id, scenario_id)

    def get_neighbors(self, node_id: str, scenario_id: str | None = None) -> tuple[Edge, ...]:
        return self.neighbors(node_id, scenario_id)

    def neighbor_nodes(self, node_id: str, scenario_id: str | None = None) -> tuple[Node, ...]:
        return tuple(
            self.get_node(edge.to_node_id)
            for edge in self.neighbors(node_id, scenario_id)
        )

    def neighbor_ids(self, node_id: str, scenario_id: str | None = None) -> tuple[str, ...]:
        return tuple(edge.to_node_id for edge in self.neighbors(node_id, scenario_id))

    def has_edge(self, edge_id: str, scenario_id: str | None = None) -> bool:
        return edge_id in self._edge_by_id and edge_id not in self._closed_edge_ids(scenario_id)

    def edge_exists(
        self,
        from_node_id: str,
        to_node_id: str,
        scenario_id: str | None = None,
    ) -> bool:
        return any(
            edge.to_node_id == to_node_id
            for edge in self.neighbors(from_node_id, scenario_id)
        )

    def get_edge(self, edge_id: str, scenario_id: str | None = None) -> Edge:
        try:
            edge = self._edge_by_id[edge_id]
        except KeyError as error:
            raise EdgeNotFoundError(f"Unknown edge: {edge_id}") from error
        if edge.edge_id in self._closed_edge_ids(scenario_id):
            raise EdgeNotFoundError(f"Edge {edge_id} is closed in scenario {scenario_id}")
        return edge

    def is_edge_closed(self, edge_id: str, scenario_id: str) -> bool:
        if edge_id not in self._edge_by_id:
            raise EdgeNotFoundError(f"Unknown edge: {edge_id}")
        return edge_id in self._closed_edge_ids(scenario_id)

    def is_edge_open(self, edge_id: str, scenario_id: str) -> bool:
        return not self.is_edge_closed(edge_id, scenario_id)

    def scenario(self, scenario_id: str) -> Scenario:
        try:
            return self._scenario_by_id[scenario_id]
        except KeyError as error:
            raise ScenarioNotFoundError(f"Unknown scenario: {scenario_id}") from error

    def for_scenario(self, scenario_id: str) -> "GraphView":
        self.scenario(scenario_id)
        return GraphView(self, scenario_id)

    def has_cycle(self, scenario_id: str | None = None) -> bool:
        """Return whether the active directed graph contains a cycle."""
        indegree = {node.node_id: 0 for node in self._nodes}
        for edge in self.list_edges(scenario_id):
            indegree[edge.to_node_id] += 1

        ready = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
        visited = 0
        while ready:
            node_id = ready.popleft()
            visited += 1
            for edge in self.neighbors(node_id, scenario_id):
                indegree[edge.to_node_id] -= 1
                if indegree[edge.to_node_id] == 0:
                    ready.append(edge.to_node_id)
        return visited != len(self._nodes)

    def is_cyclic(self, scenario_id: str | None = None) -> bool:
        return self.has_cycle(scenario_id)

    def contains_cycle(self, scenario_id: str | None = None) -> bool:
        return self.has_cycle(scenario_id)

    def _closed_edge_ids(self, scenario_id: str | None) -> frozenset[str]:
        if scenario_id is None:
            return frozenset()
        return frozenset(self.scenario(scenario_id).closed_edge_ids)

    @classmethod
    def from_csv(cls, nodes_path: str, edges_path: str, scenarios_path: str | None = None) -> "Graph":
        from .graph import GraphLoader

        return GraphLoader.from_csv(nodes_path, edges_path, scenarios_path)

    @classmethod
    def from_json(cls, graph_path: str, scenarios_path: str | None = None) -> "Graph":
        from .graph import GraphLoader

        return GraphLoader.from_json(graph_path, scenarios_path)

    @classmethod
    def from_directory(cls, directory: str) -> "Graph":
        from .graph import GraphLoader

        return GraphLoader.from_directory(directory)

    from_fixture = from_directory


class GraphView:
    """Read-only scenario view over a :class:`Graph`."""

    __slots__ = ("_graph", "_scenario_id", "_locked")

    def __init__(self, graph: Graph, scenario_id: str) -> None:
        object.__setattr__(self, "_graph", graph)
        object.__setattr__(self, "_scenario_id", scenario_id)
        object.__setattr__(self, "_locked", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_locked", False):
            raise AttributeError("GraphView is immutable")
        object.__setattr__(self, name, value)

    @property
    def graph(self) -> Graph:
        return self._graph

    @property
    def base_graph(self) -> Graph:
        return self._graph

    @property
    def scenario_id(self) -> str:
        return self._scenario_id

    @property
    def nodes(self) -> tuple[Node, ...]:
        return self._graph.nodes

    @property
    def edges(self) -> tuple[Edge, ...]:
        return _ReadOnlyTuple(self._graph.list_edges(self._scenario_id))

    @property
    def directed(self) -> bool:
        return self._graph.directed

    @property
    def is_directed(self) -> bool:
        return self._graph.is_directed

    def list_nodes(self) -> tuple[Node, ...]:
        return self._graph.list_nodes()

    def list_edges(self) -> tuple[Edge, ...]:
        return self._graph.list_edges(self._scenario_id)

    def has_node(self, node_id: str) -> bool:
        return self._graph.has_node(node_id)

    def get_node(self, node_id: str) -> Node:
        return self._graph.get_node(node_id)

    def node(self, node_id: str) -> Node:
        return self.get_node(node_id)

    def node_exists(self, node_id: str) -> bool:
        return self.has_node(node_id)

    def neighbors(self, node_id: str) -> tuple[Edge, ...]:
        return self._graph.neighbors(node_id, self._scenario_id)

    def outgoing_edges(self, node_id: str) -> tuple[Edge, ...]:
        return self.neighbors(node_id)

    def get_neighbors(self, node_id: str) -> tuple[Edge, ...]:
        return self.neighbors(node_id)

    def neighbor_nodes(self, node_id: str) -> tuple[Node, ...]:
        return self._graph.neighbor_nodes(node_id, self._scenario_id)

    def neighbor_ids(self, node_id: str) -> tuple[str, ...]:
        return self._graph.neighbor_ids(node_id, self._scenario_id)

    def has_edge(self, edge_id: str) -> bool:
        return self._graph.has_edge(edge_id, self._scenario_id)

    def edge_exists(self, from_node_id: str, to_node_id: str) -> bool:
        return self._graph.edge_exists(from_node_id, to_node_id, self._scenario_id)

    def get_edge(self, edge_id: str) -> Edge:
        return self._graph.get_edge(edge_id, self._scenario_id)

    def is_edge_closed(self, edge_id: str) -> bool:
        return self._graph.is_edge_closed(edge_id, self._scenario_id)

    def is_edge_open(self, edge_id: str) -> bool:
        return self._graph.is_edge_open(edge_id, self._scenario_id)

    def has_cycle(self) -> bool:
        return self._graph.has_cycle(self._scenario_id)

    def contains_cycle(self) -> bool:
        return self.has_cycle()


class TraceEventKind(StrEnum):
    OPEN = "OPEN"
    EXPAND = "EXPAND"
    RELAX = "RELAX"
    CLOSE = "CLOSE"
    GOAL = "GOAL"
    FAIL = "FAIL"


class AlgorithmName(StrEnum):
    UCS = "UCS"
    A_STAR = "A_STAR"
    BFS = "BFS"
    DFS = "DFS"
    GREEDY = "GREEDY"
    BIDIRECTIONAL = "BIDIRECTIONAL"


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
class SearchPath:
    """Framework-independent path/trace output produced by a search algorithm."""

    path: tuple[str, ...]
    edge_ids: tuple[str, ...]
    trace: tuple[TraceEvent, ...]
    explored_nodes: int
    guarantee: str

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("SearchPath path cannot be empty")
        if len(self.edge_ids) != len(self.path) - 1:
            raise ValueError("SearchPath edge_ids must connect every consecutive node")
        if self.explored_nodes < 0:
            raise ValueError("SearchPath explored_nodes cannot be negative")


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


@dataclass(frozen=True, slots=True)
class SearchExecution:
    """SearchResult plus request identity and edge-level provenance."""

    algorithm: AlgorithmName
    scenario_id: str
    edge_ids: tuple[str, ...]
    edge_costs: tuple[EdgeCostBreakdown, ...]
    result: SearchResult
    data_status: str

class AffectedEdgeStatus(str, Enum):
    CONGESTED = "CONGESTED"
    FLOODED = "FLOODED"
    CLOSED = "CLOSED"

class AffectedEdge(BaseModel):
    edge_id: str
    status: AffectedEdgeStatus

class RandomScenarioRequest(BaseModel):
    start_node_id: str
    goal_node_id: str
    seed: str | None = Field(
        default=None, 
        description="Seed used for reproducible pseudo-random generation."
    )
    num_edges: int = Field(
        default=5, 
        ge=1, 
        le=15, 
        description="Number of edges to randomly affect."
    )

class RandomScenarioResponse(BaseModel):
    scenario_id: str
    affected_edges: list[AffectedEdge]