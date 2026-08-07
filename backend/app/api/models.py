"""Pydantic request/response models exposed in OpenAPI."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    start: str = Field(min_length=1, examples=["N01"])
    goal: str = Field(min_length=1, examples=["N06"])
    algorithm: str = Field(min_length=1, examples=["A_STAR"])
    scenario: str = Field(min_length=1, examples=["HEAVY_RAIN_SAFE"])
    graph_id: str = Field(default="toy_graph_v0.1", min_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "start": "N01",
                "goal": "N06",
                "algorithm": "A_STAR",
                "scenario": "HEAVY_RAIN_SAFE",
            }
        }
    }


class CompareRequest(BaseModel):
    start: str = Field(min_length=1, examples=["N01"])
    goal: str = Field(min_length=1, examples=["N06"])
    scenario: str = Field(min_length=1, examples=["HEAVY_RAIN_SAFE"])
    algorithms: list[str] = Field(default_factory=lambda: ["UCS", "A_STAR"], min_length=1)
    graph_id: str = Field(default="toy_graph_v0.1", min_length=1)


class LocationItem(BaseModel):
    point_id: str | None = None
    node_id: str
    name: str
    node_type: str | None
    latitude: float | None
    longitude: float | None
    data_status: str


class LocationsResponse(BaseModel):
    graph_id: str
    data_status: str
    locations: list[LocationItem]


class ScenarioItem(BaseModel):
    scenario_id: str
    traffic_scenario: str | None
    cost_preset: str | None
    weights: dict[str, float]
    closed_edge_ids: list[str]
    data_status: str


class ScenariosResponse(BaseModel):
    graph_id: str
    data_status: str
    scenarios: list[ScenarioItem]


class MetricsResponse(BaseModel):
    distance_m: float
    distance_km: float
    estimated_time_min: float
    total_cost: float
    explored_nodes: int
    processing_time_ms: float


class TraceEventResponse(BaseModel):
    step: int
    kind: str
    node_id: str
    parent_id: str | None
    g_cost: float | None
    h_cost: float | None
    details: dict[str, Any]


class EdgeCostResponse(BaseModel):
    edge_id: str
    distance_km: float
    travel_time_min: float
    traffic_penalty: float
    flood_risk: float
    total_cost: float | None
    is_closed: bool


class SearchResponse(BaseModel):
    algorithm: str
    scenario: str
    data_status: str
    path: list[str]
    edge_ids: list[str]
    metrics: MetricsResponse
    trace: list[TraceEventResponse]
    guarantee: str
    explanation: str
    edge_breakdown: list[EdgeCostResponse]
    limitations: list[str]


class CompareResponse(BaseModel):
    start: str
    goal: str
    scenario: str
    results: list[SearchResponse]


class ErrorResponse(BaseModel):
    detail: str


__all__ = [
    "CompareRequest",
    "CompareResponse",
    "ErrorResponse",
    "LocationsResponse",
    "ScenariosResponse",
    "SearchRequest",
    "SearchResponse",
]
