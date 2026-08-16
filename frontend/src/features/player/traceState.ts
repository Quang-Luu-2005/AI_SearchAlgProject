import type { TraceEvent } from '../../lib/search'

export type TraceVisualState = {
  frontierNodeIds: string[]
  closedNodeIds: string[]
  currentNodeId: string | null
}

export function deriveTraceVisualState(
  trace: TraceEvent[],
  visibleSteps: number,
): TraceVisualState {
  const frontier = new Set<string>()
  const closed = new Set<string>()
  let currentNodeId: string | null = null

  for (const event of trace.slice(0, Math.max(0, visibleSteps))) {
    const kind = event.kind.toUpperCase()
    if (kind === 'OPEN' || kind === 'RELAX') {
      if (!closed.has(event.node_id)) frontier.add(event.node_id)
    } else if (kind === 'EXPAND') {
      frontier.delete(event.node_id)
      currentNodeId = event.node_id
    } else if (kind === 'CLOSE') {
      frontier.delete(event.node_id)
      closed.add(event.node_id)
      if (currentNodeId === event.node_id) currentNodeId = null
    } else if (kind === 'GOAL') {
      frontier.delete(event.node_id)
      currentNodeId = event.node_id
    } else if (kind === 'FAIL') {
      currentNodeId = null
    }
  }

  const sort = (values: Set<string>) => [...values].sort()
  return {
    frontierNodeIds: sort(frontier),
    closedNodeIds: sort(closed),
    currentNodeId,
  }
}
