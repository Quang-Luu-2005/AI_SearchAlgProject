import json
import csv
from pathlib import Path
from typing import Any, Mapping

from fastapi import APIRouter, HTTPException, Query

from ..core.contracts import (
    AlgorithmNotFoundError,
    CostModelError,
    Graph,
    GraphFormatError,
    Node,
    NodeNotFoundError,
    RouteNotFoundError,
    ScenarioNotFoundError,
    SearchExecution,
)
from ..core.graph import GraphLoader
from ..core.paths import DATASET_MANIFEST, FIXTURES_ROOT, PROCESSED_ROOT, THU_DUC_BOUNDARY
from ..optimization import TourOptimizerService
from ..services import SearchService
from .models import (
    CompareRequest,
    CompareResponse,
    ErrorResponse,
    LocationsResponse,
    OptimizeTourRequest,
    OptimizeTourResponse,
    ScenariosResponse,
    SearchRequest,
    SearchResponse,
    RandomScenarioRequest,
    RandomScenarioResponse,
)

from ..services.random_scenario import RandomScenarioService

router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/dataset/meta", tags=["dataset"])
def dataset_meta() -> dict[str, object]:
    """Expose dataset provenance without loading the routing graph."""
    with DATASET_MANIFEST.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


@router.get("/boundaries/thu-duc", tags=["dataset"])
def thu_duc_boundary() -> dict[str, object]:
    """Return the frozen historic OSM boundary used as Thu Duc study context."""
    with THU_DUC_BOUNDARY.open(encoding="utf-8") as boundary_file:
        return json.load(boundary_file)


def _json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_json_value(item) for item in value]
    return value


def _graph_id(path: Path, dataset_kind: str) -> str:
    root = FIXTURES_ROOT if dataset_kind == "fixture" else PROCESSED_ROOT
    relative_id = path.relative_to(root.resolve()).as_posix()
    return relative_id if dataset_kind == "fixture" else f"processed/{relative_id}"


def _load_graph(graph_id: str) -> tuple[Path, Graph, str]:
    if graph_id.startswith("processed/"):
        dataset_kind = "processed"
        root = PROCESSED_ROOT.resolve()
        relative_id = graph_id.removeprefix("processed/")
    else:
        dataset_kind = "fixture"
        root = FIXTURES_ROOT.resolve()
        relative_id = graph_id
    graph_path = (root / relative_id).resolve()
    if not graph_path.is_relative_to(root):
        raise HTTPException(status_code=404, detail="Graph folder not found")
    discovered = set(GraphLoader.discover_directories(root))
    if graph_path not in discovered:
        raise HTTPException(status_code=404, detail="Graph folder not found or incomplete")
    try:
        return graph_path, GraphLoader.from_directory(graph_path), dataset_kind
    except GraphFormatError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/graphs", tags=["graph"])
