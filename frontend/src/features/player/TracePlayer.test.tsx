import { describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TracePlayer } from './TracePlayer'
import type { TraceEvent } from '../../lib/search'

const mockTrace: TraceEvent[] = [
  { step: 1, kind: 'OPEN', node_id: 'N01', parent_id: null, g_cost: 0, h_cost: 10, details: {} },
  { step: 2, kind: 'EXPAND', node_id: 'N02', parent_id: 'N01', g_cost: 5, h_cost: 5, details: {} },
  { step: 3, kind: 'GOAL', node_id: 'N03', parent_id: 'N02', g_cost: 10, h_cost: 0, details: {} },
]

describe('TracePlayer component', () => {
  it('renders step counter, event info, and controls', () => {
    const { unmount } = render(
      <TracePlayer
        trace={mockTrace}
        currentStep={1}
        isPlaying={false}
        playbackSpeed={1}
        onPlayToggle={vi.fn()}
        onNextStep={vi.fn()}
        onPreviousStep={vi.fn()}
        onReset={vi.fn()}
        onStepChange={vi.fn()}
        onSpeedChange={vi.fn()}
        lang="vi"
      />,
    )

    expect(screen.getByText('Bước')).toBeInTheDocument()
    expect(screen.getByText('1 / 3')).toBeInTheDocument()
    expect(screen.getByText('OPEN')).toBeInTheDocument()
    expect(screen.getByText('N01')).toBeInTheDocument()
    unmount()
  })

  it('triggers onPlayToggle when Play button is clicked', () => {
    const handlePlayToggle = vi.fn()
    const { unmount } = render(
      <TracePlayer
        trace={mockTrace}
        currentStep={1}
        isPlaying={false}
        playbackSpeed={1}
        onPlayToggle={handlePlayToggle}
        onNextStep={vi.fn()}
        onPreviousStep={vi.fn()}
        onReset={vi.fn()}
        onStepChange={vi.fn()}
        onSpeedChange={vi.fn()}
        lang="vi"
      />,
    )

    const playBtn = screen.getByRole('button', { name: 'Phát' })
    fireEvent.click(playBtn)
    expect(handlePlayToggle).toHaveBeenCalledTimes(1)
    unmount()
  })

  it('triggers onNextStep and onPreviousStep when clicked', () => {
    const handleNext = vi.fn()
    const handlePrev = vi.fn()

    const { unmount } = render(
      <TracePlayer
        trace={mockTrace}
        currentStep={2}
        isPlaying={false}
        playbackSpeed={1}
        onPlayToggle={vi.fn()}
        onNextStep={handleNext}
        onPreviousStep={handlePrev}
        onReset={vi.fn()}
        onStepChange={vi.fn()}
        onSpeedChange={vi.fn()}
        lang="vi"
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Tiến' }))
    expect(handleNext).toHaveBeenCalledTimes(1)

    fireEvent.click(screen.getByRole('button', { name: 'Lùi' }))
    expect(handlePrev).toHaveBeenCalledTimes(1)
    unmount()
  })

  it('triggers onReset when reset button is clicked', () => {
    const handleReset = vi.fn()
    const { unmount } = render(
      <TracePlayer
        trace={mockTrace}
        currentStep={3}
        isPlaying={false}
        playbackSpeed={1}
        onPlayToggle={vi.fn()}
        onNextStep={vi.fn()}
        onPreviousStep={vi.fn()}
        onReset={handleReset}
        onStepChange={vi.fn()}
        onSpeedChange={vi.fn()}
        lang="vi"
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Reset' }))
    expect(handleReset).toHaveBeenCalledTimes(1)
    unmount()
  })

  it('handles timeline slider scrubbing', () => {
    const handleStepChange = vi.fn()
    const { unmount } = render(
      <TracePlayer
        trace={mockTrace}
        currentStep={1}
        isPlaying={false}
        playbackSpeed={1}
        onPlayToggle={vi.fn()}
        onNextStep={vi.fn()}
        onPreviousStep={vi.fn()}
        onReset={vi.fn()}
        onStepChange={handleStepChange}
        onSpeedChange={vi.fn()}
        lang="vi"
      />,
    )

    const slider = screen.getByLabelText('Trace step slider')
    fireEvent.change(slider, { target: { value: '3' } })
    expect(handleStepChange).toHaveBeenCalledWith(3)
    unmount()
  })

  it('handles playback speed change', () => {
    const handleSpeedChange = vi.fn()
    const { unmount } = render(
      <TracePlayer
        trace={mockTrace}
        currentStep={1}
        isPlaying={false}
        playbackSpeed={1}
        onPlayToggle={vi.fn()}
        onNextStep={vi.fn()}
        onPreviousStep={vi.fn()}
        onReset={vi.fn()}
        onStepChange={vi.fn()}
        onSpeedChange={handleSpeedChange}
        lang="vi"
      />,
    )

    const select = screen.getByLabelText('Trace playback speed')
    fireEvent.change(select, { target: { value: '5' } })
    expect(handleSpeedChange).toHaveBeenCalledWith(5)
    unmount()
  })
})
