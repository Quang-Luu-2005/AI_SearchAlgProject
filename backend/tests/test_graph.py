import json
from pathlib import Path

import pytest

from backend.app.core.contracts import (
    Edge,
    EdgeNotFoundError,
    Graph,
    GraphFormatError,
    Node,
    NodeNotFoundError,
)
from backend.app.core.graph import GraphLoader


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "toy_graph_v0.1"


def test_loader_reads_six_node_directed_fixture_and_sorts_neighbors() -> None:
    graph = GraphLoader.from_fixture(FIXTURE_DIR)

    assert isinstance(graph, Graph)
    assert isinstance(graph.get_node("N01"), Node)
    assert isinstance(graph.get_edge("E01"), Edge)
    assert len(graph.nodes) == 6
    assert len(graph.edges) == 14
    assert graph.nodes() == graph.list_nodes()
    assert graph.is_directed
    assert graph.has_node("N01")
    assert not graph.has_node("MISSING")
    assert graph.neighbor_ids("N01") == ("N02", "N03")
    assert tuple(node.node_id for node in graph.neighbor_nodes("N01")) == ("N02", "N03")
    assert tuple(edge.edge_id for edge in graph.neighbors("N01")) == ("E01", "E05")


def test_missing_node_is_explicit_and_does_not_fall_back_to_empty_neighbors() -> None:
    graph = GraphLoader.from_directory(FIXTURE_DIR)

    with pytest.raises(NodeNotFoundError, match="MISSING"):
        graph.neighbors("MISSING")
    with pytest.raises(KeyError):
        graph.get_node("MISSING")


def test_scenario_closes_edges_in_view_without_mutating_original_graph() -> None:
    graph = GraphLoader.from_directory(FIXTURE_DIR)
    rainy_graph = graph.for_scenario("HEAVY_RAIN_SAFE")

    assert graph.has_edge("E03")
    assert not rainy_graph.has_edge("E03")
    assert graph.is_edge_closed("E03", "HEAVY_RAIN_SAFE")
    assert not graph.is_edge_closed("E03", "OFFPEAK_BALANCED")
    assert graph.neighbor_ids("N02") == ("N01", "N04", "N06")
    assert rainy_graph.neighbor_ids("N02") == ("N01", "N04")
    assert tuple(edge.edge_id for edge in graph.list_edges()) == tuple(
        edge.edge_id for edge in graph.edges
    )
    with pytest.raises(EdgeNotFoundError, match="closed"):
        rainy_graph.get_edge("E03")


def test_json_loader_preserves_one_way_direction_and_detects_cycle(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "dataset_version": "test-1",
                "data_status": "SIMULATED",
                "nodes": [
                    {"node_id": "A", "latitude": 10.0, "longitude": 106.0, "source_id": "SIM"},
                    {"node_id": "B", "latitude": 10.1, "longitude": 106.1, "source_id": "SIM"},
                    {"node_id": "C", "latitude": 10.2, "longitude": 106.2, "source_id": "SIM"},
                ],
                "edges": [
                    {
                        "edge_id": "AB",
                        "from_node_id": "A",
                        "to_node_id": "B",
                        "distance_m": 1,
                        "free_flow_time_min": 1,
                        "direction": "one-way",
                    },
                    {
                        "edge_id": "BC",
                        "from_node_id": "B",
                        "to_node_id": "C",
                        "distance_m": 1,
                        "free_flow_time_min": 1,
                        "direction": "one-way",
                    },
                    {
                        "edge_id": "CA",
                        "from_node_id": "C",
                        "to_node_id": "A",
                        "distance_m": 1,
                        "free_flow_time_min": 1,
                        "direction": "one-way",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    graph = GraphLoader.from_json(graph_path)

    assert graph.edge_exists("A", "B")
    assert not graph.edge_exists("B", "A")
    assert graph.neighbor_ids("B") == ("C",)
    assert graph.has_cycle()


def test_graph_attributes_are_immutable_and_acyclic_graph_is_detected(tmp_path: Path) -> None:
    graph_path = tmp_path / "acyclic.json"
    graph_path.write_text(
        json.dumps(
            {
                "nodes": [
                    {"node_id": "A", "source_id": "SIM"},
                    {"node_id": "B", "source_id": "SIM"},
                ],
                "edges": [
                    {
                        "edge_id": "AB",
                        "from_node_id": "A",
                        "to_node_id": "B",
                        "distance_m": 1,
                        "free_flow_time_min": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    graph = GraphLoader.from_json(graph_path)

    assert not graph.has_cycle()
    with pytest.raises(AttributeError, match="immutable"):
        graph.nodes = ()  # type: ignore[misc]
    with pytest.raises(TypeError):
        graph.nodes[0].attributes["source_id"] = "CHANGED"  # type: ignore[index]


def test_invalid_scenario_edge_reference_is_rejected(tmp_path: Path) -> None:
    graph_path = tmp_path / "invalid.json"
    graph_path.write_text(
        json.dumps(
            {
                "nodes": [{"node_id": "A"}],
                "edges": [],
                "scenarios": [{"scenario_id": "BROKEN", "closed_edge_ids": ["MISSING"]}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(GraphFormatError, match="MISSING"):
        GraphLoader.from_json(graph_path)
