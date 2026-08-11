import type { ChangeEvent } from 'react'
import type { TraceEvent } from '../../lib/search'
import { t, type Language } from '../../lib/i18n'

export type TracePlayerProps = {
  trace: TraceEvent[]
  currentStep: number
  isPlaying: boolean
  playbackSpeed: number
  onPlayToggle: () => void
  onNextStep: () => void
  onPreviousStep: () => void
  onReset: () => void
  onStepChange: (step: number) => void
  onSpeedChange: (speed: number) => void
  lang?: Language
}

export function TracePlayer({
  trace,
  currentStep,
  isPlaying,
  playbackSpeed,
  onPlayToggle,
  onNextStep,
  onPreviousStep,
  onReset,
  onStepChange,
  onSpeedChange,
  lang = 'en',
}: TracePlayerProps) {
  const totalSteps = Math.max(trace.length, 1)
  const safeStep = Math.min(Math.max(currentStep, 1), totalSteps)
  const currentEvent = trace[safeStep - 1] ?? null

  const isAtEnd = safeStep >= totalSteps
  const isAtStart = safeStep <= 1

  function handleSliderChange(event: ChangeEvent<HTMLInputElement>) {
    onStepChange(Number.parseInt(event.target.value, 10))
  }

  function handleSpeedSelect(event: ChangeEvent<HTMLSelectElement>) {
    onSpeedChange(Number.parseFloat(event.target.value))
  }

  return (
    <section className="trace-player-bar" aria-label="Trace Player">
      <div className="player-main-controls">
        <button
          type="button"
          className="player-btn btn-reset"
          title={t('trace_reset', lang)}
          aria-label={t('trace_reset', lang)}
          onClick={onReset}
          disabled={isAtStart && !isPlaying}
        >
          ⏮
        </button>

        <button
          type="button"
          className="player-btn btn-prev"
          title={t('trace_prev', lang)}
          aria-label={t('trace_prev', lang)}
          onClick={onPreviousStep}
          disabled={isAtStart || isPlaying}
        >
          ◀
        </button>

        <button
          type="button"
          className={`player-btn btn-play ${isPlaying ? 'is-playing' : ''}`}
          title={isPlaying ? t('trace_pause', lang) : t('trace_play', lang)}
          aria-label={isPlaying ? t('trace_pause', lang) : t('trace_play', lang)}
          onClick={onPlayToggle}
        >
          {isPlaying ? `⏸ ${t('trace_pause', lang)}` : isAtEnd ? `🔄 ${t('trace_play', lang)}` : `▶ ${t('trace_play', lang)}`}
        </button>

        <button
          type="button"
          className="player-btn btn-next"
          title={t('trace_next', lang)}
          aria-label={t('trace_next', lang)}
          onClick={onNextStep}
          disabled={isAtEnd || isPlaying}
        >
          ▶
        </button>
      </div>

      <div className="player-timeline">
        <div className="step-counter-badge">
          <span>{t('trace_step', lang)}</span>
          <strong>{safeStep} / {totalSteps}</strong>
        </div>

        <input
          type="range"
          className="step-slider"
          min={1}
          max={totalSteps}
          value={safeStep}
          onChange={handleSliderChange}
          aria-label="Trace step slider"
        />

        <div className="speed-selector-group">
          <label htmlFor="speed-select">{t('trace_speed', lang)}:</label>
          <select
            id="speed-select"
            className="speed-select"
            value={playbackSpeed}
            onChange={handleSpeedSelect}
            aria-label="Trace playback speed"
          >
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={5}>5x</option>
            <option value={10}>10x</option>
          </select>
        </div>
      </div>

      {currentEvent && (
        <div className="event-inspector" aria-label="Thông tin chi tiết sự kiện hiện tại">
          <div className="event-tag-group">
            <span className={`event-kind-tag event-kind--${currentEvent.kind.toLowerCase()}`}>
              {currentEvent.kind}
            </span>
            <strong className="event-node-id">{currentEvent.node_id}</strong>
          </div>
          <div className="event-details-text">
            {currentEvent.parent_id && <span>Parent: <code>{currentEvent.parent_id}</code></span>}
            {currentEvent.g_cost !== null && currentEvent.g_cost !== undefined && (
              <span>g={currentEvent.g_cost.toFixed(2)}</span>
            )}
            {currentEvent.h_cost !== null && currentEvent.h_cost !== undefined && (
              <span>h={currentEvent.h_cost.toFixed(2)}</span>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
