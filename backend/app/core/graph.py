"""Graph loading from the versioned CSV/JSON data contracts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .contracts import (
    Edge,
    Graph,
    GraphFormatError,
    Node,
    Scenario,
)


PathLike = str | Path


def _required_text(record: Mapping[str, Any], field_name: str, record_type: str) -> str:
    value = record.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise GraphFormatError(f"{record_type} requires non-empty {field_name}")
    return value.strip()


def _optional_float(record: Mapping[str, Any], field_name: str, record_type: str) -> float | None:
    value = record.get(field_name)
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise GraphFormatError(f"{record_type} {field_name} must be numeric") from error


def _required_float(record: Mapping[str, Any], field_name: str, record_type: str) -> float:
    value = _optional_float(record, field_name, record_type)
    if value is None:
        raise GraphFormatError(f"{record_type} requires {field_name}")
    return value


def _csv_value(value: str) -> Any:
    if value == "":
        return None
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def _node_from_record(record: Mapping[str, Any]) -> Node:
    node_id = _required_text(record, "node_id", "Node")
    attributes = {
        key: _csv_value(value) if isinstance(value, str) else value
        for key, value in record.items()
        if key not in {"node_id", "latitude", "longitude"}
    }
    return Node(
        node_id=node_id,
        latitude=_optional_float(record, "latitude", f"Node {node_id}"),
        longitude=_optional_float(record, "longitude", f"Node {node_id}"),
        attributes=attributes,
    )


def _edge_from_record(record: Mapping[str, Any]) -> Edge:
    edge_id = _required_text(record, "edge_id", "Edge")
    from_node_id = _required_text(record, "from_node_id", f"Edge {edge_id}")
    to_node_id = _required_text(record, "to_node_id", f"Edge {edge_id}")
    attributes = {
        key: _csv_value(value) if isinstance(value, str) else value
        for key, value in record.items()
        if key not in {
            "edge_id",
            "from_node_id",
            "to_node_id",
            "distance_m",
            "free_flow_time_min",
        }
    }
    return Edge(
        edge_id=edge_id,
        from_node_id=from_node_id,
        to_node_id=to_node_id,
        distance_m=_required_float(record, "distance_m", f"Edge {edge_id}"),
        free_flow_time_min=_required_float(
            record,
            "free_flow_time_min",
            f"Edge {edge_id}",
        ),
        attributes=attributes,
    )


def _scenario_from_record(record: Mapping[str, Any]) -> Scenario:
    scenario_id = record.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise GraphFormatError("Scenario requires non-empty scenario_id")

    closed_edge_ids = record.get("closed_edge_ids", record.get("closed_edges", ()))
    if closed_edge_ids is None:
        closed_edge_ids = ()
    if isinstance(closed_edge_ids, str) or not isinstance(closed_edge_ids, Iterable):
        raise GraphFormatError(
            f"Scenario {scenario_id} closed_edge_ids must be an array of edge ids"
        )
    attributes = {
        key: value
        for key, value in record.items()
        if key not in {"scenario_id", "closed_edge_ids", "closed_edges"}
    }
    return Scenario(
        scenario_id=scenario_id,
        closed_edge_ids=tuple(closed_edge_ids),
        attributes=attributes,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise GraphFormatError(f"CSV has no header: {path}")
            return [dict(row) for row in reader]
    except FileNotFoundError as error:
        raise GraphFormatError(f"Missing graph input: {path}") from error


def _read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise GraphFormatError(f"Missing graph input: {path}") from error
    except json.JSONDecodeError as error:
        raise GraphFormatError(f"Invalid JSON in {path}: {error.msg}") from error


def _scenario_records(payload: Any) -> list[Mapping[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, Mapping):
        payload = payload.get("scenarios", payload)
        if isinstance(payload, Mapping):
            records: list[Mapping[str, Any]] = []
            for scenario_id, value in payload.items():
                if not isinstance(value, Mapping):
                    raise GraphFormatError(f"Scenario {scenario_id} must be an object")
                records.append({"scenario_id": scenario_id, **value})
            return records
    if not isinstance(payload, list):
        raise GraphFormatError("scenarios must be an array or object")
    if any(not isinstance(item, Mapping) for item in payload):
        raise GraphFormatError("Every scenario must be an object")
    return list(payload)


def _build_graph(
    node_records: Iterable[Mapping[str, Any]],
    edge_records: Iterable[Mapping[str, Any]],
    scenario_records: Iterable[Mapping[str, Any]] = (),
    *,
    metadata: Mapping[str, Any] | None = None,
) -> Graph:
    return Graph(
        nodes=tuple(_node_from_record(record) for record in node_records),
        edges=tuple(_edge_from_record(record) for record in edge_records),
        scenarios=tuple(_scenario_from_record(record) for record in scenario_records),
        metadata=metadata,
    )


class GraphLoader:
    """Factory for immutable graphs from fixture or processed graph files."""

    REQUIRED_DIRECTORY_FILES = frozenset({"nodes.csv", "edges.csv"})

    @classmethod
    def load(
        cls,
        source: PathLike,
        edges_path: PathLike | None = None,
        scenarios_path: PathLike | None = None,
    ) -> Graph:
        source_path = Path(source)
        if source_path.is_dir():
            return cls.from_directory(source_path)
        if source_path.suffix.lower() == ".json":
            return cls.from_json(source_path, scenarios_path)
        if source_path.suffix.lower() == ".csv":
            if edges_path is None:
                raise GraphFormatError("Loading CSV graph requires nodes and edges CSV paths")
            return cls.from_csv(source_path, edges_path, scenarios_path)
        raise GraphFormatError(f"Unsupported graph input: {source_path}")

    @classmethod
    def from_directory(
        cls,
        directory: PathLike,
        *,
        nodes_filename: str = "nodes.csv",
        edges_filename: str = "edges.csv",
        scenarios_filename: str = "scenarios.json",
    ) -> Graph:
        directory_path = Path(directory)
        scenarios_path = directory_path / scenarios_filename
        graph = cls.from_csv(
            directory_path / nodes_filename,
            directory_path / edges_filename,
            scenarios_path if scenarios_path.is_file() else None,
        )
        metadata_path = directory_path / "metadata.json"
        if not metadata_path.is_file():
            return graph
        metadata_payload = _read_json(metadata_path)
        if not isinstance(metadata_payload, Mapping):
            raise GraphFormatError(f"Graph metadata must be an object: {metadata_path}")
        return Graph(
            graph.nodes,
            graph.edges,
            graph.scenarios,
            metadata={**graph.metadata, **metadata_payload},
        )

    @classmethod
    def discover_directories(cls, root: PathLike) -> tuple[Path, ...]:
        """Find loadable graph folders below ``root`` in deterministic order."""
        root_path = Path(root).resolve()
        if not root_path.is_dir():
            raise GraphFormatError(f"Graph discovery root is not a directory: {root_path}")

        candidates = {root_path}
        candidates.update(path.parent.resolve() for path in root_path.rglob("nodes.csv"))
        graph_directories = []
        for candidate in candidates:
            if not candidate.is_relative_to(root_path):
                continue
            filenames = {path.name for path in candidate.iterdir() if path.is_file()}
            if cls.REQUIRED_DIRECTORY_FILES <= filenames:
                graph_directories.append(candidate)
        return tuple(
            sorted(
                graph_directories,
                key=lambda path: path.relative_to(root_path).as_posix(),
            )
        )

    from_fixture = from_directory

    @classmethod
    def from_csv(
        cls,
        nodes_path: PathLike,
        edges_path: PathLike,
        scenarios_path: PathLike | None = None,
    ) -> Graph:
        nodes_file = Path(nodes_path)
        edges_file = Path(edges_path)
        scenario_payload = _read_json(Path(scenarios_path)) if scenarios_path else None
        metadata: dict[str, Any] = {
            "source_format": "CSV",
            "nodes_path": str(nodes_file),
            "edges_path": str(edges_file),
        }
        if isinstance(scenario_payload, Mapping):
            metadata.update(
                {
                    key: value
                    for key, value in scenario_payload.items()
                    if key != "scenarios"
                }
            )
        return _build_graph(
            _read_csv(nodes_file),
            _read_csv(edges_file),
            _scenario_records(scenario_payload),
            metadata=metadata,
        )

    @classmethod
    def from_json(
        cls,
        graph_path: PathLike,
        scenarios_path: PathLike | None = None,
    ) -> Graph:
        payload = _read_json(Path(graph_path))
        if not isinstance(payload, Mapping):
            raise GraphFormatError("Graph JSON root must be an object")
        if isinstance(payload.get("graph"), Mapping):
            payload = payload["graph"]

        node_records = payload.get("nodes")
        edge_records = payload.get("edges")
        if not isinstance(node_records, list) or not isinstance(edge_records, list):
            raise GraphFormatError("Graph JSON must contain nodes and edges arrays")
        if any(not isinstance(item, Mapping) for item in node_records + edge_records):
            raise GraphFormatError("Every node and edge in Graph JSON must be an object")

        external_scenarios = _read_json(Path(scenarios_path)) if scenarios_path else None
        root_scenarios = payload.get("scenarios")
        if root_scenarios is not None and external_scenarios is not None:
            raise GraphFormatError("Specify scenarios in graph JSON or scenarios_path, not both")
        scenario_payload = (
            external_scenarios if external_scenarios is not None else root_scenarios
        )
        metadata = {
            key: value
            for key, value in payload.items()
            if key not in {"nodes", "edges", "scenarios"}
        }
        metadata["source_format"] = "JSON"
        metadata["graph_path"] = str(Path(graph_path))
        return _build_graph(
            node_records,
            edge_records,
            _scenario_records(scenario_payload),
            metadata=metadata,
        )

    load_directory = from_directory
    load_fixture = from_directory
    load_from_directory = from_directory
    load_from_fixture = from_directory
    load_csv = from_csv
    load_from_csv = from_csv
    load_json = from_json
    load_from_json = from_json


def load_graph(
    source: PathLike,
    edges_path: PathLike | None = None,
    scenarios_path: PathLike | None = None,
) -> Graph:
    """Convenience wrapper around :meth:`GraphLoader.load`."""
    return GraphLoader.load(source, edges_path, scenarios_path)


__all__ = [
    "Edge",
    "Graph",
    "GraphFormatError",
    "GraphLoader",
    "Node",
    "Scenario",
    "load_graph",
]
