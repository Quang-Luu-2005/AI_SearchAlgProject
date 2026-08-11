import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { RouteMap, type EndpointPickTarget, type TourStopMarker } from './features/map/RouteMap'
import { TracePlayer } from './features/player/TracePlayer'
import { LanguageToggle } from './features/i18n/LanguageToggle'
import { BenchmarkCharts } from './features/analytics/BenchmarkCharts'
import { EventTimelineFeed } from './features/player/EventTimelineFeed'
import { KeyboardShortcutsModal } from './features/shortcuts/KeyboardShortcutsModal'
import { getInitialLanguage, t, type Language } from './lib/i18n'

import {
  fetchThuDucBoundary,
  fetchGraph,
  fetchGraphCatalog,
  interactiveGraphs,
  preferredGraphId,
  type GraphPayload,
  type GraphSummary,
  type InvalidGraphSummary,
  type ThuDucBoundary,
} from './lib/graph'
import {
  fetchLocations,
  fetchScenarios,
  optimizeTour,
  runComparison,
  runSearch,
  type AlgorithmSelection,
  type LocationItem,
  type OptimizeTourResult,
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
  const [thuDucBoundary, setThuDucBoundary] = useState<ThuDucBoundary | null>(null)
  const [boundaryError, setBoundaryError] = useState('')
  const [locations, setLocations] = useState<LocationItem[]>([])
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([])
  const [scenarioId, setScenarioId] = useState('')
  const [startId, setStartId] = useState('')
  const [goalId, setGoalId] = useState('')
  const [pickTarget, setPickTarget] = useState<EndpointPickTarget | null>(null)
  const [algorithm, setAlgorithm] = useState<AlgorithmSelection>('')
  const [tourStops, setTourStops] = useState<string[]>([])
  const [tourResult, setTourResult] = useState<OptimizeTourResult | null>(null)
  const [result, setResult] = useState<SearchResult | null>(null)
  const [comparisonResults, setComparisonResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [reloadVersion, setReloadVersion] = useState(0)

  const [currentStep, setCurrentStep] = useState(1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false)
  const [lang, setLang] = useState<Language>(getInitialLanguage)

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      const activeEl = document.activeElement
      const isInput = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'SELECT' || activeEl.tagName === 'TEXTAREA')

      if (event.key === '?') {
        if (!isInput) {
          event.preventDefault()
          setIsShortcutsOpen((prev) => !prev)
        }
        return
      }

      if (isInput) return

      if (event.code === 'Space') {
        if (result && result.trace.length > 0) {
          event.preventDefault()
          setIsPlaying((prev) => !prev)
        }
      } else if (event.key === 'ArrowRight') {
        if (result && result.trace.length > 0) {
          event.preventDefault()
          setIsPlaying(false)
          setCurrentStep((prev) => Math.min(prev + 1, result.trace.length))
        }
      } else if (event.key === 'ArrowLeft') {
        if (result && result.trace.length > 0) {
          event.preventDefault()
          setIsPlaying(false)
          setCurrentStep((prev) => Math.max(prev - 1, 1))
        }
      } else if (event.key === 'Escape') {
        if (pickTarget) setPickTarget(null)
        if (isShortcutsOpen) setIsShortcutsOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [result, pickTarget, isShortcutsOpen])

  const selectedGraph = useMemo(
    () => catalog.find((item) => item.graph_id === graphId),
    [catalog, graphId],
  )
  const selectedScenario = useMemo(
    () => scenarios.find((item) => item.scenario_id === scenarioId),
    [scenarios, scenarioId],
  )
  const exploredNodeIds = useMemo(
    () => result?.trace.slice(0, currentStep).map((event) => event.node_id) ?? [],
    [result, currentStep],
  )
  const isTourMode = algorithm === 'HELD_KARP' || algorithm === 'NEAREST_NEIGHBOR' || algorithm === 'OPTIMIZE_TOUR'
  const canRun = Boolean(
    algorithm &&
    graphId &&
    scenarioId &&
    startId &&
    (isTourMode ? tourStops.length >= 5 : goalId) &&
    !running,
  )

  const visiblePathEdgeCount = useMemo(() => {
    if (!result || !result.edge_ids.length) return 0
    if (!result.trace.length || currentStep >= result.trace.length) return result.edge_ids.length
    const ratio = currentStep / result.trace.length
    return Math.max(1, Math.floor(ratio * result.edge_ids.length))
  }, [result, currentStep])

  const currentAnimatedNodeInfo = useMemo(() => {
    if (!result || !result.trace.length) return null
    const safeIdx = Math.min(Math.max(currentStep, 1), result.trace.length) - 1
    const event = result.trace[safeIdx]
    if (!event) return null

    const nodeId = event.node_id
    const loc = locations.find((item) => item.node_id === nodeId)
    const name = loc ? loc.name : nodeId

    if (tourResult) {
      const visitIdx = tourResult.visit_order.indexOf(nodeId)
      if (visitIdx !== -1) {
        return {
          nodeId,
          name,
          stopIndex: visitIdx + 1,
          isStop: true,
          label: `Bước ${event.step}/${result.trace.length} · ${event.kind} · Điểm #${visitIdx + 1} · ${name}`,
        }
      }
    }

    return {
      nodeId,
      name,
      stopIndex: event.step,
      isStop: false,
      label: `Bước ${event.step}/${result.trace.length} · [${event.kind}] · ${name} (${nodeId})`,
    }
  }, [result, currentStep, locations, tourResult])

  const tourStopMarkers = useMemo<TourStopMarker[]>(() => {
    if (!tourResult || !graph) return []
    const nodeById = new Map(graph.nodes.map((n) => [n.node_id, n]))
    const currentVisitedNodes = result ? result.trace.slice(0, currentStep).map((e) => e.node_id) : []
    const visitedSet = new Set(currentVisitedNodes)

    return tourResult.visit_order.map((nodeId, idx) => {
      const node = nodeById.get(nodeId)
      const loc = locations.find((l) => l.node_id === nodeId)
      const name = loc ? loc.name : (node?.label || nodeId)
      const isVisited = visitedSet.has(nodeId)

      return {
        nodeId,
        name,
        stopIndex: idx + 1,
        latitude: node?.latitude ?? 0,
        longitude: node?.longitude ?? 0,
        isVisited,
      }
    })
  }, [tourResult, graph, result, currentStep, locations])

  useEffect(() => {
    const controller = new AbortController()
    fetchThuDucBoundary(controller.signal)
      .then((payload) => {
        setThuDucBoundary(payload)
        setBoundaryError('')
      })
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') setBoundaryError('Không tải được ranh Thủ Đức.')
      })
    return () => controller.abort()
  }, [])



  useEffect(() => {
    if (!result || !result.trace.length) {
      setCurrentStep(1)
      setIsPlaying(false)
      return
    }
    setCurrentStep(1)
    setIsPlaying(true)
  }, [result])

  useEffect(() => {
    if (!isPlaying || !result || !result.trace.length) return

    const intervalMs = Math.max(Math.floor(350 / playbackSpeed), 30)
    const timer = window.setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= result.trace.length) {
          setIsPlaying(false)
          return prev
        }
        return prev + 1
      })
    }, intervalMs)

    return () => window.clearInterval(timer)
  }, [isPlaying, result, playbackSpeed])

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    fetchGraphCatalog(controller.signal)
      .then(({ graphs, invalid_graphs }) => {
        const nextCatalog = interactiveGraphs(graphs)
        setCatalog(nextCatalog)
        setInvalidGraphs(invalid_graphs)
        const initialGraphId = preferredGraphId(nextCatalog, graphId)
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
        const isTourAlg = algorithm === 'HELD_KARP' || algorithm === 'NEAREST_NEIGHBOR' || algorithm === 'OPTIMIZE_TOUR'
        setStartId((current) => (
          isTourAlg
            ? ''
            : nextLocations.some((item) => item.node_id === current)
              ? current
              : nextLocations[0]?.node_id ?? ''
        ))
        setGoalId((current) => (
          isTourAlg
            ? ''
            : nextLocations.some((item) => item.node_id === current)
              ? current
              : nextLocations.filter((item) => item.point_id).at(-1)?.node_id
              ?? nextLocations.at(-1)?.node_id
              ?? ''
        ))
        setTourStops((current) => (
          isTourAlg
            ? []
            : current
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
    setTourStops([])
    setPickTarget(null)
    clearRouteResult()
  }

  function changeAlgorithm(nextAlg: AlgorithmSelection) {
    setAlgorithm(nextAlg)
    setStartId('') // Reset điểm bắt đầu mỗi khi chuyển thuật toán
    setGoalId('') // Reset điểm đích
    setTourStops([]) // Reset toàn bộ các điểm kết thúc/giao hàng
    clearRouteResult()
  }

  function reloadGraph() {
    setStartId('') // Reset điểm bắt đầu
    setGoalId('') // Reset điểm đích
    setTourStops([]) // Reset các điểm kết thúc/giao hàng
    setPickTarget(null)
    setError('')
    clearRouteResult()
    setReloadVersion((value) => value + 1)
  }

  function clearRouteResult() {
    setResult(null)
    setTourResult(null)
    setComparisonResults([])
    setCurrentStep(1)
    setIsPlaying(false)
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
    setTourResult(null)
    setComparisonResults([])

    if (isTourMode) {
      if (tourStops.length < 5) {
        setError('Vui lòng chọn ít nhất 5 tọa độ điểm.')
        setRunning(false)
        return
      }

      try {
        const tourAlgParam = algorithm === 'NEAREST_NEIGHBOR' ? 'NEAREST_NEIGHBOR' : 'HELD_KARP'
        const tourPayload = await optimizeTour({
          graph_id: graphId,
          depot: startId,
          stops: tourStops,
          scenario: scenarioId,
          algorithm: 'A_STAR',
          tour_algorithm: tourAlgParam,
          return_to_depot: true,
        })
        setTourResult(tourPayload)

        const stitchedResult: SearchResult = {
          algorithm: (algorithm === 'NEAREST_NEIGHBOR' ? 'NEAREST_NEIGHBOR' : 'HELD_KARP') as any,
          scenario: tourPayload.scenario,
          data_status: tourPayload.data_status,
          path: tourPayload.full_path,
          edge_ids: tourPayload.edge_ids,
          metrics: {
            distance_m: tourPayload.total_distance_m,
            distance_km: tourPayload.total_distance_km,
            estimated_time_min: tourPayload.estimated_time_min,
            total_cost: tourPayload.total_cost,
            explored_nodes: tourPayload.full_path.length,
            processing_time_ms: 0,
          },
          trace: tourPayload.full_path.map((node_id, idx) => ({
            step: idx + 1,
            kind: idx === 0 ? 'OPEN' : idx === tourPayload.full_path.length - 1 ? 'GOAL' : 'EXPAND',
            node_id,
            parent_id: idx > 0 ? tourPayload.full_path[idx - 1] : null,
            g_cost: null,
            h_cost: null,
            details: {},
          })),
          guarantee: tourPayload.guarantee,
          explanation: tourPayload.explanation,
          edge_breakdown: [],
          limitations: tourPayload.limitations,
        }
        setResult(stitchedResult)
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : 'Không thể tối ưu tour.')
      } finally {
        setRunning(false)
      }
      return
    }


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
      } else if (algorithm === 'A_STAR' || algorithm === 'UCS') {
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
    setAlgorithm('') // Reset thuật toán về không chọn
    setStartId('') // Reset điểm bắt đầu
    setGoalId('') // Reset điểm đích/kết thúc
    setTourStops([]) // Reset toàn bộ điểm kết thúc/giao hàng
    setPickTarget(null)
    setError('')
  }


  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <strong>PathFinder AI</strong>
          <span>FloodRoute HCMC</span>
        </div>
        <div className="topbar-actions">
          <button
            type="button"
            className="shortcuts-help-btn"
            onClick={() => setIsShortcutsOpen(true)}
            title={t('shortcuts_btn', lang)}
            aria-label={t('shortcuts_btn', lang)}
          >
            {t('shortcuts_btn', lang)}
          </button>
          <LanguageToggle lang={lang} onLanguageChange={setLang} />
          <button className="clear-button" type="button" onClick={clearBoard}>
            {t('clear_results', lang)}
          </button>
          <button
            className="top-run-button"
            type="button"
            onClick={() => executeSearch()}
            disabled={!canRun}
            title={!algorithm ? t('select_alg_first', lang) : !startId ? t('select_start_first', lang) : t('run_algorithm', lang)}
          >
            <span aria-hidden="true">▷</span>
            {running ? t('running', lang) : t('run_algorithm', lang)}
          </button>
        </div>
      </header>

      <div className="workspace">
        <aside className="control-panel">
          <div className="panel-heading">
            <h1>{t('panel_title', lang)}</h1>
            <p>{t('panel_subtitle', lang)}</p>
          </div>

          <form onSubmit={executeSearch}>
            <label>
              {t('dataset_label', lang)}
              <select value={graphId} onChange={(event) => selectGraph(event.target.value)}>
                {catalog.map((item) => (
                  <option key={item.graph_id} value={item.graph_id}>
                    {item.label} · {item.node_count} {t('nodes_count', lang)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              {t('select_alg_label', lang)}
              <select
                value={algorithm}
                onChange={(event) => changeAlgorithm(event.target.value as AlgorithmSelection)}
              >
                <option value="">{t('select_alg_placeholder', lang)}</option>
                <option value="A_STAR">{t('alg_a_star', lang)}</option>
                <option value="UCS">{t('alg_ucs', lang)}</option>
                <option value="COMPARE">{t('alg_compare', lang)}</option>
                <option value="HELD_KARP">{t('alg_held_karp', lang)}</option>
                <option value="NEAREST_NEIGHBOR">{t('alg_nearest_neighbor', lang)}</option>
                <option value="OPTIMIZE_TOUR">{t('alg_optimize_tour', lang)}</option>
              </select>
            </label>

            <label>
              {t('scenario_label', lang)}
              <select value={scenarioId} onChange={(event) => selectScenario(event.target.value)}>
                {scenarios.map((item) => (
                  <option key={item.scenario_id} value={item.scenario_id}>
                    {item.scenario_id}
                  </option>
                ))}
              </select>
            </label>

            {!algorithm ? (
              <div className="algorithm-prompt-note">
                {t('alg_prompt', lang)}
              </div>
            ) : isTourMode ? (
              <div className="tour-stops-field">
                <LocationPicker
                  label={t('start_label', lang)}
                  value={startId}
                  locations={locations}
                  onChange={selectStart}
                />
                {!startId && (
                  <p className="warning-note" style={{ margin: '4px 0 8px 0', color: '#b45309' }}>
                    {t('depot_warning', lang)}
                  </p>
                )}
                <div className="stops-list-container">
                  <label>{t('stops_header', lang)} ({tourStops.length}/10)</label>
                  <div className="stops-chips">
                    {tourStops.map((stopId, idx) => {
                      const loc = locations.find((item) => item.node_id === stopId)
                      return (
                        <span key={`${stopId}-${idx}`} className="stop-chip">
                          <small>#{idx + 1}</small> {loc ? loc.name : stopId}
                          <button
                            type="button"
                            className="remove-chip-btn"
                            onClick={() => setTourStops(tourStops.filter((_, i) => i !== idx))}
                          >
                            ×
                          </button>
                        </span>
                      )
                    })}
                  </div>
                  {tourStops.length < 5 && (
                    <p className="warning-note" style={{ margin: '4px 0 8px 0' }}>
                      {t('stops_needed', lang, { count: 5 - tourStops.length })}
                    </p>
                  )}
                  {tourStops.length < 10 && (
                    <LocationPicker
                      label={t('add_stop_label', lang)}
                      value=""
                      locations={locations.filter((item) => item.node_id !== startId && !tourStops.includes(item.node_id))}
                      onChange={(nodeId) => {
                        if (nodeId && !tourStops.includes(nodeId)) {
                          setTourStops([...tourStops, nodeId])
                        }
                      }}
                    />
                  )}
                </div>
              </div>
            ) : (
              <div className="route-fields">
                <LocationPicker
                  label={t('start_label', lang)}
                  value={startId}
                  locations={locations}
                  onChange={selectStart}
                />
                <button
                  className="swap-button"
                  type="button"
                  aria-label={t('swap_endpoints', lang)}
                  onClick={swapEndpoints}
                >
                  ⇅
                </button>
                <LocationPicker
                  label={t('goal_label', lang)}
                  value={goalId}
                  locations={locations}
                  onChange={selectGoal}
                />
              </div>
            )}

            <button className="generate-button" type="button" onClick={reloadGraph}>
              <span aria-hidden="true">⌘</span>
              {t('reload_graph', lang)}
            </button>
            <button
              className="mobile-run-button"
              type="submit"
              disabled={!canRun}
              title={!algorithm ? t('select_alg_first', lang) : !startId ? t('select_start_first', lang) : t('run_algorithm', lang)}
            >
              {running ? t('running', lang) : t('run_algorithm', lang)}
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
                boundary={thuDucBoundary}
                boundaryWarning={boundaryError}
                pathEdgeIds={result?.edge_ids}
                visiblePathEdgeCount={visiblePathEdgeCount}
                pathNodeIds={result?.path.slice(0, visiblePathEdgeCount + 1)}
                exploredNodeIds={exploredNodeIds}
                startId={startId}
                goalId={goalId}
                pickTarget={pickTarget}
                onNodePick={pickNode}
                onPickTargetChange={setPickTarget}
                activeAnimatedNodeId={currentAnimatedNodeInfo?.nodeId}
                activeAnimatedNodeLabel={currentAnimatedNodeInfo?.label}
                tourStopMarkers={tourStopMarkers}
                isTourMode={isTourMode}
                hideEndpoints={!algorithm}
                lang={lang}
              />
            ) : (
              <div className="map-placeholder">{t('panel_subtitle', lang)}</div>
            )}
            {loading && <div className="loading-overlay">{t('running', lang)}</div>}
            {isPlaying && result && (
              <div className="route-animation-status" role="status">
                <span className="animation-pulse" />
                {currentAnimatedNodeInfo ? (
                  <span>
                    <strong>{currentAnimatedNodeInfo.label}</strong>
                    {' · '}
                    <small>{t('trace_animating', lang)} {Math.min(visiblePathEdgeCount + 1, result.edge_ids.length)}/{result.edge_ids.length}</small>
                  </span>
                ) : (
                  <span>{t('trace_animating', lang)} {Math.min(visiblePathEdgeCount + 1, result.edge_ids.length)}/{result.edge_ids.length}</span>
                )}
              </div>
            )}
          </section>

          {result && result.trace.length > 0 && (
            <>
              <TracePlayer
                trace={result.trace}
                currentStep={currentStep}
                isPlaying={isPlaying}
                playbackSpeed={playbackSpeed}
                onPlayToggle={() => setIsPlaying(!isPlaying)}
                onNextStep={() => {
                  setIsPlaying(false)
                  setCurrentStep((prev) => Math.min(prev + 1, result.trace.length))
                }}
                onPreviousStep={() => {
                  setIsPlaying(false)
                  setCurrentStep((prev) => Math.max(prev - 1, 1))
                }}
                onReset={() => {
                  setIsPlaying(false)
                  setCurrentStep(1)
                }}
                onStepChange={(step) => {
                  setIsPlaying(false)
                  setCurrentStep(step)
                }}
                onSpeedChange={setPlaybackSpeed}
                lang={lang}
              />

              <EventTimelineFeed
                trace={result.trace}
                currentStep={currentStep}
                onStepSelect={(step) => {
                  setIsPlaying(false)
                  setCurrentStep(step)
                }}
                lang={lang}
              />
            </>
          )}

          {selectedGraph?.graph_id?.startsWith('processed/thu_duc_') && (
            <p className="dataset-attribution">
              Traffic/road paths: UTraffic/HCMUT · POI/boundary{' '}
              <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">
                OpenStreetMap
              </a>{' '}
              contributors
            </p>
          )}

          <section className="metrics-bar" aria-label="Route search metrics">
            <div className="metric-chip"><span>Algorithm</span><strong>{algorithm || '—'}</strong></div>
            <div className="metric-chip"><span>Scenario</span><strong>{scenarioId || '—'}</strong></div>
            <div className="metric-chip"><span>Nodes Visited</span><strong>{result?.metrics.explored_nodes ?? 0}</strong></div>
            <div className="metric-chip"><span>Path Length (km)</span><strong>{metric(result?.metrics.distance_km, 2)}</strong></div>
            <div className="metric-chip"><span>ETA (min)</span><strong>{metric(result?.metrics.estimated_time_min, 2)}</strong></div>
            <div className="metric-chip"><span>Total Cost</span><strong>{metric(result?.metrics.total_cost, 2)}</strong></div>
          </section>

          {error && <div className="error-banner" role="alert">{error}</div>}

          {comparisonResults.length > 0 && (
            <section className="comparison-grid" aria-label="Comparison results">
              {comparisonResults.map((item) => (
                <button key={item.algorithm} type="button" onClick={() => setResult(item)}>
                  <span>{item.algorithm}</span>
                  <strong>{item.metrics.total_cost.toFixed(3)} cost</strong>
                  <small>{item.metrics.explored_nodes} nodes · {item.metrics.processing_time_ms.toFixed(3)} ms</small>
                </button>
              ))}
            </section>
          )}

          {tourResult && (
            <section className="tour-result-card" aria-label="Tour result">
              <div className="tour-header">
                <span className="tour-kicker">{t('tour_kicker', lang)} · {tourResult.scenario}</span>
                <h3>{t('tour_route', lang)} {tourResult.visit_order.join(' → ')}</h3>
                <p>{tourResult.explanation}</p>
              </div>
              {algorithm === 'OPTIMIZE_TOUR' ? (
                <div className="tour-guarantee-comparison" aria-label="Guarantee comparison">
                  <div className="tour-guarantee-card optimal-card">
                    <span className="guarantee-tag">{t('optimal_tag', lang)}</span>
                    <h4>Held-Karp DP</h4>
                    <div className="card-cost">{tourResult.comparison.held_karp_cost.toFixed(3)} cost</div>
                    <div className="card-guarantee">OPTIMAL_HELD_KARP</div>
                    <p>{t('optimal_tag', lang)}</p>
                  </div>
                  <div className="tour-guarantee-card heuristic-card">
                    <span className="guarantee-tag">{t('heuristic_tag', lang)}</span>
                    <h4>Nearest Neighbor</h4>
                    <div className="card-cost">{tourResult.comparison.nearest_neighbor_cost.toFixed(3)} cost</div>
                    <div className="card-guarantee">APPROXIMATE_NEAREST_NEIGHBOR</div>
                    <p>{t('heuristic_tag', lang)}</p>
                  </div>
                  <div className="tour-guarantee-card gap-card">
                    <span className="guarantee-tag">📊 {t('approx_gap_title', lang)}</span>
                    <h4>{t('approx_gap_title', lang)}</h4>
                    <div className={`card-cost ${tourResult.comparison.approximation_gap_percent === 0 ? 'gap-zero' : 'gap-positive'}`}>
                      +{tourResult.comparison.approximation_gap_percent.toFixed(2)}%
                    </div>
                    <div className="card-guarantee">Held-Karp vs Nearest Neighbor</div>
                    <p>{tourResult.comparison.approximation_gap_percent === 0 ? t('gap_zero_desc', lang) : t('gap_pos_desc', lang)}</p>
                  </div>
                </div>
              ) : (
                <>
                  <div className={`tour-guarantee-banner ${tourResult.guarantee === 'OPTIMAL_HELD_KARP' ? 'tour-guarantee-banner--optimal' : 'tour-guarantee-banner--heuristic'}`}>
                    <div className="guarantee-badge-header">
                      <span className="guarantee-tag-pill">
                        {tourResult.guarantee === 'OPTIMAL_HELD_KARP' ? t('optimal_tag', lang) : t('heuristic_tag', lang)}
                      </span>
                      <span className="guarantee-title-text">
                        {t('guarantee', lang)}: <code>{tourResult.guarantee}</code>
                      </span>
                    </div>
                  </div>

                  <div className="tour-summary-box">
                    <div className="comp-item">
                      <span>{t('select_alg_label', lang)}</span>
                      <strong>{algorithm === 'HELD_KARP' ? t('alg_held_karp', lang) : t('alg_nearest_neighbor', lang)}</strong>
                    </div>
                    <div className="comp-item">
                      <span>{t('dist_total', lang)}</span>
                      <strong>{tourResult.total_distance_km.toFixed(2)} km</strong>
                    </div>
                    <div className="comp-item">
                      <span>{t('time_eta', lang)}</span>
                      <strong>{tourResult.estimated_time_min.toFixed(2)} {t('minutes', lang)}</strong>
                    </div>
                    <div className="comp-item">
                      <span>{t('total_cost', lang)}</span>
                      <strong>{tourResult.total_cost.toFixed(3)}</strong>
                    </div>
                  </div>
                </>
              )}

              <div className="legs-table-container">
                <h4>{t('legs_breakdown', lang, { count: tourResult.legs.length })}</h4>
                <table className="legs-table">
                  <thead>
                    <tr>
                      <th>{t('leg_no', lang)}</th>
                      <th>{t('from_node', lang)}</th>
                      <th>{t('to_node', lang)}</th>
                      <th>{t('path_nodes', lang)}</th>
                      <th>{t('leg_dist', lang)}</th>
                      <th>{t('leg_time', lang)}</th>
                      <th>{t('leg_cost', lang)}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tourResult.legs.map((leg, idx) => {
                      const fromLoc = locations.find((loc) => loc.node_id === leg.from_node_id)
                      const toLoc = locations.find((loc) => loc.node_id === leg.to_node_id)
                      const fromName = fromLoc ? fromLoc.name : leg.from_node_id
                      const toName = toLoc ? toLoc.name : leg.to_node_id

                      return (
                        <tr key={`${leg.from_node_id}-${leg.to_node_id}-${idx}`}>
                          <td><strong>#{idx + 1}</strong></td>
                          <td>
                            <div className="leg-node-block">
                              <span className="leg-node-name">{fromName}</span>
                              <span className="leg-node-id"><code>{leg.from_node_id}</code></span>
                            </div>
                          </td>
                          <td>
                            <div className="leg-node-block">
                              <span className="leg-node-name">{toName}</span>
                              <span className="leg-node-id"><code>{leg.to_node_id}</code></span>
                            </div>
                          </td>
                          <td>
                            <span className="leg-path-seq">{leg.path.join(' → ')}</span>
                            <small style={{ display: 'block', color: 'var(--muted)', marginTop: '2px' }}>
                              ({leg.path.length} {t('nodes_count', lang)})
                            </small>
                          </td>
                          <td>{leg.distance_km.toFixed(2)} km</td>
                          <td>{leg.travel_time_min.toFixed(2)} {t('minutes', lang)}</td>
                          <td><strong>{leg.total_cost.toFixed(3)}</strong></td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

            </section>
          )}

          {tourResult?.comparison ? (
            <BenchmarkCharts comparison={tourResult.comparison} lang={lang} />
          ) : result ? (
            <BenchmarkCharts singleMetrics={result.metrics} lang={lang} />
          ) : null}

          {result && (
            <section className="result-details">
              <div>
                <span className="result-kicker">{result.algorithm} · {result.scenario}</span>
                <h3>{result.path.join(' → ')}</h3>
                <p>{result.explanation}</p>
              </div>
              <div className="guarantee-card">
                <span>{t('guarantee', lang)}</span>
                <strong>{result.guarantee}</strong>
              </div>
            </section>
          )}
        </main>
      </div>

      <KeyboardShortcutsModal isOpen={isShortcutsOpen} onClose={() => setIsShortcutsOpen(false)} />
    </div>
  )
}
