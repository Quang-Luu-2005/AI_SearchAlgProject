import type { SearchResult } from './search'

export type ComparisonInsight = {
  bestCost: SearchResult
  shortest: SearchResult
  fastest: SearchResult
  distinctRouteCount: number
}

export function summarizeComparison(results: SearchResult[]): ComparisonInsight | null {
  if (!results.length) return null
  const minimumBy = (field: (result: SearchResult) => number) => [...results].sort((left, right) => (
    field(left) - field(right) || left.algorithm.localeCompare(right.algorithm)
  ))[0]
  return {
    bestCost: minimumBy((result) => result.metrics.total_cost),
    shortest: minimumBy((result) => result.metrics.distance_km),
    fastest: minimumBy((result) => result.metrics.estimated_time_min),
    distinctRouteCount: new Set(results.map((result) => result.path.join('>'))).size,
  }
}
