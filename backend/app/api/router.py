import json
from pathlib import Path
from typing import Any, Mapping

from fastapi import APIRouter, HTTPException, Query

from ..core.contracts import (
    AlgorithmNotFoundError,
    CostModelError,
    Graph,
    GraphFormatError,
    NodeNotFoundError,
    RouteNotFoundError,
    ScenarioNotFoundError,
    SearchExecution,
)
from ..core.graph import GraphLoader
from ..core.paths import DATASET_MANIFEST, FIXTURES_ROOT
from ..services import SearchService
from .models import (
    CompareRequest,
    CompareResponse,
    ErrorResponse,
    LocationsResponse,
    ScenariosResponse,
    SearchRequest,
    SearchResponse,
)


router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/dataset/meta", tags=["dataset"])
def dataset_meta() -> dict[str, object]:
    """Expose dataset provenance without loading the routing graph."""
    with DATASET_MANIFEST.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def _json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_json_value(item) for item in value]
    return value


def _graph_id(path: Path) -> str:
    return path.relative_to(FIXTURES_ROOT.resolve()).as_posix()


def _load_fixture_graph(graph_id: str) -> tuple[Path, Graph]:
    fixtures_root = FIXTURES_ROOT.resolve()
    graph_path = (fixtures_root / graph_id).resolve()
    if not graph_path.is_relative_to(fixtures_root):
        raise HTTPException(status_code=404, detail="Graph folder not found")
    discovered = set(GraphLoader.discover_directories(fixtures_root))
    if graph_path not in discovered:
        raise HTTPException(status_code=404, detail="Graph folder not found or incomplete")
    try:
        return graph_path, GraphLoader.from_directory(graph_path)
    except GraphFormatError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/graphs", tags=["graph"])
def graph_catalog() -> dict[str, object]:
    """List valid graph folders below data/fixtures for the local explorer."""
    graphs = []
    invalid_graphs = []
    for path in GraphLoader.discover_directories(FIXTURES_ROOT):
        try:
            graph = GraphLoader.from_directory(path)
        except GraphFormatError as error:
            invalid_graphs.append({"graph_id": _graph_id(path), "error": str(error)})
            continue
        graphs.append(
            {
                "graph_id": _graph_id(path),
                "label": graph.metadata.get("dataset_id", _graph_id(path)),
                "data_status": graph.metadata.get("data_status", "SIMULATED"),
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges),
                "scenario_ids": [scenario.scenario_id for scenario in graph.scenarios],
            }
        )
    return {"graphs": graphs, "invalid_graphs": invalid_graphs}


@router.get(
    "/locations",
    tags=["search"],
    response_model=LocationsResponse,
    responses={404: {"model": ErrorResponse}},
)
def locations(graph_id: str = Query(default="toy_graph_v0.1")) -> dict[str, object]:
    """List selectable graph nodes for search inputs."""
    _, graph = _load_fixture_graph(graph_id)
    return {
        "graph_id": graph_id,
        "data_status": graph.metadata.get("data_status", "SIMULATED"),
        "locations": [
            {
                "node_id": node.node_id,
                "name": node.attributes.get("name", node.node_id),
                "node_type": node.attributes.get("node_type"),
                "latitude": node.latitude,
                "longitude": node.longitude,
                "data_status": node.attributes.get("data_status", "SIMULATED"),
            }
            for node in graph.nodes
        ],
    }


@router.get(
    "/scenarios",
    tags=["search"],
    response_model=ScenariosResponse,
    responses={404: {"model": ErrorResponse}},
)
def scenarios(graph_id: str = Query(default="toy_graph_v0.1")) -> dict[str, object]:
    """List scenario and cost-preset metadata for one graph."""
    _, graph = _load_fixture_graph(graph_id)
    return {
        "graph_id": graph_id,
        "data_status": graph.metadata.get("data_status", "SIMULATED"),
        "scenarios": [
            {
                "scenario_id": scenario.scenario_id,
                "traffic_scenario": scenario.data.get("traffic_scenario"),
                "cost_preset": scenario.data.get("cost_preset"),
                "weights": _json_value(scenario.data.get("weights", {})),
                "closed_edge_ids": list(scenario.closed_edge_ids),
                "data_status": scenario.data.get("data_status", "SIMULATED"),
            }
            for scenario in graph.scenarios
        ],
    }


