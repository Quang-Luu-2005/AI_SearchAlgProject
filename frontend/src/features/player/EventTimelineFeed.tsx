import type { TraceEvent } from '../../lib/search'
import { t, type Language } from '../../lib/i18n'

export type EventTimelineFeedProps = {
  trace: TraceEvent[]
  currentStep: number
  onStepSelect: (step: number) => void
  lang?: Language
}

export function EventTimelineFeed({ trace, currentStep, onStepSelect, lang = 'en' }: EventTimelineFeedProps) {
  if (!trace.length) return null

  return (
    <div className="event-timeline-feed-card" aria-label={t('event_feed_title', lang, { count: trace.length })}>
      <div className="timeline-feed-header">
        <h4>{t('event_feed_title', lang, { count: trace.length })}</h4>
        <small>{t('event_feed_subtitle', lang)}</small>
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
              {event.parent_id && <small className="feed-parent-id">{t('via', lang)} {event.parent_id}</small>}
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
