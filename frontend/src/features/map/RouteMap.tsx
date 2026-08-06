import { useEffect, useMemo } from 'react'
import { CircleMarker, MapContainer, Polyline, Tooltip, useMap } from 'react-leaflet'
import { latLngBounds, type LatLngExpression } from 'leaflet'
import type { GraphPayload } from '../../lib/graph'

type RouteMapProps = {
  graph: GraphPayload
  pathEdgeIds?: string[]
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

export function RouteMap({
  graph,
  pathEdgeIds = [],
  pathNodeIds = [],
  exploredNodeIds = [],
  startId,
  goalId,
}: RouteMapProps) {
  const drawableNodes = graph.nodes.filter(
    (node) => node.latitude !== null && node.longitude !== null,
  )
  const nodeById = new Map(drawableNodes.map((node) => [node.node_id, node]))
  const pathEdges = new Set(pathEdgeIds)
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

      {graph.edges.map((edge) => {
        const from = nodeById.get(edge.from_node_id)
        const to = nodeById.get(edge.to_node_id)
        if (!from || !to) return null
        const isPath = pathEdges.has(edge.edge_id)
        const color = isPath ? '#2170e4' : edge.is_closed ? '#ba1a1a' : '#00714d'
        return (
          <Polyline
            key={edge.edge_id}
            positions={[
              [from.latitude!, from.longitude!],
              [to.latitude!, to.longitude!],
            ]}
            pathOptions={{
              color,
              weight: isPath ? 7 : edge.is_closed ? 4 : 4,
              opacity: isPath ? 1 : edge.is_closed ? 0.72 : 0.82,
              dashArray: edge.is_closed && !isPath ? '7 9' : undefined,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          >
            <Tooltip>
              {edge.edge_id}: {edge.from_node_id} → {edge.to_node_id}
              {isPath ? ' · OPTIMAL PATH' : edge.is_closed ? ' · CLOSED' : ''}
            </Tooltip>
          </Polyline>
        )
      })}

      {drawableNodes.map((node) => {
        const isStart = node.node_id === startId
        const isGoal = node.node_id === goalId
        const isPath = pathNodes.has(node.node_id)
        const isExplored = exploredNodes.has(node.node_id)
        const color = isStart
          ? '#006c49'
          : isGoal
            ? '#ba1a1a'
            : isPath
              ? '#0058be'
              : isExplored
                ? '#a36700'
                : '#424754'
        const fillColor = isStart
          ? '#d9f7e9'
          : isGoal
            ? '#ffdad6'
            : isPath
              ? '#d8e2ff'
              : isExplored
                ? '#ffddb8'
                : '#ffffff'

        return (
          <CircleMarker
            key={node.node_id}
            center={[node.latitude!, node.longitude!]}
            radius={isStart || isGoal ? 10 : isPath ? 8 : 6}
            pathOptions={{ color, fillColor, fillOpacity: 1, weight: 3 }}
          >
            <Tooltip direction="top" offset={[0, -8]}>
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
