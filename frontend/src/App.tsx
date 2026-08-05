import { useEffect, useMemo, useState } from 'react'
import { MetricCard } from './features/dashboard/MetricCard'
import { RouteMap } from './features/map/RouteMap'
import {
  fetchGraph,
  fetchGraphCatalog,
  type GraphPayload,
  type GraphSummary,
  type InvalidGraphSummary,
} from './lib/graph'
import { PROJECT_NAME } from './lib/project'

export function App() {
  const [catalog, setCatalog] = useState<GraphSummary[]>([])
  const [invalidGraphs, setInvalidGraphs] = useState<InvalidGraphSummary[]>([])
  const [graphId, setGraphId] = useState('')
  const [scenarioId, setScenarioId] = useState('')
  const [graph, setGraph] = useState<GraphPayload | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [reloadVersion, setReloadVersion] = useState(0)
  const [catalogVersion, setCatalogVersion] = useState(0)

  const selectedSummary = useMemo(
    () => catalog.find((item) => item.graph_id === graphId),
    [catalog, graphId],
  )

  useEffect(() => {
    const controller = new AbortController()
    fetchGraphCatalog(controller.signal)
      .then(({ graphs, invalid_graphs }) => {
        setCatalog(graphs)
        setInvalidGraphs(invalid_graphs)
        const initial = (
          graphs.find((item) => item.graph_id === graphId)
          ?? graphs.find((item) => item.graph_id === 'toy_graph_v0.1')
          ?? graphs[0]
        )
        if (initial) {
          setGraphId(initial.graph_id)
          if (!initial.scenario_ids.includes(scenarioId)) {
            setScenarioId(initial.scenario_ids[0] ?? '')
          }
        } else {
          setLoading(false)
          setError('Không tìm thấy folder graph hợp lệ trong data/fixtures.')
        }
      })
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') {
          setLoading(false)
          setError(reason.message)
        }
      })
    return () => controller.abort()
  }, [catalogVersion])

  useEffect(() => {
    if (!graphId) return
    const controller = new AbortController()
    setLoading(true)
    setError('')
    fetchGraph(graphId, scenarioId, controller.signal)
      .then(setGraph)
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') setError(reason.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [graphId, scenarioId, reloadVersion])

  function selectGraph(nextGraphId: string) {
    const summary = catalog.find((item) => item.graph_id === nextGraphId)
    setGraphId(nextGraphId)
    setScenarioId(summary?.scenario_ids[0] ?? '')
  }

  const closedEdgeCount = graph?.edges.filter((edge) => edge.is_closed).length ?? 0

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label={PROJECT_NAME}>
          <span className="brand-mark">FR</span>
          <span>
            <strong>{PROJECT_NAME}</strong>
            <small>Graph dataset explorer</small>
          </span>
        </a>
        <div className="status-cluster">
          <span className="status-dot" />
          Graph Loader API
          <span className="badge badge-warning">SIMULATED</span>
        </div>
      </header>

      <main id="top" className="workspace">
        <aside className="control-panel">
          <div className="eyebrow">Nạp dữ liệu thông minh</div>
          <h1>Chọn graph folder</h1>
          <p className="intro">
            Backend tự tìm các folder hợp lệ trong <code>data/fixtures</code> và nạp CSV/JSON theo contract.
          </p>

          <label>
            Dataset folder
            <select
              value={graphId}
              onChange={(event) => selectGraph(event.target.value)}
              disabled={!catalog.length}
            >
              {catalog.map((item) => (
                <option key={item.graph_id} value={item.graph_id}>
                  {item.graph_id} ({item.node_count}N/{item.edge_count}E)
                </option>
              ))}
            </select>
          </label>

          <label>
            Scenario
            <select
              value={scenarioId}
              onChange={(event) => setScenarioId(event.target.value)}
              disabled={!selectedSummary?.scenario_ids.length}
            >
              {!selectedSummary?.scenario_ids.length && <option value="">Không có scenario</option>}
              {selectedSummary?.scenario_ids.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </label>

          <button
            className="run-button"
            type="button"
            onClick={() => {
              setCatalogVersion((version) => version + 1)
              setReloadVersion((version) => version + 1)
            }}
            disabled={!graphId || loading}
          >
            {loading ? 'Đang nạp…' : 'Quét và nạp lại'}
          </button>
          <p className="control-note">
            Folder tối thiểu cần <code>nodes.csv</code> và <code>edges.csv</code>;
            <code> scenarios.json</code> được tự động dùng nếu có.
          </p>
          {error && <p className="load-error" role="alert">{error}</p>}
          {invalidGraphs.length > 0 && (
            <div className="load-warning" role="status">
              <strong>{invalidGraphs.length} folder không hợp lệ</strong>
              {invalidGraphs.map((item) => (
                <small key={item.graph_id}>{item.graph_id}: {item.error}</small>
              ))}
            </div>
          )}
        </aside>

        <section className="results-panel" aria-live="polite">
          <div className="results-heading">
            <div>
              <div className="eyebrow">Graph đang hiển thị</div>
              <h2>{graph?.graph_id ?? 'Đang chờ dữ liệu'}</h2>
            </div>
            <span className={graph && !loading ? 'run-state active' : 'run-state'}>
              {loading ? 'Đang nạp' : graph ? 'Đã nạp' : 'Chưa có graph'}
            </span>
          </div>

          <div className="map-frame">
            {graph ? <RouteMap graph={graph} /> : <div className="map-placeholder">Chưa có dữ liệu bản đồ</div>}
            <div className="legend">
              <span><i className="line active-edge" />Cạnh đang mở</span>
              <span><i className="line closed-edge" />Cạnh bị đóng</span>
              <span><i className="node" />Node</span>
            </div>
          </div>

          <div className="metrics-grid">
            <MetricCard label="Node" value={String(graph?.nodes.length ?? 0)} detail="CSV" />
            <MetricCard label="Tổng edge" value={String(graph?.edges.length ?? 0)} detail="directed" />
            <MetricCard label="Edge đang mở" value={String(graph?.active_edge_count ?? 0)} detail={scenarioId || 'base'} />
            <MetricCard label="Edge bị đóng" value={String(closedEdgeCount)} detail={scenarioId || 'base'} />
          </div>

          <article className="explanation-card">
            <span className="explanation-icon">i</span>
            <div>
              <strong>Luồng dữ liệu</strong>
              <p>
                Folder → GraphLoader bất biến → FastAPI → React map. Cạnh đóng theo scenario vẫn được hiển thị bằng nét đứt màu đỏ.
              </p>
            </div>
          </article>
        </section>
      </main>
    </div>
  )
}
