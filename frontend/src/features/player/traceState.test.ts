import { describe, expect, it } from 'vitest'
import { deriveTraceVisualState } from './traceState'
import type { TraceEvent } from '../../lib/search'

const events: TraceEvent[] = [
  { step: 1, kind: 'OPEN', node_id: 'A', parent_id: null, g_cost: 0, h_cost: 2, details: {} },
  { step: 2, kind: 'EXPAND', node_id: 'A', parent_id: null, g_cost: 0, h_cost: 2, details: {} },
  { step: 3, kind: 'RELAX', node_id: 'B', parent_id: 'A', g_cost: 1, h_cost: 1, details: {} },
  { step: 4, kind: 'CLOSE', node_id: 'A', parent_id: null, g_cost: 0, h_cost: 2, details: {} },
  { step: 5, kind: 'EXPAND', node_id: 'B', parent_id: 'A', g_cost: 1, h_cost: 1, details: {} },
]

describe('deriveTraceVisualState', () => {
  it('distinguishes frontier, current and closed nodes', () => {
    expect(deriveTraceVisualState(events, 3)).toEqual({
      frontierNodeIds: ['B'], closedNodeIds: [], currentNodeId: 'A',
    })
    expect(deriveTraceVisualState(events, 5)).toEqual({
      frontierNodeIds: [], closedNodeIds: ['A'], currentNodeId: 'B',
    })
  })
})
