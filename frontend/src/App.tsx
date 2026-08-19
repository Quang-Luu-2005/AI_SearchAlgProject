import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { RouteMap, type EndpointPickTarget, type TourStopMarker } from './features/map/RouteMap'
import { TracePlayer } from './features/player/TracePlayer'
import { LanguageToggle } from './features/i18n/LanguageToggle'
import { EventTimelineFeed } from './features/player/EventTimelineFeed'
import { deriveTraceVisualState } from './features/player/traceState'
import { KeyboardShortcutsModal } from './features/shortcuts/KeyboardShortcutsModal'
import { getInitialLanguage, t, translateGraphLabel, type Language } from './lib/i18n'

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
  generateRandomScenario,
  optimizeTour,
  runAlternatives,
  runComparison,
  runSearch,
  type AlgorithmSelection,
  type LocationItem,
  type OptimizeTourResult,
  type ScenarioItem,
  type SearchResult,
  type RandomAffectedEdge,
} from './lib/search'
import { addTourStop, MAX_TOUR_STOPS } from './lib/tourSelection'
import { summarizeComparison } from './lib/comparison'


export function metric(value: number | undefined, digits = 1): string {
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
  const [randomAffectedEdges, setRandomAffectedEdges] = useState<RandomAffectedEdge[]>([])
  const [randomRunning, setRandomRunning] = useState(false)
  const [startId, setStartId] = useState('')
  const [goalId, setGoalId] = useState('')
  const [pickTarget, setPickTarget] = useState<EndpointPickTarget | null>(null)
  const [algorithm, setAlgorithm] = useState<AlgorithmSelection>('')
  const [tourStops, setTourStops] = useState<string[]>([])
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null)
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
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false)
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
        if (isMobileDrawerOpen) setIsMobileDrawerOpen(false)
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
  const traceVisualState = useMemo(
    () => deriveTraceVisualState(result?.trace ?? [], currentStep),
    [result, currentStep],
  )
  const comparisonInsight = useMemo(
    () => summarizeComparison(comparisonResults),
    [comparisonResults],
  )
  const alternativeRoutes = useMemo(() => {
    if (!['LANDMARK_FLOOD', 'LANDMARK_CONGESTION'].includes(scenarioId)
      && !scenarioId.startsWith('SCENARIO_')) return []
    const unique = new Map<string, SearchResult>()
    comparisonResults.forEach((candidate) => {
      const key = candidate.edge_ids.join('|')
      const previous = unique.get(key)
      if (!previous || candidate.metrics.total_cost < previous.metrics.total_cost) unique.set(key, candidate)
    })
    return [...unique.values()]
      .sort((left, right) => left.metrics.total_cost - right.metrics.total_cost)
      .slice(0, 3)
  }, [comparisonResults, scenarioId])
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
    if (!graph) return []
    const nodeById = new Map(graph.nodes.map((n) => [n.node_id, n]))
    const currentVisitedNodes = result ? result.trace.slice(0, currentStep).map((e) => e.node_id) : []
    const visitedSet = new Set(currentVisitedNodes)
    const orderedStopIds = tourResult
      ? tourResult.visit_order.filter(
        (nodeId, index, visitOrder) => nodeId !== startId && visitOrder.indexOf(nodeId) === index,
      )
      : tourStops

    return orderedStopIds.map((nodeId, idx) => {
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
  }, [tourResult, graph, result, currentStep, locations, startId, tourStops])

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
            : nextScenarios.find((item) => item.scenario_id === 'LANDMARK_CONGESTION')?.scenario_id
            ?? nextScenarios.find((item) => item.scenario_id === 'RAIN_FLOOD_AWARE_2025_2026')?.scenario_id
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
    setPickTarget(null)
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

  function selectAlternativeRoute(candidate: SearchResult) {
    setResult(candidate)
    setTourResult(null)
    setCurrentStep(candidate.trace.length || 1)
    setIsPlaying(false)
  }

  function selectStart(nodeId: string) {
    setStartId(nodeId)
    if (isTourMode) {
      setTourStops((current) => current.filter((stopId) => stopId !== nodeId))
    }
    setError('')
    clearRouteResult()
  }

  function selectGoal(nodeId: string) {
    setGoalId(nodeId)
    setError('')
    clearRouteResult()
  }

  function selectTourStop(nodeId: string) {
    const selection = addTourStop(tourStops, startId, nodeId)
    if (selection.status === 'DEPOT_SELECTED') {
      setError(t('tour_stop_same_as_depot', lang))
      return
    }
    if (selection.status === 'DUPLICATE') {
      setError(t('tour_stop_duplicate', lang))
      return
    }
    if (selection.status === 'LIMIT_REACHED') {
      setError(t('tour_stop_limit', lang, { count: MAX_TOUR_STOPS }))
      setPickTarget(null)
      return
    }

    setTourStops(selection.stops)
    setError('')
    clearRouteResult()
    if (selection.stops.length >= MAX_TOUR_STOPS) setPickTarget(null)
  }

  function pickNode(target: EndpointPickTarget, nodeId: string) {
    if (target === 'START') selectStart(nodeId)
    else if (isTourMode) selectTourStop(nodeId)
    else selectGoal(nodeId)
  }

  function swapEndpoints() {
    setStartId(goalId)
    setGoalId(startId)
    clearRouteResult()
  }

  function selectScenario(nextScenarioId: string) {
    if (nextScenarioId === 'RANDOM') {
      void createRandomScenario()
      return
    }
    setScenarioId(nextScenarioId)
    setRandomAffectedEdges([])
    clearRouteResult()
  }

  async function createRandomScenario() {
    if (!graphId || !startId || !goalId || randomRunning) return
    setRandomRunning(true)
    setError('')
    try {
      const payload = await generateRandomScenario({
        graph_id: graphId,
        start_node_id: startId,
        goal_node_id: goalId,
        num_edges: 5,
      })
      setRandomAffectedEdges(payload.affected_edges)
      setScenarioId(payload.scenario_id)
      clearRouteResult()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'KhĂ´ng thá»ƒ sinh scenario ngáº«u nhiĂªn.')
    } finally {
      setRandomRunning(false)
    }
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
        const payload = await runComparison(input, ['UCS', 'A_STAR', 'BFS', 'DFS', 'GREEDY', 'BIDIRECTIONAL'])
        setComparisonResults(payload.results)
        setResult(payload.results[0] ?? null)
      } else if (algorithm === 'A_STAR' || algorithm === 'UCS' || algorithm === 'BFS' || algorithm === 'DFS' || algorithm === 'GREEDY' || algorithm === 'BIDIRECTIONAL') {
        const primary = await runSearch({ ...input, algorithm })
        if (['LANDMARK_FLOOD', 'LANDMARK_CONGESTION'].includes(scenarioId) || scenarioId.startsWith('SCENARIO_')) {
          const alternatives = await runAlternatives({ ...input, algorithm, limit: 2 })
          setComparisonResults(alternatives.results)
          setResult(alternatives.results[0] ?? primary)
        } else {
          setResult(primary)
        }
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không thể chạy thuật toán.')
    } finally {
      setRunning(false)
    }
  }

  function moveTourStop(fromIndex: number, toIndex: number) {
    if (fromIndex < 0 || fromIndex >= tourStops.length) return
    if (toIndex < 0 || toIndex >= tourStops.length) return
    if (fromIndex === toIndex) return
    const updated = [...tourStops]
    const [movedItem] = updated.splice(fromIndex, 1)
    updated.splice(toIndex, 0, movedItem)
    setTourStops(updated)
  }

  function handleStopDragStart(event: React.DragEvent, index: number) {
    setDraggedIndex(index)
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(index))
  }

  function handleStopDragOver(event: React.DragEvent, index: number) {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    if (dragOverIndex !== index) {
      setDragOverIndex(index)
    }
  }

  function handleStopDrop(event: React.DragEvent, targetIndex: number) {
    event.preventDefault()
    const data = event.dataTransfer.getData('text/plain')
    let fromIndex = draggedIndex
    if (data !== '' && !isNaN(Number(data))) {
      fromIndex = Number(data)
    }
    if (fromIndex !== null && fromIndex !== undefined && !isNaN(fromIndex)) {
      moveTourStop(fromIndex, targetIndex)
    }
    setDraggedIndex(null)
    setDragOverIndex(null)
  }

  function handleStopDragEnd() {
    setDraggedIndex(null)
    setDragOverIndex(null)
  }

  function clearBoard() {
    clearRouteResult()
    setAlgorithm('') // Reset thuật toán về không chọn
    setStartId('') // Reset điểm bắt đầu
    setGoalId('') // Reset điểm đích/kết thúc
    setTourStops([]) // Reset toàn bộ điểm kết thúc/giao hàng
    setDraggedIndex(null)
    setDragOverIndex(null)
    setPickTarget(null)
    setError('')
  }


  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <button
            type="button"
            className="mobile-menu-btn"
            onClick={() => setIsMobileDrawerOpen((prev) => !prev)}
            title="Menu"
            aria-label="Toggle menu"
          >
            ☰
          </button>
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
          <button
            type="button"
            className="sidebar-toggle-btn"
            onClick={() => setIsSidebarCollapsed((prev) => !prev)}
            title={isSidebarCollapsed ? t('expand_sidebar', lang) : t('collapse_sidebar', lang)}
            aria-label={isSidebarCollapsed ? t('expand_sidebar', lang) : t('collapse_sidebar', lang)}
          >
            {isSidebarCollapsed ? `▶ ${t('expand_sidebar', lang)}` : `◀ ${t('collapse_sidebar', lang)}`}
          </button>
          <LanguageToggle lang={lang} onLanguageChange={setLang} />
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

      <div className={`workspace${isSidebarCollapsed ? ' is-sidebar-collapsed' : ''}`}>
        {isMobileDrawerOpen && (
          <div
            className="mobile-drawer-backdrop"
            onClick={() => setIsMobileDrawerOpen(false)}
            aria-hidden="true"
          />
        )}
        <aside className={`control-panel${isSidebarCollapsed ? ' is-collapsed' : ''}${isMobileDrawerOpen ? ' is-mobile-open' : ''}`}>
          <div className="panel-heading">
            <div className="panel-title-row">
              <h1>{t('panel_title', lang)}</h1>
              <button
                type="button"
                className="mobile-drawer-close-btn"
                onClick={() => setIsMobileDrawerOpen(false)}
                aria-label="Close menu"
              >
                ✕
              </button>
            </div>
            <p>{t('panel_subtitle', lang)}</p>
          </div>

          <form onSubmit={executeSearch}>
            <label>
              {t('dataset_label', lang)}
              <select value={graphId} onChange={(event) => selectGraph(event.target.value)}>
                {catalog.map((item) => (
                  <option key={item.graph_id} value={item.graph_id}>
                    {translateGraphLabel(item.label, lang)} · {item.node_count} {t('nodes_count', lang)}
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
                <optgroup label={t('group_two_point', lang)}>
                  <option value="A_STAR">{t('alg_a_star', lang)}</option>
                  <option value="UCS">{t('alg_ucs', lang)}</option>
                  <option value="BFS">{t('alg_bfs', lang)}</option>
                  <option value="DFS">{t('alg_dfs', lang)}</option>
                  <option value="GREEDY">{t('alg_greedy', lang)}</option>
                  <option value="BIDIRECTIONAL">{t('alg_bidirectional', lang)}</option>
                </optgroup>
                <optgroup label={t('group_multi_stop', lang)}>
                  <option value="HELD_KARP">{t('alg_held_karp', lang)}</option>
                  <option value="NEAREST_NEIGHBOR">{t('alg_nearest_neighbor', lang)}</option>
                </optgroup>
                <optgroup label={t('group_comparison', lang)}>
                  <option value="COMPARE">{t('alg_compare', lang)}</option>
                  <option value="OPTIMIZE_TOUR">{t('alg_optimize_tour', lang)}</option>
                </optgroup>
              </select>
            </label>

            <label>
              {t('scenario_label', lang)}
              <select value={scenarioId.startsWith('SCENARIO_') ? 'RANDOM' : scenarioId} onChange={(event) => selectScenario(event.target.value)}>
                <option value="LANDMARK_CONGESTION">{t('scenario_congestion', lang)}</option>
                <option value="LANDMARK_FLOOD">{t('scenario_flood', lang)}</option>
                <option value="RANDOM">{t('scenario_random', lang)}</option>
              </select>
            </label>
            {randomAffectedEdges.length > 0 && (
              <div className="scenario-summary scenario-summary--random">
                <span>RANDOM</span>
                <strong>{t('random_affected', lang, { count: randomAffectedEdges.length })}</strong>
                <small>{randomAffectedEdges.map((edge) => `${edge.edge_id} (${edge.status === 'CONGESTED' ? t('status_congested', lang) : edge.status === 'FLOODED' ? t('status_flooded', lang) : t('status_closed', lang)})`).join(' · ')}</small>
              </div>
            )}

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
                  <label>{t('stops_header', lang)} ({tourStops.length}/{MAX_TOUR_STOPS})</label>
                  <div className="stops-chips">
                    {tourStops.map((stopId, idx) => {
                      const loc = locations.find((item) => item.node_id === stopId)
                      const isDragging = draggedIndex === idx
                      const isDragOver = dragOverIndex === idx
                      return (
                        <span
                          key={`${stopId}-${idx}`}
                          className={`stop-chip${isDragging ? ' is-dragging' : ''}${isDragOver ? ' is-drag-over' : ''}`}
                          draggable={true}
                          onDragStart={(event) => handleStopDragStart(event, idx)}
                          onDragOver={(event) => handleStopDragOver(event, idx)}
                          onDrop={(event) => handleStopDrop(event, idx)}
                          onDragEnd={handleStopDragEnd}
                          title="Kéo thả hoặc dùng nút ▲ ▼ để thay đổi thứ tự điểm dừng"
                        >
                          <span className="drag-handle" aria-hidden="true">⋮⋮</span>
                          <small>#{idx + 1}</small>
                          <span className="stop-name-text">{loc ? loc.name : stopId}</span>
                          <div className="stop-reorder-btns">
                            <button
                              type="button"
                              className="reorder-btn move-up"
                              title="Di chuyển lên trước"
                              aria-label={`Di chuyển ${loc ? loc.name : stopId} lên trước`}
                              disabled={idx === 0}
                              onClick={(e) => {
                                e.stopPropagation()
                                moveTourStop(idx, idx - 1)
                              }}
                            >
                              ▲
                            </button>
                            <button
                              type="button"
                              className="reorder-btn move-down"
                              title="Di chuyển xuống sau"
                              aria-label={`Di chuyển ${loc ? loc.name : stopId} xuống sau`}
                              disabled={idx === tourStops.length - 1}
                              onClick={(e) => {
                                e.stopPropagation()
                                moveTourStop(idx, idx + 1)
                              }}
                            >
                              ▼
                            </button>
                          </div>
                          <button
                            type="button"
                            className="remove-chip-btn"
                            title="Xóa điểm dừng"
                            aria-label={`Xóa điểm dừng ${loc ? loc.name : stopId}`}
                            onClick={(e) => {
                              e.stopPropagation()
                              setTourStops(tourStops.filter((_, i) => i !== idx))
                            }}
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
                  {tourStops.length < MAX_TOUR_STOPS && (
                    <LocationPicker
                      label={t('add_stop_label', lang)}
                      value=""
                      locations={locations.filter((item) => item.node_id !== startId && !tourStops.includes(item.node_id))}
                      onChange={selectTourStop}
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

            <div className="panel-actions-group">
              <button className="generate-button" type="button" onClick={reloadGraph}>
                <span aria-hidden="true">⌘</span>
                {t('reload_graph', lang)}
              </button>
              <button className="panel-clear-button" type="button" onClick={clearBoard}>
                <span aria-hidden="true">🗑️</span>
                {t('clear_results', lang)}
              </button>
            </div>
            <button
              className="mobile-run-button"
              type="submit"
              disabled={!canRun}
              title={!algorithm ? t('select_alg_first', lang) : !startId ? t('select_start_first', lang) : t('run_algorithm', lang)}
            >
              <span aria-hidden="true">▷</span>
              {running ? t('running', lang) : t('run_algorithm', lang)}
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
            {t('api_connected', lang)}
          </div>
        </aside>

        <main className="canvas-area" aria-live="polite">
          <div className="canvas-heading">
            <div>
              <span className="eyebrow">{t('eyebrow_title', lang)}</span>
              <h2>{selectedGraph ? translateGraphLabel(selectedGraph.label, lang) : t('loading_graph', lang)}</h2>
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
                frontierNodeIds={traceVisualState.frontierNodeIds}
                closedNodeIds={traceVisualState.closedNodeIds}
                currentNodeId={traceVisualState.currentNodeId}
                startId={startId}
                goalId={goalId}
                pickTarget={pickTarget}
                onNodePick={pickNode}
                onPickTargetChange={setPickTarget}
                activeAnimatedNodeId={currentAnimatedNodeInfo?.nodeId}
                activeAnimatedNodeLabel={currentAnimatedNodeInfo?.label}
                tourStopMarkers={tourStopMarkers}
                tourStopCount={tourStops.length}
                isTourMode={isTourMode}
                isSidebarCollapsed={isSidebarCollapsed}
                hideEndpoints={!algorithm}
                lang={lang}
                affectedEdges={randomAffectedEdges}
              />
            ) : (
              <div className="map-placeholder">{t('panel_subtitle', lang)}</div>
            )}
            <div className="legend" aria-label={t('legend_title', lang)}>
              <div className="legend-header">
                <span className="legend-icon" aria-hidden="true">📌</span>
                <strong>{t('legend_title', lang)}</strong>
              </div>
              <div className="legend-items">
                <span className="legend-item"><i className="legend-line open" />{t('legend_normal_road', lang)}</span>
                <span className="legend-item"><i className="legend-line congested" />{t('legend_congested_road', lang)}</span>
                <span className="legend-item"><i className="legend-line flooded" />{t('legend_flooded_road', lang)}</span>
                <span className="legend-item"><i className="legend-line blocked" />{t('legend_closed_road', lang)}</span>
                <span className="legend-item"><i className="legend-node" />{t('legend_node', lang)}</span>
                <span className="legend-item"><i className="legend-node legend-node--frontier" />{t('legend_frontier', lang)}</span>
                <span className="legend-item"><i className="legend-node legend-node--current" />{t('legend_current', lang)}</span>
                <span className="legend-item"><i className="legend-node legend-node--closed" />{t('legend_closed', lang)}</span>
                <span className="legend-item"><i className="legend-line path" />{t('legend_optimal_path', lang)}</span>
                <span className="legend-item"><i className="legend-line boundary" />{t('legend_boundary', lang)}</span>
              </div>
            </div>
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


          {result && !tourResult && (
            <section className="metrics-bar" aria-label="Route search metrics">
              <div className="metric-chip"><span>{t('metric_algorithm', lang)}</span><strong>{result.algorithm}</strong></div>
              <div className="metric-chip"><span>{t('explored_nodes', lang)}</span><strong>{result.metrics.explored_nodes}</strong></div>
              <div className="metric-chip"><span>{t('dist_total', lang)}</span><strong>{metric(result.metrics.distance_km, 2)} km</strong></div>
              <div className="metric-chip"><span>{t('time_eta', lang)}</span><strong>{metric(result.metrics.estimated_time_min, 2)} min</strong></div>
              <div className="metric-chip"><span>{t('total_cost', lang)}</span><strong>{metric(result.metrics.total_cost, 3)}</strong></div>
              <div className="metric-chip"><span>{t('metric_runtime', lang)}</span><strong>{metric(result.metrics.processing_time_ms, 3)} ms</strong></div>
            </section>
          )}

          {error && <div className="error-banner" role="alert">{error}</div>}

          {comparisonResults.length > 0 && algorithm === 'COMPARE' && (
            <section className="comparison-section" aria-label="Comparison results">
              {comparisonInsight && <p className="comparison-insight">{t('comparison_insight', lang, {
                cost: comparisonInsight.bestCost.algorithm,
                distance: comparisonInsight.shortest.algorithm,
                time: comparisonInsight.fastest.algorithm,
                routes: comparisonInsight.distinctRouteCount,
              })}</p>}
              <div className="comparison-grid">{comparisonResults.map((item) => (
                <button key={item.algorithm} type="button" onClick={() => setResult(item)}>
                  <span>{item.algorithm}</span>
                  <strong>{item.metrics.total_cost.toFixed(3)} cost</strong>
                  <small>{item.metrics.distance_km.toFixed(2)} km · {item.metrics.estimated_time_min.toFixed(2)} min</small>
                  <small>{item.metrics.explored_nodes} nodes · {item.metrics.processing_time_ms.toFixed(3)} ms</small>
                </button>
              ))}</div>
            </section>
          )}

          {alternativeRoutes.length > 0 && (
            <section className="alternative-routes-section" aria-label={t('alternative_routes_title', lang)}>
              <div className="alternative-routes-header">
                <div>
                  <h3>{t('alternative_routes_title', lang)}</h3>
                  <p>{t('alternative_routes_subtitle', lang)}</p>
                </div>
                <span>{alternativeRoutes.length} route(s)</span>
              </div>
              <div className="alternative-routes-grid">
                {alternativeRoutes.map((candidate, index) => (
                  <button
                    key={`${candidate.algorithm}-${candidate.edge_ids.join('-')}`}
                    type="button"
                    className={`alternative-route-card${index === 0 ? ' alternative-route-card--optimal' : ''}${result?.edge_ids.join('|') === candidate.edge_ids.join('|') ? ' alternative-route-card--selected' : ''}`}
                    onClick={() => selectAlternativeRoute(candidate)}
                  >
                    <div className="alternative-route-card__topline">
                      <strong>{index === 0 ? t('optimal_route_badge', lang) : t('alternative_route_badge', lang)}</strong>
                      <span>{candidate.algorithm}</span>
                    </div>
                    <div className="alternative-route-card__cost">{candidate.metrics.total_cost.toFixed(3)}</div>
                    <small>{t('total_cost', lang)} · {candidate.metrics.distance_km.toFixed(2)} km · {candidate.metrics.estimated_time_min.toFixed(2)} min</small>
                    {index === 0 && <small className="alternative-route-card__proof">{t('cost_proof', lang)}</small>}
                    <code>{candidate.path.join(' → ')}</code>
                  </button>
                ))}
              </div>
            </section>
          )}

          {tourResult && (
            <section className="tour-result-card" aria-label="Tour result">
              {/* 1. Header with Landmark Stop Badges */}
              <div className="tour-header">
                <div className="tour-header-meta">
                  <span className="tour-kicker">{t('tour_kicker', lang)} · {tourResult.scenario}</span>
                  <span className="tour-status-pill">{tourResult.data_status}</span>
                </div>
                <h3 className="tour-title-route">{t('tour_route', lang)}</h3>

                <div className="tour-sequence-badges">
                  {tourResult.visit_order.map((nodeId, idx) => {
                    const isDepot = idx === 0 || idx === tourResult.visit_order.length - 1
                    const loc = locations.find((item) => item.node_id === nodeId)
                    const locName = loc ? loc.name : nodeId
                    return (
                      <div key={`${nodeId}-${idx}`} className="tour-seq-item">
                        <span className={`tour-stop-badge ${isDepot ? 'tour-stop-badge--depot' : 'tour-stop-badge--stop'}`}>
                          {isDepot ? '🏠 ' + t('depot_badge', lang) : `📍 ${t('stop_badge', lang, { no: idx })}`}
                        </span>
                        <span className="tour-stop-name">{locName}</span>
                        <span className="tour-stop-id"><code>{nodeId}</code></span>
                        {idx < tourResult.visit_order.length - 1 && (
                          <span className="tour-seq-arrow" aria-hidden="true">➔</span>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* 2. Before vs After Optimization Comparison */}
              <div className="tour-optimization-comparison-card">
                <div className="tour-opt-header">
                  <h4>⚡ {t('tour_savings_title', lang)}</h4>
                  <div className="tour-savings-highlight-badge">
                    🎉 {t('tour_savings_badge', lang, {
                      dist: (tourResult.comparison.original_order_distance_km - tourResult.total_distance_km).toFixed(2),
                      time: (tourResult.comparison.original_order_time_min - tourResult.estimated_time_min).toFixed(2),
                      percent: tourResult.comparison.selected_savings_percent.toFixed(1),
                    })}
                  </div>
                </div>

                <div className="tour-comparison-before-after">
                  {/* Left: Original Sequence */}
                  <div className="tour-compare-col tour-compare-col--baseline">
                    <div className="tour-compare-col-header">
                      <span className="compare-badge compare-badge--baseline">📝 {t('original_order_title', lang)}</span>
                    </div>
                    <div className="tour-compare-seq-text">
                      {tourResult.comparison.original_visit_order.map((nodeId, i) => {
                        const loc = locations.find((item) => item.node_id === nodeId)
                        return (
                          <span key={i} className="mini-stop-chip">
                            {loc ? loc.name : nodeId}
                          </span>
                        )
                      })}
                    </div>
                    <div className="tour-compare-metrics">
                      <div className="mini-metric">
                        <span>{t('dist_total', lang)}</span>
                        <strong>{tourResult.comparison.original_order_distance_km.toFixed(2)} km</strong>
                      </div>
                      <div className="mini-metric">
                        <span>{t('time_eta', lang)}</span>
                        <strong>{tourResult.comparison.original_order_time_min.toFixed(2)} min</strong>
                      </div>
                      <div className="mini-metric">
                        <span>{t('total_cost', lang)}</span>
                        <strong>{tourResult.comparison.original_order_cost.toFixed(3)}</strong>
                      </div>
                    </div>
                  </div>

                  {/* Right: Optimized Sequence */}
                  <div className="tour-compare-col tour-compare-col--optimized">
                    <div className="tour-compare-col-header">
                      <span className="compare-badge compare-badge--optimized">🚀 {t('optimized_order_title', lang)}</span>
                    </div>
                    <div className="tour-compare-seq-text">
                      {tourResult.visit_order.map((nodeId, i) => {
                        const loc = locations.find((item) => item.node_id === nodeId)
                        return (
                          <span key={i} className="mini-stop-chip mini-stop-chip--optimized">
                            {loc ? loc.name : nodeId}
                          </span>
                        )
                      })}
                    </div>
                    <div className="tour-compare-metrics">
                      <div className="mini-metric">
                        <span>{t('dist_total', lang)}</span>
                        <strong className="text-success">{tourResult.total_distance_km.toFixed(2)} km</strong>
                      </div>
                      <div className="mini-metric">
                        <span>{t('time_eta', lang)}</span>
                        <strong className="text-success">{tourResult.estimated_time_min.toFixed(2)} min</strong>
                      </div>
                      <div className="mini-metric">
                        <span>{t('total_cost', lang)}</span>
                        <strong className="text-success">{tourResult.total_cost.toFixed(3)}</strong>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* 3. Theoretical Guarantee & Algorithm Complexity Card */}
              {algorithm === 'OPTIMIZE_TOUR' ? (
                <div className="tour-guarantee-comparison" aria-label="Guarantee comparison">
                  <div className="tour-guarantee-card optimal-card">
                    <span className="guarantee-tag">{t('optimal_tag', lang)}</span>
                    <h4>Held-Karp DP</h4>
                    <div className="card-cost">{tourResult.comparison.held_karp_cost.toFixed(3)} cost</div>
                    <div className="card-guarantee">OPTIMAL_HELD_KARP · O(N²·2ᴺ)</div>
                    <p>{t('held_karp_badge_desc', lang)}</p>
                  </div>
                  <div className="tour-guarantee-card heuristic-card">
                    <span className="guarantee-tag">{t('heuristic_tag', lang)}</span>
                    <h4>Nearest Neighbor</h4>
                    <div className="card-cost">{tourResult.comparison.nearest_neighbor_cost.toFixed(3)} cost</div>
                    <div className="card-guarantee">APPROXIMATE_NEAREST_NEIGHBOR · O(N²)</div>
                    <p>{t('nn_badge_desc', lang)}</p>
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
                <div className={`tour-guarantee-banner ${tourResult.guarantee === 'OPTIMAL_HELD_KARP' ? 'tour-guarantee-banner--optimal' : 'tour-guarantee-banner--heuristic'}`}>
                  <div className="guarantee-badge-header">
                    <span className="guarantee-tag-pill">
                      {tourResult.guarantee === 'OPTIMAL_HELD_KARP' ? t('optimal_tag', lang) : t('heuristic_tag', lang)}
                    </span>
                    <span className="guarantee-title-text">
                      {algorithm === 'HELD_KARP' ? t('alg_held_karp', lang) : t('alg_nearest_neighbor', lang)}
                    </span>
                    <span className="guarantee-algo-code">
                      <code>{tourResult.guarantee}</code>
                    </span>
                  </div>
                  <p className="guarantee-desc-text">
                    {algorithm === 'HELD_KARP'
                      ? t('held_karp_badge_desc', lang)
                      : `${t('nn_badge_desc', lang)} · ${t('approx_gap_title', lang)}: +${tourResult.comparison.approximation_gap_percent.toFixed(2)}%`}
                  </p>
                </div>
              )}

              {/* 4. Detailed Legs Breakdown Table */}
              <div className="legs-table-container">
                <h4>{t('legs_breakdown', lang, { count: tourResult.legs.length })}</h4>
                <table className="legs-table">
                  <thead>
                    <tr>
                      <th>{t('leg_no', lang)}</th>
                      <th>{t('from_node', lang)}</th>
                      <th>{t('to_node', lang)}</th>
                      <th>{t('leg_dist', lang)}</th>
                      <th>{t('leg_time', lang)}</th>
                      <th>{t('leg_cost', lang)}</th>
                      <th>{t('path_nodes', lang)}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tourResult.legs.map((leg, idx) => {
                      const isFirst = idx === 0
                      const isLast = idx === tourResult.legs.length - 1
                      const fromLoc = locations.find((loc) => loc.node_id === leg.from_node_id)
                      const toLoc = locations.find((loc) => loc.node_id === leg.to_node_id)
                      const fromName = fromLoc ? fromLoc.name : leg.from_node_id
                      const toName = toLoc ? toLoc.name : leg.to_node_id

                      return (
                        <tr key={`${leg.from_node_id}-${leg.to_node_id}-${idx}`}>
                          <td><span className="leg-badge-num">#{idx + 1}</span></td>
                          <td>
                            <div className="leg-node-block">
                              <span className="leg-node-role">{isFirst ? '🏠 ' + t('depot_badge', lang) : `📍 ${t('stop_badge', lang, { no: idx })}`}</span>
                              <span className="leg-node-name">{fromName}</span>
                              <span className="leg-node-id"><code>{leg.from_node_id}</code></span>
                            </div>
                          </td>
                          <td>
                            <div className="leg-node-block">
                              <span className="leg-node-role">{isLast ? '🏠 ' + t('depot_badge', lang) : `📍 ${t('stop_badge', lang, { no: idx + 1 })}`}</span>
                              <span className="leg-node-name">{toName}</span>
                              <span className="leg-node-id"><code>{leg.to_node_id}</code></span>
                            </div>
                          </td>
                          <td><strong>{leg.distance_km.toFixed(2)} km</strong></td>
                          <td><strong>{leg.travel_time_min.toFixed(2)} {t('minutes', lang)}</strong></td>
                          <td><strong className="text-primary">{leg.total_cost.toFixed(3)}</strong></td>
                          <td>
                            <details className="leg-subpath-details">
                              <summary>{t('view_subpath_nodes', lang, { count: leg.path.length })}</summary>
                              <div className="leg-path-seq">{leg.path.join(' → ')}</div>
                            </details>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {result && !tourResult && (
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