def graph_catalog() -> dict[str, object]:
    """List valid fixture and processed graph folders for the local explorer."""
    graphs = []
    invalid_graphs = []
    for root, dataset_kind in ((FIXTURES_ROOT, "fixture"), (PROCESSED_ROOT, "processed")):
        for path in GraphLoader.discover_directories(root):
            graph_id = _graph_id(path, dataset_kind)
            try:
                graph = GraphLoader.from_directory(path)
            except GraphFormatError as error:
                invalid_graphs.append({"graph_id": graph_id, "error": str(error)})
                continue
            graphs.append(
                {
                    "graph_id": graph_id,
                    "label": graph.metadata.get("label", graph.metadata.get("dataset_id", graph_id)),
                    "data_status": graph.metadata.get("data_status", "SIMULATED"),
                    "dataset_kind": dataset_kind,
                    "snapshot_date": graph.metadata.get("snapshot_date"),
                    "real_time": graph.metadata.get("real_time", False),
                    "source_ids": list(graph.metadata.get("source_ids", [])),
                    "limitations": list(graph.metadata.get("limitations", [])),
                    "routing_dataset_status": graph.metadata.get("routing_dataset_status"),
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
    graph_path, graph, dataset_kind = _load_graph(graph_id)
    incident_roads: dict[str, set[str]] = {node.node_id: set() for node in graph.nodes}
    for edge in graph.edges:
        road_name = str(edge.attributes.get("road_name") or "").strip()
        if not road_name:
            continue
        incident_roads[edge.from_node_id].add(road_name)
        incident_roads[edge.to_node_id].add(road_name)

    def topology_name(node: Node) -> str:
        node_id = node.node_id
        raw_name = str(node.attributes.get("name") or "").strip()
        if raw_name and raw_name != node_id and not raw_name.casefold().startswith("utraffic node "):
            return raw_name
        roads = sorted(incident_roads[node_id])
        if len(roads) >= 2:
            return f"Giao {' × '.join(roads[:3])}"
        if roads:
            return f"Nút trên {roads[0]}"
        if node.latitude is not None and node.longitude is not None:
            return f"Node tại {node.latitude:.5f}, {node.longitude:.5f}"
        return node_id

    if dataset_kind == "processed" and (graph_path / "delivery_points.csv").is_file():
        with (graph_path / "delivery_points.csv").open(encoding="utf-8", newline="") as file:
            point_rows = [
                row for row in csv.DictReader(file)
                if row.get("selected_for_demo", "").casefold() == "true"
            ]
        points_by_node: dict[str, list[dict[str, str]]] = {}
        for row in point_rows:
            points_by_node.setdefault(row["snap_node_id"], []).append(row)
        nodes_by_id = {node.node_id: node for node in graph.nodes}
        ordered_node_ids = list(points_by_node)
        ordered_node_ids.extend(
            node_id for node_id in sorted(nodes_by_id) if node_id not in points_by_node
        )
        location_rows = [
            {
                "point_id": points_by_node[node_id][0]["point_id"] if node_id in points_by_node else None,
                "node_id": node_id,
                "name": (
                    " / ".join(dict.fromkeys(row["name"] for row in points_by_node[node_id]))
                    if node_id in points_by_node
                    else topology_name(nodes_by_id[node_id])
                ),
                "node_type": (
                    points_by_node[node_id][0]["point_type"]
                    if node_id in points_by_node
                    else nodes_by_id[node_id].attributes.get("node_type")
                ),
                "latitude": nodes_by_id[node_id].latitude,
                "longitude": nodes_by_id[node_id].longitude,
                "data_status": (
                    points_by_node[node_id][0]["location_data_status"]
                    if node_id in points_by_node
                    else nodes_by_id[node_id].attributes.get("data_status", "SOURCE_BACKED")
                ),
            }
            for node_id in ordered_node_ids
        ]
    else:
        location_rows = [
            {
                "point_id": None,
                "node_id": node.node_id,
                "name": topology_name(node),
                "node_type": node.attributes.get("node_type"),
                "latitude": node.latitude,
                "longitude": node.longitude,
                "data_status": node.attributes.get("data_status", "SIMULATED"),
            }
            for node in graph.nodes
        ]
    return {
        "graph_id": graph_id,
        "data_status": graph.metadata.get("data_status", "SIMULATED"),
        "locations": location_rows,
    }


@router.get(
    "/scenarios",
    tags=["search"],
    response_model=ScenariosResponse,
    responses={404: {"model": ErrorResponse}},
)
def scenarios(graph_id: str = Query(default="toy_graph_v0.1")) -> dict[str, object]:
    """List scenario and cost-preset metadata for one graph."""
    _, graph, _ = _load_graph(graph_id)
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


def _search_response(execution: SearchExecution, graph: Graph) -> dict[str, object]:
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
        "limitations": list(graph.metadata.get("limitations", [])),
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
    _, graph, _ = _load_graph(payload.graph_id)
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
    return _search_response(execution, graph)


@router.post(
    "/compare",
    tags=["search"],
    response_model=CompareResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def compare(payload: CompareRequest) -> dict[str, object]:
    """Run multiple registered algorithms against the exact same graph/cost input."""
    _, graph, _ = _load_graph(payload.graph_id)
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
        "results": [_search_response(execution, graph) for execution in executions],
    }


@router.post(
    "/optimize-tour",
    tags=["optimization"],
    response_model=OptimizeTourResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def optimize_tour(payload: OptimizeTourRequest) -> dict[str, object]:
    """Optimize 5-10 unique delivery stops using Held-Karp DP or Nearest Neighbor."""
    _, graph, limitations = _load_graph(payload.graph_id)
    try:
        service = TourOptimizerService(graph)
        res = service.optimize_tour(
            depot=payload.depot,
            stops=payload.stops,
            scenario_id=payload.scenario,
            algorithm=payload.algorithm,
            tour_algorithm=payload.tour_algorithm,
            return_to_depot=payload.return_to_depot,
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

    res_dict = res.to_dict()
    res_dict["scenario"] = payload.scenario
    res_dict["limitations"] = list(graph.metadata.get("limitations", []))
    return res_dict


@router.get("/graphs/{graph_id:path}", tags=["graph"])
def graph_detail(
    graph_id: str,
    scenario_id: str | None = Query(default=None),
) -> dict[str, object]:
    """Load one discovered graph folder and serialize it for visualization."""
    _, graph, _ = _load_graph(graph_id)
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

@router.post(
    "/scenarios/random",
    tags=["search"],
    response_model=RandomScenarioResponse,
    responses={422: {"model": ErrorResponse}},
)
def generate_random_scenario(payload: RandomScenarioRequest) -> dict[str, object]:
    """Sinh kịch bản giao thông ngẫu nhiên, đảm bảo vẫn còn đường đi tới đích."""
    _, graph, _ = _load_graph(payload.graph_id)
    
    try:
        service = RandomScenarioService(base_graph=graph)
        response = service.generate(
            start=payload.start_node_id,
            goal=payload.goal_node_id,
            num_edges=payload.num_edges,
            seed=payload.seed
        )
        return response.model_dump()
        
    except RouteNotFoundError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
