import type { Feature, FeatureCollection, LineString, Point } from 'geojson'
import type { GraphEdge, GraphNode, GraphPayload } from '../../lib/graph'

export type NodeVisualState = 'default' | 'frontier' | 'current' | 'closed' | 'path' | 'start' | 'goal'

export type NodeFeatureProperties = {
  node_id: string
  display_name: string
  node_type: string
  data_status: string
  label_status: 'SOURCE_BACKED' | 'DERIVED'
  visual_state: NodeVisualState
  selectable: boolean
  place_category: string
  snap_distance_m: number
}

export type EdgeFeatureProperties = {
  edge_id: string
  from_node_id: string
  to_node_id: string
  road_name: string
  is_closed: boolean
  route_index: number
  distance_m: number
  free_flow_time_min: number
}

type GraphState = {
  startId?: string
  goalId?: string
  pathNodeIds?: string[]
  frontierNodeIds?: string[]
  closedNodeIds?: string[]
  currentNodeId?: string | null
}

export type NodeSnapResult = {
  nodeId: string
  longitude: number
  latitude: number
  distanceM: number
}

function haversineM(
  fromLongitude: number,
  fromLatitude: number,
  toLongitude: number,
  toLatitude: number,
): number {
  const radians = Math.PI / 180
  const deltaLatitude = (toLatitude - fromLatitude) * radians
  const deltaLongitude = (toLongitude - fromLongitude) * radians
  const fromLatitudeRadians = fromLatitude * radians
  const toLatitudeRadians = toLatitude * radians
  const haversine = Math.sin(deltaLatitude / 2) ** 2
    + Math.cos(fromLatitudeRadians) * Math.cos(toLatitudeRadians)
    * Math.sin(deltaLongitude / 2) ** 2
  return 2 * 6_371_000 * Math.asin(Math.sqrt(haversine))
}

export function findNearestGraphNode(
  graph: GraphPayload,
  longitude: number,
  latitude: number,
  maxDistanceM = 200,
): NodeSnapResult | null {
  if (!Number.isFinite(longitude) || !Number.isFinite(latitude) || maxDistanceM < 0) return null
  let nearest: NodeSnapResult | null = null
  for (const node of graph.nodes) {
    if (node.attributes.selectable === false || node.attributes.selectable === 'false') continue
    if (node.longitude === null || node.latitude === null) continue
    const distanceM = haversineM(longitude, latitude, node.longitude, node.latitude)
    if (
      distanceM > maxDistanceM
      || (nearest && distanceM > nearest.distanceM)
      || (nearest && distanceM === nearest.distanceM && node.node_id >= nearest.nodeId)
    ) continue
    nearest = {
      nodeId: node.node_id,
      longitude: node.longitude,
      latitude: node.latitude,
      distanceM,
    }
  }
  return nearest
}

function sortedUnique(values: string[]): string[] {
  return [...new Set(values.map((value) => value.trim()).filter(Boolean))]
    .sort((left, right) => left < right ? -1 : left > right ? 1 : 0)
}

function isMeaningfulNodeLabel(node: GraphNode): boolean {
  const label = node.label.trim()
  if (!label || label === node.node_id || /^UTraffic node \d+$/i.test(label)) return false
  return node.attributes.node_type === 'POI' || !/^node\b/i.test(label)
}

export function deriveNodeDisplayName(node: GraphNode, incidentEdges: GraphEdge[]): {
  displayName: string
  labelStatus: 'SOURCE_BACKED' | 'DERIVED'
} {
  if (isMeaningfulNodeLabel(node)) {
    return { displayName: node.label.trim(), labelStatus: 'SOURCE_BACKED' }
  }

  const roadNames = sortedUnique(incidentEdges.map((edge) => {
    const value = edge.attributes.road_name
    return typeof value === 'string' ? value : ''
  }))
  if (roadNames.length >= 2) {
    return {
      displayName: `Giao ${roadNames.slice(0, 3).join(' × ')}`,
      labelStatus: 'DERIVED',
    }
  }
  if (roadNames.length === 1) {
    return { displayName: `Nút trên ${roadNames[0]}`, labelStatus: 'DERIVED' }
  }
  if (node.latitude !== null && node.longitude !== null) {
    return {
      displayName: `Node tại ${node.latitude.toFixed(5)}, ${node.longitude.toFixed(5)}`,
      labelStatus: 'DERIVED',
    }
  }
  return { displayName: node.node_id, labelStatus: 'DERIVED' }
}

