import json
from pathlib import Path
from typing import Any, Mapping

from fastapi import APIRouter, HTTPException, Query

from ..core.contracts import Graph, GraphFormatError, ScenarioNotFoundError
from ..core.graph import GraphLoader
from ..core.paths import DATASET_MANIFEST, FIXTURES_ROOT


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
