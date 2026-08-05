import { useEffect, useMemo } from 'react'
import { CircleMarker, MapContainer, Polyline, Tooltip, useMap } from 'react-leaflet'
import { latLngBounds, type LatLngExpression } from 'leaflet'
import type { GraphPayload } from '../../lib/graph'

type RouteMapProps = {
  graph: GraphPayload
}

function FitGraphBounds({ positions }: { positions: LatLngExpression[] }) {
  const map = useMap()

  useEffect(() => {
    if (positions.length > 1) {
      map.fitBounds(latLngBounds(positions), { padding: [36, 36], maxZoom: 16 })
    }
  }, [map, positions])

  return null
}

export function RouteMap({ graph }: RouteMapProps) {
  const drawableNodes = graph.nodes.filter(
    (node) => node.latitude !== null && node.longitude !== null,
  )
  const nodeById = new Map(drawableNodes.map((node) => [node.node_id, node]))
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
        return (
          <Polyline
            key={edge.edge_id}
            positions={[
              [from.latitude!, from.longitude!],
              [to.latitude!, to.longitude!],
            ]}
            pathOptions={{
              color: edge.is_closed ? '#c75b4d' : '#0d6f64',
              weight: edge.is_closed ? 4 : 5,
              opacity: edge.is_closed ? 0.65 : 0.82,
              dashArray: edge.is_closed ? '5 8' : undefined,
            }}
          >
            <Tooltip>
              {edge.edge_id}: {edge.from_node_id} → {edge.to_node_id}
              {edge.is_closed ? ' · CLOSED' : ''}
            </Tooltip>
          </Polyline>
        )
      })}

      {drawableNodes.map((node) => (
        <CircleMarker
          key={node.node_id}
          center={[node.latitude!, node.longitude!]}
          radius={7}
          pathOptions={{
            color: '#0d6f64',
            fillColor: '#e4fff9',
            fillOpacity: 1,
            weight: 3,
          }}
        >
          <Tooltip direction="top" offset={[0, -8]}>
            {node.label} · {node.node_id}
          </Tooltip>
        </CircleMarker>
      ))}

      <div className="map-note">{graph.data_status} · {graph.graph_id}</div>
    </MapContainer>
  )
}