def _search_response(execution: SearchExecution) -> dict[str, object]:
    result = execution.result
    return {
        "algorithm": execution.algorithm.value,
        "scenario": execution.scenario_id,
        "data_status": execution.data_status,
        "path": list(result.path),
        "edge_ids": list(execution.edge_ids),
        "metrics": {
            "distance_m": result.metrics.distance_m,
            "distance_km": result.metrics.distance_m / 1000,
            "estimated_time_min": result.metrics.estimated_time_min,
            "total_cost": result.metrics.total_cost,
            "explored_nodes": result.metrics.explored_nodes,
            "processing_time_ms": result.metrics.processing_time_ms,
        },
        "trace": [
            {
                "step": event.step,
                "kind": event.kind.value,
                "node_id": event.node_id,
                "parent_id": event.parent_id,
                "g_cost": event.g_cost,
                "h_cost": event.h_cost,
                "details": _json_value(event.details),
            }
            for event in result.trace
        ],
        "guarantee": result.guarantee,
        "explanation": result.explanation,
        "edge_breakdown": [
            {
                "edge_id": edge_cost.edge_id,
                "distance_km": edge_cost.distance_km,
                "travel_time_min": edge_cost.travel_time_min,
                "traffic_penalty": edge_cost.traffic_penalty,
                "flood_risk": edge_cost.flood_risk,
                "total_cost": edge_cost.total_cost,
                "is_closed": edge_cost.is_closed,
            }
            for edge_cost in execution.edge_costs
        ],
        "limitations": [
            "SIMULATED fixture; not real-world routing guidance.",
            "A_STAR currently uses h=0 and therefore behaves like UCS.",
        ],
    }


def _raise_search_http_error(error: Exception) -> None:
    message = str(error.args[0]) if error.args else str(error)
    if isinstance(error, (NodeNotFoundError, ScenarioNotFoundError, RouteNotFoundError)):
        raise HTTPException(status_code=404, detail=message) from error
    if isinstance(error, (AlgorithmNotFoundError, CostModelError, ValueError)):
        raise HTTPException(status_code=422, detail=message) from error
    raise error


@router.post(
    "/search",
    tags=["search"],
    response_model=SearchResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def search(payload: SearchRequest) -> dict[str, object]:
    """Run one validated two-point search on an immutable scenario graph."""
    _, graph = _load_fixture_graph(payload.graph_id)
    try:
        execution = SearchService(graph).search(
            start=payload.start,
            goal=payload.goal,
            algorithm=payload.algorithm,
            scenario_id=payload.scenario,
        )
    except (
        AlgorithmNotFoundError,
        CostModelError,
        NodeNotFoundError,
        RouteNotFoundError,
        ScenarioNotFoundError,
        ValueError,
    ) as error:
        _raise_search_http_error(error)
    return _search_response(execution)


@router.post(
    "/compare",
    tags=["search"],
    response_model=CompareResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def compare(payload: CompareRequest) -> dict[str, object]:
    """Run multiple registered algorithms against the exact same graph/cost input."""
    _, graph = _load_fixture_graph(payload.graph_id)
    try:
        executions = SearchService(graph).compare(
            start=payload.start,
            goal=payload.goal,
            algorithms=payload.algorithms,
            scenario_id=payload.scenario,
        )
    except (
        AlgorithmNotFoundError,
        CostModelError,
        NodeNotFoundError,
        RouteNotFoundError,
        ScenarioNotFoundError,
        ValueError,
    ) as error:
        _raise_search_http_error(error)
    return {
        "start": payload.start,
        "goal": payload.goal,
        "scenario": payload.scenario,
        "results": [_search_response(execution) for execution in executions],
    }


@router.get("/graphs/{graph_id:path}", tags=["graph"])
def graph_detail(
    graph_id: str,
    scenario_id: str | None = Query(default=None),
) -> dict[str, object]:
    """Load one discovered graph folder and serialize it for visualization."""
    _, graph = _load_fixture_graph(graph_id)
    if scenario_id is not None:
        try:
            graph.scenario(scenario_id)
        except ScenarioNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    nodes = [
        {
            "node_id": node.node_id,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "label": node.attributes.get("name", node.node_id),
            "attributes": _json_value(node.attributes),
        }
        for node in graph.nodes
    ]
    edges = [
        {
            "edge_id": edge.edge_id,
            "from_node_id": edge.from_node_id,
            "to_node_id": edge.to_node_id,
            "distance_m": edge.distance_m,
            "free_flow_time_min": edge.free_flow_time_min,
            "is_closed": (
                graph.is_edge_closed(edge.edge_id, scenario_id)
                if scenario_id is not None
                else False
            ),
            "attributes": _json_value(edge.attributes),
        }
        for edge in graph.edges
    ]
    return {
        "graph_id": graph_id,
        "directed": graph.is_directed,
        "data_status": graph.metadata.get("data_status", "SIMULATED"),
        "active_scenario_id": scenario_id,
        "metadata": _json_value(graph.metadata),
        "scenarios": [
            {
                "scenario_id": scenario.scenario_id,
                "closed_edge_ids": list(scenario.closed_edge_ids),
            }
            for scenario in graph.scenarios
        ],
        "nodes": nodes,
        "edges": edges,
        "active_edge_count": sum(not edge["is_closed"] for edge in edges),
    }
