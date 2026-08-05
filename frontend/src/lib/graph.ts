export type GraphSummary = {
  graph_id: string
  label: string
  data_status: string
  node_count: number
  edge_count: number
  scenario_ids: string[]
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
