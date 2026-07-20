import { describe, expect, it } from 'vitest'
import { COST_PRESETS, PROJECT_NAME } from './project'

describe('project configuration', () => {
  it('uses the expected project identity', () => {
    expect(PROJECT_NAME).toBe('FloodRoute HCMC')
  })

  it.each(Object.entries(COST_PRESETS))('%s weights sum to one', (_, weights) => {
    expect(Object.values(weights).reduce((sum, value) => sum + value, 0)).toBeCloseTo(1)
  })
})

