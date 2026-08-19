from pathlib import Path

import pytest

from backend.app.core.contracts import Graph, RouteNotFoundError, Scenario
from backend.app.core.graph import GraphLoader
from backend.app.services import SearchService


DATASET_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "thu_duc_landmarks_v1.0.4"
)
ALGORITHMS = ("BFS", "DFS", "UCS", "A_STAR", "GREEDY", "BIDIRECTIONAL")


@pytest.fixture(scope="module")
def service() -> SearchService:
    return SearchService(GraphLoader.from_directory(DATASET_DIR))


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_hard_closure_is_respected_by_all_algorithms(
    service: SearchService, algorithm: str
) -> None:
    execution = service.search(
        start="LM_001",
        goal="LM_036",
        algorithm=algorithm,
        scenario_id="LANDMARK_HARD_CLOSURE_DETOUR",
    )

    assert "LM_EDGE_0001" not in execution.edge_ids
    assert execution.result.path[0] == "LM_001"
    assert execution.result.path[-1] == "LM_036"


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_edge_override_closure_is_respected_by_all_algorithms(
    service: SearchService, algorithm: str
) -> None:
    original = service.graph
    override_scenario = Scenario(
        scenario_id="TEST_OVERRIDE_CLOSURE",
        attributes={
            "cost_preset": "BALANCED",
            "weights": {
                "distance": 0.25,
                "freeflow_time": 0.3,
                "congestion": 0.2,
                "flood_risk": 0.25,
            },
            "edge_overrides": {"LM_EDGE_0001": {"is_closed": True}},
        },
    )
    override_service = SearchService(
        Graph(
            nodes=original.nodes,
            edges=original.edges,
            scenarios=tuple(original.scenarios) + (override_scenario,),
            metadata=original.metadata,
        )
    )

    execution = override_service.search(
        start="LM_001",
        goal="LM_036",
        algorithm=algorithm,
        scenario_id="TEST_OVERRIDE_CLOSURE",
    )
    assert "LM_EDGE_0001" not in execution.edge_ids


def test_hard_closure_returns_no_route_when_all_start_edges_are_closed(
    service: SearchService,
) -> None:
    original = service.graph
    outgoing = tuple(edge.edge_id for edge in original.neighbors("LM_001"))
    lockdown = Scenario(
        scenario_id="TEST_NO_ROUTE_LOCKDOWN",
        closed_edge_ids=outgoing,
        attributes={
            "cost_preset": "BALANCED",
            "weights": {
                "distance": 0.25,
                "freeflow_time": 0.3,
                "congestion": 0.2,
                "flood_risk": 0.25,
            },
        },
    )
    lockdown_service = SearchService(
        Graph(
            nodes=original.nodes,
            edges=original.edges,
            scenarios=tuple(original.scenarios) + (lockdown,),
            metadata=original.metadata,
        )
    )

    for algorithm in ALGORITHMS:
        with pytest.raises(RouteNotFoundError):
            lockdown_service.search(
                start="LM_001",
                goal="LM_036",
                algorithm=algorithm,
                scenario_id="TEST_NO_ROUTE_LOCKDOWN",
            )


def test_alternatives_use_the_same_algorithm_and_distinct_edges(
    service: SearchService,
) -> None:
    routes = service.alternatives(
        start="LM_001",
        goal="LM_036",
        algorithm="A_STAR",
        scenario_id="LANDMARK_FLOOD",
        limit=2,
    )

    assert 1 <= len(routes) <= 3
    assert {route.algorithm.value for route in routes} == {"A_STAR"}
    assert len({route.edge_ids for route in routes}) == len(routes)
    assert routes[0].result.metrics.total_cost <= routes[-1].result.metrics.total_cost
