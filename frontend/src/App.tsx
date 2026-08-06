import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { RouteMap } from './features/map/RouteMap'
import {
  fetchGraph,
  fetchGraphCatalog,
  type GraphPayload,
  type GraphSummary,
  type InvalidGraphSummary,
} from './lib/graph'
import {
  fetchLocations,
  fetchScenarios,
  runComparison,
  runSearch,
  type AlgorithmSelection,
  type LocationItem,
  type ScenarioItem,
  type SearchResult,
} from './lib/search'

function metric(value: number | undefined, digits = 1): string {
  return value === undefined ? '—' : value.toFixed(digits)
}

export function App() {
  const [catalog, setCatalog] = useState<GraphSummary[]>([])
  const [invalidGraphs, setInvalidGraphs] = useState<InvalidGraphSummary[]>([])
  const [graphId, setGraphId] = useState('')
  const [graph, setGraph] = useState<GraphPayload | null>(null)
  const [locations, setLocations] = useState<LocationItem[]>([])
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([])
  const [scenarioId, setScenarioId] = useState('')
  const [startId, setStartId] = useState('')
  const [goalId, setGoalId] = useState('')
  const [algorithm, setAlgorithm] = useState<AlgorithmSelection>('A_STAR')
  const [result, setResult] = useState<SearchResult | null>(null)
  const [comparisonResults, setComparisonResults] = useState<SearchResult[]>([])
  const [visiblePathEdgeCount, setVisiblePathEdgeCount] = useState(0)
  const [animatingPath, setAnimatingPath] = useState(false)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [reloadVersion, setReloadVersion] = useState(0)

  const selectedGraph = useMemo(
    () => catalog.find((item) => item.graph_id === graphId),
    [catalog, graphId],
  )
  const selectedScenario = useMemo(
    () => scenarios.find((item) => item.scenario_id === scenarioId),
    [scenarios, scenarioId],
  )
  const exploredNodeIds = useMemo(
    () => result?.trace.map((event) => event.node_id) ?? [],
    [result],
  )
  const canRun = Boolean(graphId && scenarioId && startId && goalId && !running)

  useEffect(() => {
    const edgeCount = result?.edge_ids.length ?? 0
    setVisiblePathEdgeCount(0)
    if (!edgeCount) {
      setAnimatingPath(false)
      return
    }

    setAnimatingPath(true)
    let nextEdgeCount = 0
    const timer = window.setInterval(() => {
      nextEdgeCount += 1
      setVisiblePathEdgeCount(nextEdgeCount)
      if (nextEdgeCount >= edgeCount) {
        window.clearInterval(timer)
        setAnimatingPath(false)
      }
    }, 480)

    return () => window.clearInterval(timer)
  }, [result])

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    fetchGraphCatalog(controller.signal)
      .then(({ graphs, invalid_graphs }) => {
        setCatalog(graphs)
        setInvalidGraphs(invalid_graphs)
        const initial = graphs.find((item) => item.graph_id === graphId)
          ?? graphs.find((item) => item.graph_id === 'toy_graph_v0.1')
          ?? graphs[0]
        if (initial) setGraphId(initial.graph_id)
        else setError('Không tìm thấy graph hợp lệ trong data/fixtures.')
      })
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') setError(reason.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [reloadVersion])

  useEffect(() => {
    if (!graphId) return
    const controller = new AbortController()
    setError('')
    setResult(null)
    setComparisonResults([])

    Promise.all([
      fetchLocations(graphId, controller.signal),
      fetchScenarios(graphId, controller.signal),
    ])
      .then(([locationPayload, scenarioPayload]) => {
        const nextLocations = locationPayload.locations
        const nextScenarios = scenarioPayload.scenarios
        setLocations(nextLocations)
        setScenarios(nextScenarios)
        setStartId((current) => (
          nextLocations.some((item) => item.node_id === current)
            ? current
            : nextLocations[0]?.node_id ?? ''
        ))
        setGoalId((current) => (
          nextLocations.some((item) => item.node_id === current)
            ? current
            : nextLocations.at(-1)?.node_id ?? ''
        ))
        setScenarioId((current) => (
          nextScenarios.some((item) => item.scenario_id === current)
            ? current
            : nextScenarios.find((item) => item.scenario_id === 'HEAVY_RAIN_SAFE')?.scenario_id
              ?? nextScenarios[0]?.scenario_id
              ?? ''
        ))
      })
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') setError(reason.message)
      })

    return () => controller.abort()
  }, [graphId, reloadVersion])

  useEffect(() => {
    if (!graphId) return
    const controller = new AbortController()
    setLoading(true)
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
    setGraphId(nextGraphId)
    setScenarioId('')
    setStartId('')
    setGoalId('')
  }

  async function executeSearch(event?: FormEvent) {
    event?.preventDefault()
    if (!canRun) return
    setRunning(true)
    setError('')
    setResult(null)
    setComparisonResults([])
    const input = {
      graph_id: graphId,
      start: startId,
      goal: goalId,
      scenario: scenarioId,
    }
    try {
      if (algorithm === 'COMPARE') {
        const payload = await runComparison(input)
        setComparisonResults(payload.results)
        setResult(payload.results[0] ?? null)
      } else {
        setResult(await runSearch({ ...input, algorithm }))
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không thể chạy thuật toán.')
    } finally {
      setRunning(false)
    }
  }

  function clearBoard() {
    setResult(null)
    setComparisonResults([])
    setError('')
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <strong>Pathfinder AI</strong>
          <span>FloodRoute HCMC</span>
        </div>
        <button className="clear-button" type="button" onClick={clearBoard}>
          Xóa kết quả
        </button>
        <button className="top-run-button" type="button" onClick={() => executeSearch()} disabled={!canRun}>
          <span aria-hidden="true">▷</span>
          {running ? 'Đang tìm đường…' : 'Chạy thuật toán'}
        </button>
      </header>

      <div className="workspace">
        <aside className="control-panel">
          <div className="panel-heading">
            <h1>Bảng điều khiển</h1>
            <p>Cấu hình tìm đường trên graph</p>
          </div>

          <form onSubmit={executeSearch}>
            <label>
              Dataset
              <select value={graphId} onChange={(event) => selectGraph(event.target.value)}>
                {catalog.map((item) => (
                  <option key={item.graph_id} value={item.graph_id}>
                    {item.label} · {item.node_count} nút
                  </option>
                ))}
              </select>
            </label>

            <label>
              Chọn thuật toán
              <select
                value={algorithm}
                onChange={(event) => setAlgorithm(event.target.value as AlgorithmSelection)}
              >
                <option value="A_STAR">A* Search</option>
                <option value="UCS">Uniform Cost Search</option>
                <option value="COMPARE">So sánh UCS và A*</option>
              </select>
            </label>

            <label>
              Kịch bản chi phí
              <select value={scenarioId} onChange={(event) => setScenarioId(event.target.value)}>
                {scenarios.map((item) => (
                  <option key={item.scenario_id} value={item.scenario_id}>
                    {item.scenario_id}
                  </option>
                ))}
              </select>
            </label>

            <div className="route-fields">
              <label>
                Điểm bắt đầu
                <select value={startId} onChange={(event) => setStartId(event.target.value)}>
                  {locations.map((item) => (
                    <option key={item.node_id} value={item.node_id}>
                      {item.node_id} · {item.name}
                    </option>
                  ))}
                </select>
              </label>
              <button
                className="swap-button"
                type="button"
                aria-label="Đổi điểm bắt đầu và đích"
                onClick={() => {
                  setStartId(goalId)
                  setGoalId(startId)
                }}
              >
                ⇅
              </button>
              <label>
                Điểm đích
                <select value={goalId} onChange={(event) => setGoalId(event.target.value)}>
                  {locations.map((item) => (
                    <option key={item.node_id} value={item.node_id}>
                      {item.node_id} · {item.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <button className="generate-button" type="button" onClick={() => setReloadVersion((value) => value + 1)}>
              <span aria-hidden="true">⌘</span>
              Nạp lại graph
            </button>
            <button className="mobile-run-button" type="submit" disabled={!canRun}>
              {running ? 'Đang tìm đường…' : 'Chạy thuật toán'}
            </button>
          </form>

          {selectedScenario && (
            <div className="scenario-summary">
              <span>{selectedScenario.cost_preset ?? 'CUSTOM'} preset</span>
              <strong>{selectedScenario.closed_edge_ids.length} cạnh đóng</strong>
            </div>
          )}
          {invalidGraphs.length > 0 && (
            <p className="warning-note">{invalidGraphs.length} graph không hợp lệ đã bị bỏ qua.</p>
          )}
          <div className="connection-state">
            <span className="status-dot" />
            Backend API đã kết nối
          </div>
        </aside>

        <main className="canvas-area" aria-live="polite">
          <div className="canvas-heading">
            <div>
              <span className="eyebrow">Optimal path visualizer</span>
              <h2>{selectedGraph?.label ?? 'Đang tải graph'}</h2>
            </div>
            <span className="simulated-badge">SIMULATED</span>
          </div>

          <section className="map-card">
            {graph ? (
              <RouteMap
                graph={graph}
                pathEdgeIds={result?.edge_ids}
                visiblePathEdgeCount={visiblePathEdgeCount}
                pathNodeIds={result?.path.slice(0, visiblePathEdgeCount + 1)}
                exploredNodeIds={exploredNodeIds}
                startId={startId}
                goalId={goalId}
              />
            ) : (
              <div className="map-placeholder">Chưa có dữ liệu graph</div>
            )}
            {loading && <div className="loading-overlay">Đang nạp dữ liệu…</div>}
            {animatingPath && result && (
              <div className="route-animation-status">
                <span className="animation-pulse" />
                Đang mô phỏng tuyến {Math.min(visiblePathEdgeCount + 1, result.edge_ids.length)}/{result.edge_ids.length}
              </div>
            )}
          </section>

          <section className="status-bar">
            <div className="legend">
              <span><i className="legend-line open" />Đường thoáng</span>
              <span><i className="legend-line blocked" />Đường bị chặn</span>
              <span><i className="legend-node" />Nút giao</span>
              <span><i className="legend-line path" />Đường tối ưu</span>
            </div>
            <div className="metric-pair">
              <div><span>Nodes Visited</span><strong>{result?.metrics.explored_nodes ?? 0}</strong></div>
              <div><span>Path Length (km)</span><strong>{metric(result?.metrics.distance_km, 2)}</strong></div>
              <div><span>ETA (min)</span><strong>{metric(result?.metrics.estimated_time_min, 2)}</strong></div>
              <div><span>Total Cost</span><strong>{metric(result?.metrics.total_cost, 2)}</strong></div>
            </div>
          </section>

          {error && <div className="error-banner" role="alert">{error}</div>}

          {comparisonResults.length > 0 && (
            <section className="comparison-grid" aria-label="Kết quả so sánh">
              {comparisonResults.map((item) => (
                <button key={item.algorithm} type="button" onClick={() => setResult(item)}>
                  <span>{item.algorithm}</span>
                  <strong>{item.metrics.total_cost.toFixed(3)} cost</strong>
                  <small>{item.metrics.explored_nodes} nodes · {item.metrics.processing_time_ms.toFixed(3)} ms</small>
                </button>
              ))}
            </section>
          )}

          {result && (
            <section className="result-details">
              <div>
                <span className="result-kicker">{result.algorithm} · {result.scenario}</span>
                <h3>{result.path.join(' → ')}</h3>
                <p>{result.explanation}</p>
              </div>
              <div className="guarantee-card">
                <span>Guarantee</span>
                <strong>{result.guarantee}</strong>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  )
}
