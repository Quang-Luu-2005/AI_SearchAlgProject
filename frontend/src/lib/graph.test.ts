import { describe, expect, it } from 'vitest'
import { buildGraphUrl, interactiveGraphs, preferredGraphId, type GraphSummary } from './graph'

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
      summary('processed/thu_duc_landmarks_v1.0.3', 'processed'),
    ])).toBe('processed/thu_duc_landmarks_v1.0.3')
  })

  it('keeps capacity-only graphs out of the interactive routing dropdown', () => {
    const graphs = [
      { graph_id: 'processed/thu_duc_landmarks_v1.0.3', routing_dataset_status: 'ACADEMIC_LANDMARK_DEMO' },
      { graph_id: 'processed/thu_duc_market_v1.0.0', routing_dataset_status: 'REVIEW_REQUIRED' },
      { graph_id: 'processed/thu_duc_core_capacity_v0.1.0', routing_dataset_status: 'CAPACITY_BENCHMARK_ONLY' },
    ] as GraphSummary[]

    expect(interactiveGraphs(graphs).map((item) => item.graph_id)).toEqual([
      'processed/thu_duc_landmarks_v1.0.3',
      'processed/thu_duc_market_v1.0.0',
    ])
  })
})
