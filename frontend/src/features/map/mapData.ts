import type { Feature, FeatureCollection, LineString, Point } from 'geojson'
import type { GraphEdge, GraphNode, GraphPayload } from '../../lib/graph'

export type NodeVisualState = 'default' | 'explored' | 'path' | 'start' | 'goal'

export type NodeFeatureProperties = {
  node_id: string
  display_name: string
  node_type: string
  data_status: string
  label_status: 'SOURCE_BACKED' | 'DERIVED'
  visual_state: NodeVisualState
}

export type EdgeFeatureProperties = {
  edge_id: string
  from_node_id: string
  to_node_id: string
  road_name: string
  is_closed: boolean
  route_index: number
}

type GraphState = {
  startId?: string
  goalId?: string
  pathNodeIds?: string[]
  exploredNodeIds?: string[]
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
  const exploredNodes = new Set(state.exploredNodeIds ?? [])

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
          : exploredNodes.has(node.node_id)
            ? 'explored'
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
  return {
    type: 'Feature',
    id: edge.edge_id,
    geometry: {
      type: 'LineString',
      coordinates: [
        [from.longitude, from.latitude],
        [to.longitude, to.latitude],
      ],
    },
    properties: {
      edge_id: edge.edge_id,
      from_node_id: edge.from_node_id,
      to_node_id: edge.to_node_id,
      road_name: String(edge.attributes.road_name ?? ''),
      is_closed: edge.is_closed,
      route_index: routeIndex,
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
