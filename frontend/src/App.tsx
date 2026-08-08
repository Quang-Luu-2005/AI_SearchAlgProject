import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { RouteMap, type EndpointPickTarget } from './features/map/RouteMap'
import {
  fetchGraph,
  fetchGraphCatalog,
  preferredGraphId,
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

type LocationPickerProps = {
  label: string
  value: string
  locations: LocationItem[]
  onChange: (nodeId: string) => void
}

function LocationPicker({ label, value, locations, onChange }: LocationPickerProps) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = locations.find((item) => item.node_id === value)
  const normalizedQuery = query.trim().toLocaleLowerCase()
  const matches = locations
    .filter((item) => {
      if (!normalizedQuery) return true
      return `${item.name} ${item.node_id}`.toLocaleLowerCase().includes(normalizedQuery)
    })
    .slice(0, 40)

  function choose(nodeId: string) {
    onChange(nodeId)
    setQuery('')
    setOpen(false)
  }

  return (
    <div className="location-picker">
      <label>
        {label}
        <input
          type="search"
          value={open ? query : (selected ? `${selected.name} · ${selected.node_id}` : '')}
          placeholder="Tìm theo tên hoặc node_id…"
          aria-label={label}
          aria-expanded={open}
          onFocus={() => {
            setQuery('')
            setOpen(true)
          }}
          onChange={(event) => {
            setQuery(event.target.value)
            setOpen(true)
          }}
          onBlur={() => window.setTimeout(() => setOpen(false), 120)}
        />
      </label>
      {open && (
        <div className="location-results" role="listbox" aria-label={`${label} results`}>
          {matches.length > 0 ? matches.map((item) => (
            <button
              key={item.point_id ?? item.node_id}
              type="button"
              role="option"
              aria-selected={item.node_id === value}
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => choose(item.node_id)}
            >
              <span>{item.name}</span>
              <small>{item.node_id}</small>
            </button>
          )) : <span className="location-empty">Không tìm thấy điểm phù hợp</span>}
          {matches.length === 40 && <small className="location-result-limit">Đang hiển thị 40 kết quả đầu tiên</small>}
        </div>
      )}
    </div>
  )
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
  const [pickTarget, setPickTarget] = useState<EndpointPickTarget | null>(null)
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
        const initialGraphId = preferredGraphId(graphs, graphId)
        if (initialGraphId) setGraphId(initialGraphId)
        else setError('Không tìm thấy graph hợp lệ trong data/fixtures hoặc data/processed.')
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
            : nextLocations.filter((item) => item.point_id).at(-1)?.node_id
              ?? nextLocations.at(-1)?.node_id
              ?? ''
        ))
        setScenarioId((current) => (
          nextScenarios.some((item) => item.scenario_id === current)
            ? current
            : nextScenarios.find((item) => item.scenario_id === 'RAIN_FLOOD_AWARE_2025_2026')?.scenario_id
              ?? nextScenarios.find((item) => item.scenario_id === 'HEAVY_RAIN_SAFE')?.scenario_id
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
    setPickTarget(null)
  }

  function clearRouteResult() {
    setResult(null)
    setComparisonResults([])
    setVisiblePathEdgeCount(0)
    setAnimatingPath(false)
  }

  function selectStart(nodeId: string) {
    setStartId(nodeId)
    clearRouteResult()
  }

  function selectGoal(nodeId: string) {
    setGoalId(nodeId)
    clearRouteResult()
  }

  function pickNode(target: EndpointPickTarget, nodeId: string) {
    if (target === 'START') selectStart(nodeId)
    else selectGoal(nodeId)
  }

  function swapEndpoints() {
    setStartId(goalId)
    setGoalId(startId)
    clearRouteResult()
  }

  function selectScenario(nextScenarioId: string) {
    setScenarioId(nextScenarioId)
    clearRouteResult()
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
    clearRouteResult()
    setPickTarget(null)
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
              <select value={scenarioId} onChange={(event) => selectScenario(event.target.value)}>
                {scenarios.map((item) => (
                  <option key={item.scenario_id} value={item.scenario_id}>
                    {item.scenario_id}
                  </option>
                ))}
              </select>
            </label>

            <div className="route-fields">
              <LocationPicker
                label="Điểm bắt đầu"
                value={startId}
                locations={locations}
                onChange={selectStart}
              />
              <button
                className="swap-button"
                type="button"
                aria-label="Đổi điểm bắt đầu và đích"
                onClick={swapEndpoints}
              >
                ⇅
              </button>
              <LocationPicker
                label="Điểm đích"
                value={goalId}
                locations={locations}
                onChange={selectGoal}
              />
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
          {selectedGraph?.dataset_kind === 'processed' && (
            <div className="dataset-notice">
              <strong>{selectedGraph.real_time ? 'Real-time dataset' : 'Historical traffic · not real-time'}</strong>
              <span>Snapshot {selectedGraph.snapshot_date ?? 'unknown'} · {selectedGraph.routing_dataset_status}</span>
              {selectedGraph.graph_id === 'processed/thu_duc_market_v1.0.0' && (
                <small>No flood record does not mean a road is safe.</small>
              )}
              <details>
                <summary>Nguồn và giới hạn dataset</summary>
                <ul>
                  {selectedGraph.limitations.map((item) => <li key={item}>{item}</li>)}
                </ul>
                {selectedGraph.graph_id === 'processed/thu_duc_market_v1.0.0' && (
                  <div>
                    <a href="https://ttbc-hcm.gov.vn/24-diem-mua-la-ngap-o-tp-thu-duc-nguoi-dan-can-chu-y-1018710.html" target="_blank" rel="noreferrer">
                      Flood hotspots 2025
                    </a>
                    {' · '}
                    <a href="https://tuoitre.vn/nld/so-xay-dung-tphcm-neu-nguyen-nhan-cho-thu-duc-ngap-nang-sau-mua-dau-mua-196260507181450735.htm" target="_blank" rel="noreferrer">
                      Thu Duc Market update 2026
                    </a>
                  </div>
                )}
              </details>
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
            <span className={`data-badge data-badge--${(selectedGraph?.data_status ?? 'unknown').toLowerCase()}`}>
              {selectedGraph?.data_status ?? 'UNKNOWN'}
            </span>
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
                pickTarget={pickTarget}
                onNodePick={pickNode}
                onPickTargetChange={setPickTarget}
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

          {selectedGraph?.graph_id === 'processed/thu_duc_market_v1.0.0' && (
            <p className="dataset-attribution">
              Traffic: UTraffic/HCMUT · Flood records: TP.HCM public reporting · POI{' '}
              <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">
                © OpenStreetMap contributors, ODbL 1.0
              </a>
            </p>
          )}

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
