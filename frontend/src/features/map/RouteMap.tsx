import { CircleMarker, MapContainer, Polyline, Tooltip } from 'react-leaflet'
import type { LatLngExpression } from 'leaflet'

type Scenario = 'OFFPEAK_BALANCED' | 'HEAVY_RAIN_SAFE'

type RouteMapProps = {
  scenario: Scenario
}

const nodes: Record<string, { label: string; position: LatLngExpression }> = {
  N01: { label: 'Kho Linh Trung', position: [10.8678, 106.7789] },
  N02: { label: 'Võ Văn Ngân', position: [10.8506, 106.7719] },
  N03: { label: 'Chợ Thủ Đức', position: [10.8498, 106.7535] },
  N04: { label: 'Kha Vạn Cân', position: [10.85, 106.747] },
  N05: { label: 'Phạm Văn Đồng', position: [10.831, 106.7345] },
  N06: { label: 'Điểm giao Linh Đông', position: [10.842, 106.741] },
}

const graphEdges: [string, string][] = [
  ['N01', 'N02'],
  ['N02', 'N06'],
  ['N01', 'N03'],
  ['N03', 'N04'],
  ['N04', 'N06'],
  ['N02', 'N04'],
  ['N03', 'N05'],
  ['N05', 'N06'],
]

const routes: Record<Scenario, string[]> = {
  OFFPEAK_BALANCED: ['N01', 'N02', 'N06'],
  HEAVY_RAIN_SAFE: ['N01', 'N02', 'N04', 'N06'],
}

export function RouteMap({ scenario }: RouteMapProps) {
  const route = routes[scenario]
  const routePositions = route.map((nodeId) => nodes[nodeId].position)

  return (
    <MapContainer
      center={[10.849, 106.756]}
      zoom={14}
      scrollWheelZoom={false}
      className="route-map"
      attributionControl={false}
    >
      {graphEdges.map(([from, to]) => (
        <Polyline
          key={`${from}-${to}`}
          positions={[nodes[from].position, nodes[to].position]}
          pathOptions={{ color: '#9fb5b0', weight: 3, opacity: 0.55, dashArray: '7 8' }}
        />
      ))}

      <Polyline
        positions={routePositions}
        pathOptions={{ color: '#ff6b35', weight: 7, opacity: 0.95 }}
      />

      {Object.entries(nodes).map(([nodeId, node]) => {
        const isOnRoute = route.includes(nodeId)
        const isEndpoint = nodeId === route[0] || nodeId === route.at(-1)

        return (
          <CircleMarker
            key={nodeId}
            center={node.position}
            radius={isEndpoint ? 9 : 6}
            pathOptions={{
              color: isOnRoute ? '#0d6f64' : '#718b86',
              fillColor: isOnRoute ? '#e4fff9' : '#eef4f2',
              fillOpacity: 1,
              weight: 3,
            }}
          >
            <Tooltip direction="top" offset={[0, -8]} permanent={isEndpoint}>
              {node.label}
            </Tooltip>
          </CircleMarker>
        )
      })}

      <div className="map-note">Offline fixture · SIMULATED</div>
    </MapContainer>
  )
}

