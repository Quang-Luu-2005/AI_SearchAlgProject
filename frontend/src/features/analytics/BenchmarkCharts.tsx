import type { TourComparison } from '../../lib/search'
import { t, type Language } from '../../lib/i18n'

export type BenchmarkChartsProps = {
  comparison?: TourComparison | null
  singleMetrics?: {
    distance_km: number
    estimated_time_min: number
    total_cost: number
    explored_nodes: number
    processing_time_ms: number
  } | null
  lang?: Language
}

export function BenchmarkCharts({ comparison, singleMetrics, lang = 'en' }: BenchmarkChartsProps) {
  if (!comparison && !singleMetrics) return null

  if (comparison) {
    const hkCost = comparison.held_karp_cost
    const nnCost = comparison.nearest_neighbor_cost
    const maxCost = Math.max(hkCost, nnCost, 1)

    const hkWidth = `${Math.round((hkCost / maxCost) * 100)}%`
    const nnWidth = `${Math.round((nnCost / maxCost) * 100)}%`

    return (
      <div className="benchmark-charts-card" aria-label={t('charts_title', lang)}>
        <div className="charts-header">
          <h4>{t('charts_title', lang)}</h4>
          <span className="gap-pill">
            {t('gap_label', lang)}: +{comparison.approximation_gap_percent.toFixed(2)}%
          </span>
        </div>

        <div className="chart-bar-group">
          <div className="chart-row">
            <div className="chart-label">
              <strong>Held-Karp DP (Exact)</strong>
              <small>{hkCost.toFixed(3)} cost</small>
            </div>
            <div className="chart-track">
              <div className="chart-fill fill--hk" style={{ width: hkWidth }}>
                <span className="fill-value">{hkCost.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div className="chart-row">
            <div className="chart-label">
              <strong>Nearest Neighbor (Greedy)</strong>
              <small>{nnCost.toFixed(3)} cost</small>
            </div>
            <div className="chart-track">
              <div className="chart-fill fill--nn" style={{ width: nnWidth }}>
                <span className="fill-value">{nnCost.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="benchmark-charts-card" aria-label={t('metrics_title', lang)}>
      <div className="charts-header">
        <h4>{t('metrics_title', lang)}</h4>
      </div>
      <div className="metrics-summary-grid">
        <div className="summary-metric-box">
          <span>{t('dist_total', lang)}</span>
          <strong>{singleMetrics?.distance_km.toFixed(2)} km</strong>
        </div>
        <div className="summary-metric-box">
          <span>{t('time_eta', lang)}</span>
          <strong>{singleMetrics?.estimated_time_min.toFixed(2)} {t('minutes', lang)}</strong>
        </div>
        <div className="summary-metric-box">
          <span>{t('total_cost', lang)}</span>
          <strong>{singleMetrics?.total_cost.toFixed(3)}</strong>
        </div>
        <div className="summary-metric-box">
          <span>{t('explored_nodes', lang)}</span>
          <strong>{singleMetrics?.explored_nodes} {t('nodes_count', lang)}</strong>
        </div>
      </div>
    </div>
  )
}
