import type { FeatureCollection, MultiPolygon, Polygon } from 'geojson'

export type GraphSummary = {
  graph_id: string
  label: string
  data_status: string
  dataset_kind: 'fixture' | 'processed'
  snapshot_date: string | null
  real_time: boolean
  source_ids: string[]
  limitations: string[]
  routing_dataset_status: string | null
  node_count: number
  edge_count: number
  scenario_ids: string[]
}

export type ThuDucBoundary = FeatureCollection<Polygon | MultiPolygon> & {
  snapshot_date: string
  source_url: string
  source_id: string
  license: string
  attribution: string
  scope_note: string
}

export function interactiveGraphs(graphs: GraphSummary[]): GraphSummary[] {
  return graphs.filter((item) => item.routing_dataset_status !== 'CAPACITY_BENCHMARK_ONLY')
}

export function preferredGraphId(graphs: GraphSummary[], currentId = ''): string {
  return graphs.find((item) => item.graph_id === currentId)?.graph_id
    ?? graphs.find((item) => item.graph_id === 'processed/thu_duc_landmarks_v1.0.0')?.graph_id
    ?? graphs.find((item) => item.graph_id === 'processed/thu_duc_market_v1.0.0')?.graph_id
    ?? graphs.find((item) => item.graph_id === 'toy_graph_v0.1')?.graph_id
    ?? graphs[0]?.graph_id
    ?? ''
}

export type InvalidGraphSummary = {
  graph_id: string
  error: string
}

export type GraphNode = {
  node_id: string
  latitude: number | null
  longitude: number | null
  label: string
  attributes: Record<string, unknown>
}

export type GraphEdge = {
  edge_id: string
  from_node_id: string
  to_node_id: string
  distance_m: number
  free_flow_time_min: number
  is_closed: boolean
  attributes: Record<string, unknown>
}

export type GraphPayload = {
  graph_id: string
  directed: boolean
  data_status: string
  active_scenario_id: string | null
  metadata: Record<string, unknown>
  scenarios: Array<{ scenario_id: string; closed_edge_ids: string[] }>
  nodes: GraphNode[]
  edges: GraphEdge[]
  active_edge_count: number
}

export function buildGraphUrl(graphId: string, scenarioId = ''): string {
  const safeGraphId = graphId.split('/').map(encodeURIComponent).join('/')
  const query = scenarioId
    ? `?${new URLSearchParams({ scenario_id: scenarioId }).toString()}`
    : ''
  return `/api/v1/graphs/${safeGraphId}${query}`
}

async function getJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal })
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail ?? `Không thể tải dữ liệu (${response.status})`)
  }
  return response.json() as Promise<T>
}

export function fetchGraphCatalog(signal?: AbortSignal): Promise<{
  graphs: GraphSummary[]
  invalid_graphs: InvalidGraphSummary[]
}> {
  return getJson('/api/v1/graphs', signal)
}

export function fetchGraph(
  graphId: string,
  scenarioId = '',
  signal?: AbortSignal,
): Promise<GraphPayload> {
  return getJson(buildGraphUrl(graphId, scenarioId), signal)
}

export function fetchThuDucBoundary(signal?: AbortSignal): Promise<ThuDucBoundary> {
  return getJson('/api/v1/boundaries/thu-duc', signal)
}
