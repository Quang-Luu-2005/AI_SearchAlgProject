export type Algorithm = 'UCS' | 'A_STAR'
export type AlgorithmSelection = '' | Algorithm | 'COMPARE' | 'HELD_KARP' | 'NEAREST_NEIGHBOR' | 'OPTIMIZE_TOUR'


export type LocationItem = {
  point_id: string | null
  node_id: string
  name: string
  node_type: string | null
  latitude: number | null
  longitude: number | null
  data_status: string
}

export type ScenarioItem = {
  scenario_id: string
  traffic_scenario: string | null
  cost_preset: string | null
  weights: Record<string, number>
  closed_edge_ids: string[]
  data_status: string
}

export type TraceEvent = {
  step: number
  kind: string
  node_id: string
  parent_id: string | null
  g_cost: number | null
  h_cost: number | null
  details: Record<string, unknown>
}

export type SearchResult = {
  algorithm: Algorithm
  scenario: string
  data_status: string
  path: string[]
  edge_ids: string[]
  metrics: {
    distance_m: number
    distance_km: number
    estimated_time_min: number
    total_cost: number
    explored_nodes: number
    processing_time_ms: number
  }
  trace: TraceEvent[]
  guarantee: string
  explanation: string
  edge_breakdown: Array<{
    edge_id: string
    distance_km: number
    travel_time_min: number
    traffic_penalty: number
    flood_risk: number
    total_cost: number | null
    is_closed: boolean
  }>
  limitations: string[]
}

type SearchInput = {
  graph_id: string
  start: string
  goal: string
  scenario: string
}

async function requestJson<T>(
  url: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(url, init)
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail ?? `Yêu cầu thất bại (${response.status})`)
  }
  return response.json() as Promise<T>
}

function graphQuery(graphId: string): string {
  return new URLSearchParams({ graph_id: graphId }).toString()
}

export function fetchLocations(
  graphId: string,
  signal?: AbortSignal,
): Promise<{ graph_id: string; data_status: string; locations: LocationItem[] }> {
  return requestJson(`/api/v1/locations?${graphQuery(graphId)}`, { signal })
}

export function fetchScenarios(
  graphId: string,
  signal?: AbortSignal,
): Promise<{ graph_id: string; data_status: string; scenarios: ScenarioItem[] }> {
  return requestJson(`/api/v1/scenarios?${graphQuery(graphId)}`, { signal })
}

export function runSearch(
  input: SearchInput & { algorithm: Algorithm },
  signal?: AbortSignal,
): Promise<SearchResult> {
  return requestJson('/api/v1/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
    signal,
  })
}

export function runComparison(
  input: SearchInput,
  signal?: AbortSignal,
): Promise<{
  start: string
  goal: string
  scenario: string
  results: SearchResult[]
}> {
  return requestJson('/api/v1/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...input, algorithms: ['UCS', 'A_STAR'] }),
    signal,
  })
}

export type TourLeg = {
  from_node_id: string
  to_node_id: string
  path: string[]
  edge_ids: string[]
  distance_m: number
  distance_km: number
  travel_time_min: number
  total_cost: number
}

export type TourComparison = {
  held_karp_cost: number
  nearest_neighbor_cost: number
  approximation_gap_percent: number
}

export type OptimizeTourResult = {
  depot: string
  scenario: string
  data_status: string
  visit_order: string[]
  full_path: string[]
  edge_ids: string[]
  total_distance_m: number
  total_distance_km: number
  estimated_time_min: number
  total_cost: number
  comparison: TourComparison
  legs: TourLeg[]
  guarantee: string
  explanation: string
  limitations: string[]
}

export type OptimizeTourInput = {
  graph_id: string
  depot: string
  stops: string[]
  scenario: string
  algorithm?: string
  tour_algorithm?: string
  return_to_depot?: boolean
}

export function optimizeTour(
  input: OptimizeTourInput,
  signal?: AbortSignal,
): Promise<OptimizeTourResult> {
  return requestJson('/api/v1/optimize-tour', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
    signal,
  })
}

