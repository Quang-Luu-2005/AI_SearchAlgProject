import type { TourComparison } from '../../lib/search'

export type BenchmarkChartsProps = {
  comparison?: TourComparison | null
  singleMetrics?: {
    distance_km: number
    estimated_time_min: number
    total_cost: number
    explored_nodes: number
    processing_time_ms: number
  } | null
}

export function BenchmarkCharts({ comparison, singleMetrics }: BenchmarkChartsProps) {
  if (!comparison && !singleMetrics) return null

  if (comparison) {
    const hkCost = comparison.held_karp_cost
    const nnCost = comparison.nearest_neighbor_cost
    const maxCost = Math.max(hkCost, nnCost, 1)

    const hkWidth = `${Math.round((hkCost / maxCost) * 100)}%`
    const nnWidth = `${Math.round((nnCost / maxCost) * 100)}%`

    return (
      <div className="benchmark-charts-card" aria-label="Biểu đồ so sánh thuật toán">
        <div className="charts-header">
          <h4>📊 Biểu đồ Trực quan hóa So sánh Multi-Stop Tour</h4>
          <span className="gap-pill">
            Approximation Gap: +{comparison.approximation_gap_percent.toFixed(2)}%
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
    <div className="benchmark-charts-card" aria-label="Bảng chỉ số tìm đường">
      <div className="charts-header">
        <h4>📊 Bảng Thống kê Chỉ số Thuật toán</h4>
      </div>
      <div className="metrics-summary-grid">
        <div className="summary-metric-box">
          <span>Tổng khoảng cách</span>
          <strong>{singleMetrics?.distance_km.toFixed(2)} km</strong>
        </div>
        <div className="summary-metric-box">
          <span>Thời gian dự kiến (ETA)</span>
          <strong>{singleMetrics?.estimated_time_min.toFixed(2)} phút</strong>
        </div>
        <div className="summary-metric-box">
          <span>Tổng chi phí (Cost)</span>
          <strong>{singleMetrics?.total_cost.toFixed(3)}</strong>
        </div>
        <div className="summary-metric-box">
          <span>Số node đã mở rộng</span>
          <strong>{singleMetrics?.explored_nodes} nodes</strong>
        </div>
      </div>
    </div>
  )
}
