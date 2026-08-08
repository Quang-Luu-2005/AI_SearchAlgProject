import { describe, expect, it } from 'vitest'
import { buildGraphUrl, preferredGraphId, type GraphSummary } from './graph'

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

describe('default dataset selection', () => {
  it('prefers the released Thu Duc processed dataset', () => {
    const summary = (graph_id: string, dataset_kind: 'fixture' | 'processed'): GraphSummary => ({
      graph_id,
      dataset_kind,
      label: graph_id,
      data_status: dataset_kind === 'processed' ? 'MIXED' : 'SIMULATED',
      snapshot_date: null,
      real_time: false,
      source_ids: [],
      limitations: [],
      routing_dataset_status: null,
      node_count: 1,
      edge_count: 1,
      scenario_ids: [],
    })
    expect(preferredGraphId([
      summary('toy_graph_v0.1', 'fixture'),
      summary('processed/thu_duc_market_v1.0.0', 'processed'),
      summary('processed/thu_duc_landmarks_v1.0.0', 'processed'),
    ])).toBe('processed/thu_duc_landmarks_v1.0.0')
  })
})
