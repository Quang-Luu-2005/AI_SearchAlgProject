import { describe, expect, it } from 'vitest'
import { summarizeComparison } from './comparison'
import type { SearchResult } from './search'

function result(
  algorithm: SearchResult['algorithm'],
  cost: number,
  distance: number,
  time: number,
  path: string[],
): SearchResult {
  return {
    algorithm, scenario: 'S', data_status: 'SIMULATED', path, edge_ids: [],
    metrics: { distance_m: distance * 1000, distance_km: distance, estimated_time_min: time, total_cost: cost, explored_nodes: 1, processing_time_ms: 1 },
    trace: [], guarantee: 'TEST', explanation: '', edge_breakdown: [], limitations: [],
  }
}

describe('summarizeComparison', () => {
  it('identifies weighted-cost, distance, time and distinct-route leaders', () => {
    const insight = summarizeComparison([
      result('UCS', 1, 5, 9, ['A', 'B']),
      result('BFS', 2, 3, 8, ['A', 'C']),
      result('GREEDY', 3, 4, 2, ['A', 'C']),
    ])

    expect(insight?.bestCost.algorithm).toBe('UCS')
    expect(insight?.shortest.algorithm).toBe('BFS')
    expect(insight?.fastest.algorithm).toBe('GREEDY')
    expect(insight?.distinctRouteCount).toBe(2)
  })
})
