import type { ChangeEvent } from 'react'
import type { TraceEvent } from '../../lib/search'

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
    <section className="trace-player-bar" aria-label="Bộ điều khiển Trace Player">
      <div className="player-main-controls">
        <button
          type="button"
          className="player-btn btn-reset"
          title="Reset về bước 1"
          aria-label="Reset về bước 1"
          onClick={onReset}
          disabled={isAtStart && !isPlaying}
        >
          ⏮
        </button>

        <button
          type="button"
          className="player-btn btn-prev"
          title="Bước trước (Previous Step)"
          aria-label="Bước trước"
          onClick={onPreviousStep}
          disabled={isAtStart || isPlaying}
        >
          ◀
        </button>

        <button
          type="button"
          className={`player-btn btn-play ${isPlaying ? 'is-playing' : ''}`}
          title={isPlaying ? 'Tạm dừng (Pause)' : 'Phát tự động (Play)'}
          aria-label={isPlaying ? 'Tạm dừng' : 'Phát tự động'}
          onClick={onPlayToggle}
        >
          {isPlaying ? '⏸ Tạm dừng' : isAtEnd ? '🔄 Phát lại' : '▶ Phát Trace'}
        </button>

        <button
          type="button"
          className="player-btn btn-next"
          title="Bước kế tiếp (Next Step)"
          aria-label="Bước kế tiếp"
          onClick={onNextStep}
          disabled={isAtEnd || isPlaying}
        >
          ▶
        </button>
      </div>

      <div className="player-timeline">
        <div className="step-counter-badge">
          <span>Bước</span>
          <strong>{safeStep} / {totalSteps}</strong>
        </div>

        <input
          type="range"
          className="step-slider"
          min={1}
          max={totalSteps}
          value={safeStep}
          onChange={handleSliderChange}
          aria-label="Thanh trượt thời gian trace"
        />

        <div className="speed-selector-group">
          <label htmlFor="speed-select">Tốc độ:</label>
          <select
            id="speed-select"
            className="speed-select"
            value={playbackSpeed}
            onChange={handleSpeedSelect}
            aria-label="Tốc độ phát trace"
          >
            <option value={1}>1x (Chậm)</option>
            <option value={2}>2x (Vừa)</option>
            <option value={5}>5x (Nhanh)</option>
            <option value={10}>10x (Siêu nhanh)</option>
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
