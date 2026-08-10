import { describe, expect, it } from 'vitest'
import type { GraphEdge, GraphNode, GraphPayload } from '../../lib/graph'
import {
  buildEdgeFeatureCollection,
  buildNodeFeatureCollection,
  buildRouteFeatureCollection,
  deriveNodeDisplayName,
  findNearestGraphNode,
} from './mapData'

function node(
  node_id: string,
  label = `UTraffic node ${node_id}`,
  latitude: number | null = 10.85,
  longitude: number | null = 106.75,
  node_type = 'INTERSECTION_OR_GEOMETRY',
): GraphNode {
  return {
    node_id,
    label,
    latitude,
    longitude,
    attributes: { node_type, data_status: 'SOURCE_BACKED' },
  }
}

function edge(
  edge_id: string,
  from_node_id: string,
  to_node_id: string,
  road_name = '',
  is_closed = false,
): GraphEdge {
  return {
    edge_id,
    from_node_id,
    to_node_id,
    distance_m: 100,
    free_flow_time_min: 1,
    is_closed,
    attributes: { road_name },
  }
}

const graph: GraphPayload = {
  graph_id: 'test_graph',
  directed: true,
  data_status: 'MIXED',
  active_scenario_id: 'TEST',
  metadata: {},
  scenarios: [{ scenario_id: 'TEST', closed_edge_ids: [] }],
  nodes: [
    node('1', 'UTraffic node 1', 10.85, 106.75),
    node('2', 'Chợ Thủ Đức', 10.851, 106.751, 'POI'),
    node('3', 'UTraffic node 3', 10.852, 106.752),
  ],
  edges: [
    edge('E1', '1', '2', 'Kha Vạn Cân'),
    edge('E2', '3', '1', 'Dương Văn Cam', true),
  ],
  active_edge_count: 1,
}

describe('deterministic map labels', () => {
  it('keeps a source-backed POI name', () => {
    expect(deriveNodeDisplayName(graph.nodes[1], graph.edges)).toEqual({
      displayName: 'Chợ Thủ Đức',
      labelStatus: 'SOURCE_BACKED',
    })
  })

  it('derives sorted intersection and single-road names', () => {
    const target = graph.nodes[0]
    expect(deriveNodeDisplayName(target, [
      edge('A', '1', '2', 'Kha Vạn Cân'),
      edge('B', '3', '1', 'Dương Văn Cam'),
    ])).toEqual({
      displayName: 'Giao Dương Văn Cam × Kha Vạn Cân',
      labelStatus: 'DERIVED',
    })
    expect(deriveNodeDisplayName(target, [edge('C', '1', '2', 'Kha Vạn Cân')]).displayName)
      .toBe('Nút trên Kha Vạn Cân')
  })

  it('falls back to fixed coordinate precision', () => {
    expect(deriveNodeDisplayName(node('9', 'UTraffic node 9', 10.851234, 106.751239), []))
      .toEqual({
        displayName: 'Node tại 10.85123, 106.75124',
        labelStatus: 'DERIVED',
      })
  })
})

describe('graph GeoJSON', () => {
  it('encodes node visual-state priority and skips missing coordinates', () => {
    const payload = { ...graph, nodes: [...graph.nodes, node('missing', 'missing', null, null)] }
    const collection = buildNodeFeatureCollection(payload, {
      startId: '1',
      goalId: '2',
      pathNodeIds: ['1', '2', '3'],
      exploredNodeIds: ['1', '2', '3'],
    })

    expect(collection.features).toHaveLength(3)
    expect(collection.features.map((feature) => feature.properties.visual_state))
      .toEqual(['start', 'goal', 'path'])
  })

  it('keeps directed edge closure and route ordering', () => {
    const edges = buildEdgeFeatureCollection(graph)
    const route = buildRouteFeatureCollection(graph, ['E2', 'E1'])

    expect(edges.features[1].properties).toMatchObject({
      edge_id: 'E2',
      from_node_id: '3',
      to_node_id: '1',
      is_closed: true,
    })
    expect(route.features.map((feature) => [
      feature.properties.edge_id,
      feature.properties.route_index,
    ])).toEqual([['E2', 0], ['E1', 1]])
  })

  it('uses frozen road-path geometry when an aggregate landmark edge provides it', () => {
    const aggregate = edge('AGG', '1', '2', 'Road path')
    aggregate.attributes.path_coordinates_json = JSON.stringify([
      [106.75, 10.85],
      [106.7505, 10.8507],
      [106.751, 10.851],
    ])
    const payload = { ...graph, edges: [aggregate] }

    expect(buildEdgeFeatureCollection(payload).features[0].geometry.coordinates).toEqual([
      [106.75, 10.85],
      [106.7505, 10.8507],
      [106.751, 10.851],
    ])
  })
})

describe('basemap click snapping', () => {
  it('selects the nearest topology node only inside the threshold', () => {
    const snap = findNearestGraphNode(graph, 106.75102, 10.85102, 100)

    expect(snap?.nodeId).toBe('2')
    expect(snap?.distanceM).toBeLessThan(5)
    expect(findNearestGraphNode(graph, 106.8, 10.9, 20)).toBeNull()
  })

  it('ignores nodes explicitly marked as not selectable', () => {
    const hidden = node('hidden', 'Hidden', 10.851, 106.751)
    hidden.attributes.selectable = false
    const payload = { ...graph, nodes: [hidden, graph.nodes[0]] }

    expect(findNearestGraphNode(payload, 106.751, 10.851, 200)?.nodeId).toBe('1')
  })
})

describe('capacity graph conversion', () => {
  it('materializes 3229 nodes and 5057 edges without dropping selectable topology', () => {
    const nodes = Array.from({ length: 3229 }, (_, index) => node(
      `C${index}`,
      `UTraffic node ${index}`,
      10.82 + (index % 60) * 0.0005,
      106.72 + Math.floor(index / 60) * 0.0005,
    ))
    const edges = Array.from({ length: 5057 }, (_, index) => edge(
      `CE${index}`,
      `C${index % nodes.length}`,
      `C${(index + 1) % nodes.length}`,
      'Capacity Road',
    ))
    const payload: GraphPayload = { ...graph, nodes, edges, active_edge_count: edges.length }

    expect(buildNodeFeatureCollection(payload).features).toHaveLength(3229)
    expect(buildEdgeFeatureCollection(payload).features).toHaveLength(5057)
  })
})
