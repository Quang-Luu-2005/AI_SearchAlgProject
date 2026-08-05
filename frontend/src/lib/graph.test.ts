import { describe, expect, it } from 'vitest'
import { buildGraphUrl } from './graph'

describe('graph API paths', () => {
  it('keeps graph folders as safe path segments', () => {
    expect(buildGraphUrl('graph_examples_v0.1/simple_path')).toBe(
      '/api/v1/graphs/graph_examples_v0.1/simple_path',
    )
  })

  it('encodes scenario query values', () => {
    expect(buildGraphUrl('toy_graph_v0.1', 'HEAVY RAIN')).toBe(
      '/api/v1/graphs/toy_graph_v0.1?scenario_id=HEAVY+RAIN',
    )
  })
})
