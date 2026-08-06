import { useEffect, useMemo } from 'react'
import { CircleMarker, MapContainer, Polyline, Tooltip, useMap } from 'react-leaflet'
import { latLngBounds, type LatLngExpression } from 'leaflet'
import recenterGraphIcon from '../../assets/recenter-graph.png'
import type { GraphPayload } from '../../lib/graph'

type RouteMapProps = {
  graph: GraphPayload
  pathEdgeIds?: string[]
  visiblePathEdgeCount?: number
  pathNodeIds?: string[]
  exploredNodeIds?: string[]
  startId?: string
  goalId?: string
}

function FitGraphBounds({ positions }: { positions: LatLngExpression[] }) {
  const map = useMap()

  useEffect(() => {
    map.invalidateSize()
    if (positions.length > 1) {
      map.fitBounds(latLngBounds(positions), { padding: [52, 52], maxZoom: 16 })
    }
  }, [map, positions])

  return null
}

function ResetGraphView({ positions }: { positions: LatLngExpression[] }) {
  const map = useMap()

  function resetView() {
    if (positions.length > 1) {
      map.fitBounds(latLngBounds(positions), { padding: [52, 52], maxZoom: 16 })
    } else if (positions[0]) {
      map.setView(positions[0], 15)
    }
  }

  return (
    <button
      type="button"
      className="map-reset-button"
      title="Đưa bản đồ về vị trí graph"
      aria-label="Đưa bản đồ về vị trí graph"
      onMouseDown={(event) => event.stopPropagation()}
      onDoubleClick={(event) => event.stopPropagation()}
      onClick={(event) => {
        event.stopPropagation()
        resetView()
      }}
    >
      <img src={recenterGraphIcon} alt="" aria-hidden="true" />
    </button>
  )
}

export function RouteMap({
  graph,
  pathEdgeIds = [],
  visiblePathEdgeCount = pathEdgeIds.length,
  pathNodeIds = [],
  exploredNodeIds = [],
  startId,
  goalId,
}: RouteMapProps) {
  const drawableNodes = useMemo(
    () => graph.nodes.filter(
      (node) => node.latitude !== null && node.longitude !== null,
    ),
    [graph.nodes],
  )
  const nodeById = new Map(drawableNodes.map((node) => [node.node_id, node]))
  const visiblePathEdgeIds = pathEdgeIds.slice(0, visiblePathEdgeCount)
  const pathNodes = new Set(pathNodeIds)
  const exploredNodes = new Set(exploredNodeIds)
  const positions = useMemo<LatLngExpression[]>(
    () => drawableNodes.map((node) => [node.latitude!, node.longitude!]),
    [drawableNodes],
  )
  const center = positions[0] ?? ([10.849, 106.756] as LatLngExpression)

  return (
    <MapContainer
      key={graph.graph_id}
      center={center}
      zoom={14}
      scrollWheelZoom
      className="route-map"
      attributionControl={false}
    >
      <FitGraphBounds positions={positions} />
      <ResetGraphView positions={positions} />

      {graph.edges.map((edge) => {
        const from = nodeById.get(edge.from_node_id)
        const to = nodeById.get(edge.to_node_id)
        if (!from || !to) return null
        return (
          <Polyline
            key={edge.edge_id}
            positions={[
              [from.latitude!, from.longitude!],
              [to.latitude!, to.longitude!],
            ]}
            pathOptions={{
              color: edge.is_closed ? '#ba1a1a' : '#00714d',
              weight: 4,
              opacity: edge.is_closed ? 0.72 : 0.82,
              dashArray: edge.is_closed ? '7 9' : undefined,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          >
            <Tooltip>
              {edge.edge_id}: {edge.from_node_id} → {edge.to_node_id}
              {edge.is_closed ? ' · CLOSED' : ''}
            </Tooltip>
          </Polyline>
        )
      })}

      {visiblePathEdgeIds.flatMap((edgeId, index) => {
        const edge = graph.edges.find((item) => item.edge_id === edgeId)
        if (!edge) return []
        const from = nodeById.get(edge.from_node_id)
        const to = nodeById.get(edge.to_node_id)
        if (!from || !to) return []
        const segment: LatLngExpression[] = [
          [from.latitude!, from.longitude!],
          [to.latitude!, to.longitude!],
        ]
        return [
          <Polyline
            key={`${edgeId}-halo`}
            positions={segment}
            pathOptions={{
              color: '#ffffff',
              weight: 13,
              opacity: 0.94,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />,
          <Polyline
            key={`${edgeId}-path`}
            positions={segment}
            pathOptions={{
              color: '#6d28d9',
              weight: 8,
              opacity: 1,
              lineCap: 'round',
              lineJoin: 'round',
              className: `route-path-segment route-path-segment-${index}`,
            }}
          >
            <Tooltip>{edge.edge_id} · OPTIMAL PATH</Tooltip>
          </Polyline>,
        ]
      })}

      {drawableNodes.map((node) => {
        const isStart = node.node_id === startId
        const isGoal = node.node_id === goalId
        const isPath = pathNodes.has(node.node_id)
        const isExplored = exploredNodes.has(node.node_id)
        const color = isStart
          ? '#d97706'
          : isGoal
            ? '#db2777'
            : isPath
              ? '#6d28d9'
              : isExplored
                ? '#a36700'
                : '#424754'
        const fillColor = isStart
          ? '#fef3c7'
          : isGoal
            ? '#fce7f3'
            : isPath
              ? '#ede9fe'
              : isExplored
                ? '#ffddb8'
                : '#ffffff'

        return (
          <CircleMarker
            key={node.node_id}
            center={[node.latitude!, node.longitude!]}
            radius={isStart || isGoal ? 12 : isPath ? 8 : 6}
            pathOptions={{
              color,
              fillColor,
              fillOpacity: 1,
              weight: isStart || isGoal ? 5 : 3,
              className: isStart
                ? 'endpoint-marker endpoint-start'
                : isGoal
                  ? 'endpoint-marker endpoint-goal'
                  : undefined,
            }}
          >
            <Tooltip
              direction="top"
              offset={[0, -10]}
              permanent={isStart || isGoal}
              className={isStart ? 'endpoint-label start-label' : isGoal ? 'endpoint-label goal-label' : ''}
            >
              {node.label} · {node.node_id}
              {isStart ? ' · START' : isGoal ? ' · GOAL' : isPath ? ' · PATH' : ''}
            </Tooltip>
          </CircleMarker>
        )
      })}

      <div className="map-note">{graph.data_status} · {graph.graph_id}</div>
    </MapContainer>
  )
}
