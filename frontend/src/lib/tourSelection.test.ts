import { describe, expect, it } from 'vitest'
import { addTourStop, MAX_TOUR_STOPS } from './tourSelection'

describe('tour stop selection', () => {
  it('appends a unique stop without mutating the current selection', () => {
    const current = ['N02', 'N03']

    const result = addTourStop(current, 'N01', 'N04')

    expect(result).toEqual({ stops: ['N02', 'N03', 'N04'], status: 'ADDED' })
    expect(current).toEqual(['N02', 'N03'])
  })

  it.each([
    ['N01', ['N02'], 'DEPOT_SELECTED'],
    ['N02', ['N02'], 'DUPLICATE'],
  ] as const)('rejects invalid stop %s', (nodeId, current, status) => {
    expect(addTourStop(current, 'N01', nodeId)).toEqual({ stops: [...current], status })
  })

  it('rejects an eleventh stop', () => {
    const current = Array.from({ length: MAX_TOUR_STOPS }, (_, index) => `N${index + 2}`)

    expect(addTourStop(current, 'N01', 'N99')).toEqual({
      stops: current,
      status: 'LIMIT_REACHED',
    })
  })
})
