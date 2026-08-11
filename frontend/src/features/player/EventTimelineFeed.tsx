import type { TraceEvent } from '../../lib/search'

export type EventTimelineFeedProps = {
  trace: TraceEvent[]
  currentStep: number
  onStepSelect: (step: number) => void
}

export function EventTimelineFeed({ trace, currentStep, onStepSelect }: EventTimelineFeedProps) {
  if (!trace.length) return null

  return (
    <div className="event-timeline-feed-card" aria-label="Danh sách các bước Trace tương tác">
      <div className="timeline-feed-header">
        <h4>📋 Nhật ký Trace Events ({trace.length} bước)</h4>
        <small>Click chọn bước để tua nhanh tới vị trí đó</small>
      </div>

      <div className="timeline-feed-list">
        {trace.map((event) => {
          const isActive = event.step === currentStep
          return (
            <button
              key={`${event.step}-${event.node_id}`}
              type="button"
              className={`timeline-feed-item ${isActive ? 'is-active' : ''}`}
              onClick={() => onStepSelect(event.step)}
            >
              <div className="feed-step-badge">#{event.step}</div>
              <span className={`feed-kind-tag feed-kind--${event.kind.toLowerCase()}`}>
                {event.kind}
              </span>
              <strong className="feed-node-id">{event.node_id}</strong>
              {event.parent_id && <small className="feed-parent-id">via {event.parent_id}</small>}
              <div className="feed-cost-metrics">
                {event.g_cost !== null && <span>g: {event.g_cost.toFixed(1)}</span>}
                {event.h_cost !== null && <span>h: {event.h_cost.toFixed(1)}</span>}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
