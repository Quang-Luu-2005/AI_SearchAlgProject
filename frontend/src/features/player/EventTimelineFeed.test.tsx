import { describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { EventTimelineFeed } from './EventTimelineFeed'
import type { TraceEvent } from '../../lib/search'

const mockTrace: TraceEvent[] = [
  { step: 1, kind: 'OPEN', node_id: 'N01', parent_id: null, g_cost: 0, h_cost: 10, details: {} },
  { step: 2, kind: 'EXPAND', node_id: 'N02', parent_id: 'N01', g_cost: 5, h_cost: 5, details: {} },
]

describe('EventTimelineFeed component', () => {
  it('renders trace feed items correctly', () => {
    const { unmount } = render(
      <EventTimelineFeed trace={mockTrace} currentStep={1} onStepSelect={vi.fn()} />,
    )

    expect(screen.getByText('📋 Nhật ký Trace Events (2 bước)')).toBeInTheDocument()
    expect(screen.getByText('N01')).toBeInTheDocument()
    expect(screen.getByText('N02')).toBeInTheDocument()
    unmount()
  })

  it('triggers onStepSelect when an item is clicked', () => {
    const handleStepSelect = vi.fn()
    const { unmount } = render(
      <EventTimelineFeed trace={mockTrace} currentStep={1} onStepSelect={handleStepSelect} />,
    )

    const secondItem = screen.getByText('N02').closest('button')
    expect(secondItem).not.toBeNull()
    fireEvent.click(secondItem!)

    expect(handleStepSelect).toHaveBeenCalledWith(2)
    unmount()
  })
})
