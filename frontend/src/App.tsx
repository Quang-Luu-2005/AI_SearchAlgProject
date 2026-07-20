import { useState } from 'react'
import { MetricCard } from './features/dashboard/MetricCard'
import { RouteMap } from './features/map/RouteMap'
import { PROJECT_NAME } from './lib/project'

type Scenario = 'OFFPEAK_BALANCED' | 'HEAVY_RAIN_SAFE'

const scenarioView = {
  OFFPEAK_BALANCED: {
    label: 'Ngoài giờ · Cân bằng',
    path: 'N01 → N02 → N06',
    distance: '2,50 km',
    eta: '5,6 phút',
    explored: '4 nút',
    explanation:
      'Tuyến ngắn qua N02 được chọn vì cạnh trũng chưa bị đóng và có tổng chi phí thấp nhất.',
  },
  HEAVY_RAIN_SAFE: {
    label: 'Mưa lớn · An toàn',
    path: 'N01 → N02 → N04 → N06',
    distance: '3,00 km',
    eta: '7,9 phút',
    explored: '5 nút',
    explanation:
      'Cạnh N02 → N06 bị đóng trong fixture mưa lớn. Tuyến chuyển qua N04 dù dài hơn để tránh rủi ro ngập.',
  },
} as const

export function App() {
  const [scenario, setScenario] = useState<Scenario>('OFFPEAK_BALANCED')
  const [hasRun, setHasRun] = useState(false)
  const view = scenarioView[scenario]

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label={PROJECT_NAME}>
          <span className="brand-mark">FR</span>
          <span>
            <strong>{PROJECT_NAME}</strong>
            <small>Explainable urban routing</small>
          </span>
        </a>
        <div className="status-cluster">
          <span className="status-dot" />
          Khung dự án v0.1
          <span className="badge badge-warning">SIMULATED</span>
        </div>
      </header>

      <main id="top" className="workspace">
        <aside className="control-panel">
          <div className="eyebrow">Thiết lập hành trình</div>
          <h1>Tìm tuyến giao hàng</h1>
          <p className="intro">Chọn điều kiện để xem route fixture thay đổi trước khi graph OSM v1.0 hoàn tất.</p>

          <label>
            Điểm xuất phát
            <select defaultValue="N01">
              <option value="N01">Kho Linh Trung</option>
            </select>
          </label>

          <label>
            Điểm đến
            <select defaultValue="N06">
              <option value="N06">Điểm giao Linh Đông</option>
            </select>
          </label>

          <label>
            Thuật toán
            <select defaultValue="A_STAR">
              <option value="A_STAR">A* Search</option>
              <option value="UCS">Uniform Cost Search</option>
              <option value="BFS">Breadth-First Search</option>
              <option value="DFS">Depth-First Search</option>
            </select>
          </label>

          <fieldset>
            <legend>Kịch bản</legend>
            {(Object.keys(scenarioView) as Scenario[]).map((scenarioId) => (
              <label className="scenario-option" key={scenarioId}>
                <input
                  type="radio"
                  name="scenario"
                  value={scenarioId}
                  checked={scenario === scenarioId}
                  onChange={() => {
                    setScenario(scenarioId)
                    setHasRun(false)
                  }}
                />
                <span>
                  <strong>{scenarioView[scenarioId].label}</strong>
                  <small>{scenarioId}</small>
                </span>
              </label>
            ))}
          </fieldset>

          <button className="run-button" type="button" onClick={() => setHasRun(true)}>
            Chạy mô phỏng fixture
          </button>
          <p className="control-note">Backend search API là bước kế tiếp; màn hình này xác nhận layout và data contract.</p>
        </aside>

        <section className="results-panel" aria-live="polite">
          <div className="results-heading">
            <div>
              <div className="eyebrow">Kết quả xem trước</div>
              <h2>{view.path}</h2>
            </div>
            <span className={hasRun ? 'run-state active' : 'run-state'}>
              {hasRun ? 'Đã phát trace mẫu' : 'Sẵn sàng'}
            </span>
          </div>

          <div className="map-frame">
            <RouteMap scenario={scenario} />
            <div className="legend">
              <span><i className="line final" />Tuyến chọn</span>
              <span><i className="line graph" />Cạnh graph</span>
              <span><i className="node" />Node</span>
            </div>
          </div>

          <div className="metrics-grid">
            <MetricCard label="Khoảng cách" value={view.distance} detail="fixture" />
            <MetricCard label="ETA" value={view.eta} detail="free-flow" />
            <MetricCard label="Đã mở rộng" value={view.explored} detail="trace mẫu" />
            <MetricCard label="Bảo đảm" value="Optimal*" detail="khi heuristic hợp lệ" />
          </div>

          <article className="explanation-card">
            <span className="explanation-icon">i</span>
            <div>
              <strong>Vì sao chọn tuyến này?</strong>
              <p>{view.explanation}</p>
            </div>
          </article>
        </section>
      </main>
    </div>
  )
}