export function buildNodeFeatureCollection(
  graph: GraphPayload,
  state: GraphState = {},
): FeatureCollection<Point, NodeFeatureProperties> {
  const incidentByNode = new Map<string, GraphEdge[]>()
  for (const edge of graph.edges) {
    incidentByNode.set(
      edge.from_node_id,
      [...(incidentByNode.get(edge.from_node_id) ?? []), edge],
    )
    incidentByNode.set(
      edge.to_node_id,
      [...(incidentByNode.get(edge.to_node_id) ?? []), edge],
    )
  }
  const pathNodes = new Set(state.pathNodeIds ?? [])
  const frontierNodes = new Set(state.frontierNodeIds ?? [])
  const closedNodes = new Set(state.closedNodeIds ?? [])

  const features = graph.nodes.flatMap<Feature<Point, NodeFeatureProperties>>((node) => {
    if (node.latitude === null || node.longitude === null) return []
    const { displayName, labelStatus } = deriveNodeDisplayName(
      node,
      incidentByNode.get(node.node_id) ?? [],
    )
    const visualState: NodeVisualState = node.node_id === state.startId
      ? 'start'
      : node.node_id === state.goalId
        ? 'goal'
        : pathNodes.has(node.node_id)
          ? 'path'
          : node.node_id === state.currentNodeId
            ? 'current'
            : frontierNodes.has(node.node_id)
              ? 'frontier'
              : closedNodes.has(node.node_id)
                ? 'closed'
            : 'default'
    return [{
      type: 'Feature',
      id: node.node_id,
      geometry: {
        type: 'Point',
        coordinates: [node.longitude, node.latitude],
      },
      properties: {
        node_id: node.node_id,
        display_name: displayName,
        node_type: String(node.attributes.node_type ?? 'INTERSECTION_OR_GEOMETRY'),
        data_status: String(node.attributes.data_status ?? graph.data_status),
        label_status: labelStatus,
        visual_state: visualState,
        selectable: node.attributes.selectable !== false && node.attributes.selectable !== 'false',
        place_category: String(node.attributes.place_category ?? ''),
        snap_distance_m: Number(node.attributes.snap_distance_m ?? 0),
      },
    }]
  })
  return { type: 'FeatureCollection', features }
}

function edgeFeature(
  edge: GraphEdge,
  nodeById: Map<string, GraphNode>,
  routeIndex: number,
): Feature<LineString, EdgeFeatureProperties> | null {
  const from = nodeById.get(edge.from_node_id)
  const to = nodeById.get(edge.to_node_id)
  if (
    !from || !to
    || from.latitude === null || from.longitude === null
    || to.latitude === null || to.longitude === null
  ) return null
  let coordinates: [number, number][] = [
    [from.longitude, from.latitude],
    [to.longitude, to.latitude],
  ]
  const encodedPath = edge.attributes.path_coordinates_json
  if (typeof encodedPath === 'string' && encodedPath) {
    try {
      const parsed: unknown = JSON.parse(encodedPath)
      if (Array.isArray(parsed)) {
        const validCoordinates = parsed.flatMap<[number, number]>((item) => (
          Array.isArray(item) && item.length >= 2
          && typeof item[0] === 'number' && Number.isFinite(item[0])
          && typeof item[1] === 'number' && Number.isFinite(item[1])
            ? [[item[0], item[1]]]
            : []
        ))
        if (validCoordinates.length >= 2) coordinates = validCoordinates
      }
    } catch {
      // Invalid optional display geometry falls back to the contract endpoints.
    }
  }
  return {
    type: 'Feature',
    id: edge.edge_id,
    geometry: {
      type: 'LineString',
      coordinates,
    },
    properties: {
      edge_id: edge.edge_id,
      from_node_id: edge.from_node_id,
      to_node_id: edge.to_node_id,
      road_name: String(edge.attributes.road_name ?? ''),
      is_closed: edge.is_closed,
      route_index: routeIndex,
      distance_m: edge.distance_m,
      free_flow_time_min: edge.free_flow_time_min,
    },
  }
}

export function buildEdgeFeatureCollection(
  graph: GraphPayload,
): FeatureCollection<LineString, EdgeFeatureProperties> {
  const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]))
  const features = graph.edges.flatMap((edge) => {
    const feature = edgeFeature(edge, nodeById, -1)
    return feature ? [feature] : []
  })
  return { type: 'FeatureCollection', features }
}

export function buildRouteFeatureCollection(
  graph: GraphPayload,
  edgeIds: string[],
): FeatureCollection<LineString, EdgeFeatureProperties> {
  const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]))
  const edgeById = new Map(graph.edges.map((edge) => [edge.edge_id, edge]))
  const features = edgeIds.flatMap((edgeId, index) => {
    const edge = edgeById.get(edgeId)
    if (!edge) return []
    const feature = edgeFeature(edge, nodeById, index)
    return feature ? [feature] : []
  })
  return { type: 'FeatureCollection', features }
}

export type ClosedEdgeMarkerData = {
  edgeId: string
  roadName: string
  fromNodeId: string
  toNodeId: string
  distanceM: number
  freeFlowTimeMin: number
  midpoint: [number, number]
}

export function buildClosedEdgeMarkers(graph: GraphPayload): ClosedEdgeMarkerData[] {
  const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]))
  const processedPairs = new Set<string>()
  const markers: ClosedEdgeMarkerData[] = []

  for (const edge of graph.edges) {
    if (!edge.is_closed) continue

    // Group pair of bidirectional edges so we only display 1 barrier marker on the street
    const pairKey = [edge.from_node_id, edge.to_node_id].sort().join('--')
    if (processedPairs.has(pairKey)) continue
    processedPairs.add(pairKey)

    const feature = edgeFeature(edge, nodeById, -1)
    if (!feature) continue
    const coords = feature.geometry.coordinates as [number, number][]
    if (!coords.length) continue
    const midIdx = Math.floor(coords.length / 2)
    const midpoint = coords[midIdx] || coords[0]

    markers.push({
      edgeId: edge.edge_id,
      roadName: String(edge.attributes.road_name || edge.edge_id),
      fromNodeId: edge.from_node_id,
      toNodeId: edge.to_node_id,
      distanceM: edge.distance_m,
      freeFlowTimeMin: edge.free_flow_time_min,
      midpoint,
    })
  }

  return markers
}
