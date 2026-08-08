import { useEffect, useMemo, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import {
  type GeoJSONSource,
  type MapGeoJSONFeature,
  type MapLayerMouseEvent,
  type StyleSpecification,
} from 'maplibre-gl'
import recenterGraphIcon from '../../assets/recenter-graph.png'
import type { GraphPayload } from '../../lib/graph'
import {
  buildEdgeFeatureCollection,
  buildNodeFeatureCollection,
  buildRouteFeatureCollection,
  type NodeFeatureProperties,
} from './mapData'

export type EndpointPickTarget = 'START' | 'GOAL'

type RouteMapProps = {
  graph: GraphPayload
  pathEdgeIds?: string[]
  visiblePathEdgeCount?: number
  pathNodeIds?: string[]
  exploredNodeIds?: string[]
  startId?: string
  goalId?: string
  pickTarget: EndpointPickTarget | null
  onNodePick: (target: EndpointPickTarget, nodeId: string) => void
  onPickTargetChange: (target: EndpointPickTarget | null) => void
}

const BASEMAP_STYLE_URL = import.meta.env.VITE_BASEMAP_STYLE_URL
  || 'https://tiles.openfreemap.org/styles/liberty'
const EMPTY_FEATURE_COLLECTION = { type: 'FeatureCollection' as const, features: [] }
const FALLBACK_STYLE: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{
    id: 'fallback-background',
    type: 'background',
    paint: { 'background-color': '#eef1f2' },
  }],
}

const SOURCE_EDGES = 'floodroute-edges'
const SOURCE_ROUTE = 'floodroute-route'
const SOURCE_NODES = 'floodroute-nodes'
const LAYER_NODE_HITBOX = 'floodroute-node-hitbox'

function addGraphLayers(map: maplibregl.Map) {
  if (!map.getSource(SOURCE_EDGES)) {
    map.addSource(SOURCE_EDGES, { type: 'geojson', data: EMPTY_FEATURE_COLLECTION })
  }
  if (!map.getSource(SOURCE_ROUTE)) {
    map.addSource(SOURCE_ROUTE, { type: 'geojson', data: EMPTY_FEATURE_COLLECTION })
  }
  if (!map.getSource(SOURCE_NODES)) {
    map.addSource(SOURCE_NODES, { type: 'geojson', data: EMPTY_FEATURE_COLLECTION })
  }

  if (!map.getLayer('floodroute-edge-open')) {
    map.addLayer({
      id: 'floodroute-edge-open',
      type: 'line',
      source: SOURCE_EDGES,
      filter: ['==', ['get', 'is_closed'], false],
      paint: {
        'line-color': '#00714d',
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 1.4, 17, 3.4],
        'line-opacity': 0.58,
      },
      layout: { 'line-cap': 'round', 'line-join': 'round' },
    })
  }
  if (!map.getLayer('floodroute-edge-closed')) {
    map.addLayer({
      id: 'floodroute-edge-closed',
      type: 'line',
      source: SOURCE_EDGES,
      filter: ['==', ['get', 'is_closed'], true],
      paint: {
        'line-color': '#ba1a1a',
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 2, 17, 4],
        'line-opacity': 0.78,
        'line-dasharray': [2, 2.5],
      },
      layout: { 'line-cap': 'round', 'line-join': 'round' },
    })
  }
  if (!map.getLayer('floodroute-route-halo')) {
    map.addLayer({
      id: 'floodroute-route-halo',
      type: 'line',
      source: SOURCE_ROUTE,
      paint: {
        'line-color': '#ffffff',
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 7, 17, 13],
        'line-opacity': 0.92,
      },
      layout: { 'line-cap': 'round', 'line-join': 'round' },
    })
  }
  if (!map.getLayer('floodroute-route')) {
    map.addLayer({
      id: 'floodroute-route',
      type: 'line',
      source: SOURCE_ROUTE,
      paint: {
        'line-color': '#6d28d9',
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 4, 17, 8],
        'line-opacity': 1,
      },
      layout: { 'line-cap': 'round', 'line-join': 'round' },
    })
  }
  if (!map.getLayer('floodroute-nodes')) {
    map.addLayer({
      id: 'floodroute-nodes',
      type: 'circle',
      source: SOURCE_NODES,
      paint: {
        'circle-radius': [
          'match', ['get', 'visual_state'],
          'start', 9,
          'goal', 9,
          'path', 6,
          'explored', 5,
          ['interpolate', ['linear'], ['zoom'], 13, 2.5, 17, 4],
        ],
        'circle-color': [
          'match', ['get', 'visual_state'],
          'start', '#fef3c7',
          'goal', '#fce7f3',
          'path', '#ede9fe',
          'explored', '#ffddb8',
          '#ffffff',
        ],
        'circle-stroke-color': [
          'match', ['get', 'visual_state'],
          'start', '#d97706',
          'goal', '#db2777',
          'path', '#6d28d9',
          'explored', '#a36700',
          '#424754',
        ],
        'circle-stroke-width': [
          'match', ['get', 'visual_state'],
          'start', 4,
          'goal', 4,
          'path', 2.5,
          1.5,
        ],
        'circle-opacity': 0.94,
      },
    })
  }
  if (!map.getLayer(LAYER_NODE_HITBOX)) {
    map.addLayer({
      id: LAYER_NODE_HITBOX,
      type: 'circle',
      source: SOURCE_NODES,
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 12, 7, 17, 12],
        'circle-opacity': 0,
      },
    })
  }
}

function featureProperties(feature: MapGeoJSONFeature | undefined): NodeFeatureProperties | null {
  const properties = feature?.properties
  if (!properties || typeof properties.node_id !== 'string') return null
  return properties as NodeFeatureProperties
}

function popupContent(properties: NodeFeatureProperties): HTMLElement {
  const root = document.createElement('div')
  root.className = 'map-node-popup'
  const title = document.createElement('strong')
  title.textContent = properties.display_name
  const id = document.createElement('span')
  id.textContent = properties.node_id
  const meta = document.createElement('small')
  meta.textContent = `${properties.node_type} · ${properties.label_status === 'DERIVED' ? 'DERIVED LABEL' : properties.data_status}`
  root.append(title, id, meta)
  return root
}

function graphBounds(graph: GraphPayload): maplibregl.LngLatBounds | null {
  const coordinates = graph.nodes.flatMap<[number, number]>((node) => (
    node.latitude === null || node.longitude === null
      ? []
      : [[node.longitude, node.latitude]]
  ))
  if (!coordinates.length) return null
  const bounds = new maplibregl.LngLatBounds(coordinates[0], coordinates[0])
  for (const coordinate of coordinates.slice(1)) bounds.extend(coordinate)
  return bounds
}

export function RouteMap({
  graph,
  pathEdgeIds = [],
  visiblePathEdgeCount = pathEdgeIds.length,
  pathNodeIds = [],
  exploredNodeIds = [],
  startId,
  goalId,
  pickTarget,
  onNodePick,
  onPickTargetChange,
}: RouteMapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const hoverPopupRef = useRef<maplibregl.Popup | null>(null)
  const clickPopupRef = useRef<maplibregl.Popup | null>(null)
  const pickTargetRef = useRef(pickTarget)
  const onNodePickRef = useRef(onNodePick)
  const onPickTargetChangeRef = useRef(onPickTargetChange)
  const fallbackAppliedRef = useRef(false)
  const styleReadyRef = useRef(false)
  const [styleRevision, setStyleRevision] = useState(0)
  const [basemapWarning, setBasemapWarning] = useState('')

  pickTargetRef.current = pickTarget
  onNodePickRef.current = onNodePick
  onPickTargetChangeRef.current = onPickTargetChange

  const edgeData = useMemo(() => buildEdgeFeatureCollection(graph), [graph])
  const nodeData = useMemo(() => buildNodeFeatureCollection(graph, {
    startId,
    goalId,
    pathNodeIds,
    exploredNodeIds,
  }), [exploredNodeIds, goalId, graph, pathNodeIds, startId])
  const routeData = useMemo(
    () => buildRouteFeatureCollection(graph, pathEdgeIds.slice(0, visiblePathEdgeCount)),
    [graph, pathEdgeIds, visiblePathEdgeCount],
  )

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASEMAP_STYLE_URL,
      center: [106.756, 10.849],
      zoom: 14,
      attributionControl: false,
    })
    mapRef.current = map
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right')
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 120 }), 'bottom-left')
    map.addControl(new maplibregl.AttributionControl({
      compact: true,
      customAttribution: 'Basemap © OpenFreeMap · © OpenStreetMap contributors',
    }), 'bottom-right')

    const onStyleLoad = () => {
      styleReadyRef.current = true
      addGraphLayers(map)
      setStyleRevision((value) => value + 1)
      if (!fallbackAppliedRef.current) setBasemapWarning('')
    }
    const onError = () => {
      if (!styleReadyRef.current && !fallbackAppliedRef.current) {
        fallbackAppliedRef.current = true
        setBasemapWarning('Không tải được basemap; graph vẫn hoạt động trên nền dự phòng.')
        map.setStyle(FALLBACK_STYLE)
        return
      }
      setBasemapWarning('Một phần basemap không tải được; dữ liệu graph không bị ảnh hưởng.')
    }
    const onMouseEnter = (event: MapLayerMouseEvent) => {
      map.getCanvas().style.cursor = 'pointer'
      const properties = featureProperties(event.features?.[0])
      if (!properties) return
      hoverPopupRef.current?.remove()
      hoverPopupRef.current = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        offset: 12,
      })
        .setLngLat(event.lngLat)
        .setDOMContent(popupContent(properties))
        .addTo(map)
    }
    const onMouseLeave = () => {
      map.getCanvas().style.cursor = ''
      hoverPopupRef.current?.remove()
      hoverPopupRef.current = null
    }
    const onNodeClick = (event: MapLayerMouseEvent) => {
      const properties = featureProperties(event.features?.[0])
      if (!properties) return
      const target = pickTargetRef.current
      if (target) {
        onNodePickRef.current(target, properties.node_id)
        onPickTargetChangeRef.current(null)
      }
      clickPopupRef.current?.remove()
      clickPopupRef.current = new maplibregl.Popup({ closeButton: true, offset: 14 })
        .setLngLat(event.lngLat)
        .setDOMContent(popupContent(properties))
        .addTo(map)
    }

    map.on('style.load', onStyleLoad)
    map.on('error', onError)
    map.on('mouseenter', LAYER_NODE_HITBOX, onMouseEnter)
    map.on('mouseleave', LAYER_NODE_HITBOX, onMouseLeave)
    map.on('click', LAYER_NODE_HITBOX, onNodeClick)

    return () => {
      hoverPopupRef.current?.remove()
      clickPopupRef.current?.remove()
      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !styleReadyRef.current) return
    ;(map.getSource(SOURCE_EDGES) as GeoJSONSource | undefined)?.setData(edgeData)
    ;(map.getSource(SOURCE_NODES) as GeoJSONSource | undefined)?.setData(nodeData)
    ;(map.getSource(SOURCE_ROUTE) as GeoJSONSource | undefined)?.setData(routeData)
  }, [edgeData, nodeData, routeData, styleRevision])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !styleReadyRef.current) return
    const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]))
    const endpoints = [startId, goalId].flatMap<[number, number]>((nodeId) => {
      if (!nodeId) return []
      const node = nodeById.get(nodeId)
      return !node || node.latitude === null || node.longitude === null
        ? []
        : [[node.longitude, node.latitude]]
    })
    if (endpoints.length === 1) {
      map.flyTo({ center: endpoints[0], zoom: Math.max(map.getZoom(), 16), essential: true })
    } else if (endpoints.length === 2) {
      map.fitBounds(new maplibregl.LngLatBounds(endpoints[0], endpoints[1]), {
        padding: 84,
        maxZoom: 17,
        duration: 650,
      })
    } else {
      const bounds = graphBounds(graph)
      if (bounds) map.fitBounds(bounds, { padding: 52, maxZoom: 16, duration: 0 })
    }
  }, [goalId, graph, startId, styleRevision])

  useEffect(() => {
    if (!pickTarget) return
    const cancel = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onPickTargetChange(null)
    }
    window.addEventListener('keydown', cancel)
    return () => window.removeEventListener('keydown', cancel)
  }, [onPickTargetChange, pickTarget])

  function resetView() {
    const map = mapRef.current
    const bounds = graphBounds(graph)
    if (map && bounds) map.fitBounds(bounds, { padding: 52, maxZoom: 16, duration: 500 })
  }

  return (
    <div className={`route-map-shell${pickTarget ? ' is-picking' : ''}`}>
      <div ref={containerRef} className="route-map" aria-label="Bản đồ graph FloodRoute" />
      <div className="map-pick-toolbar" aria-label="Chọn điểm trên bản đồ">
        <button
          type="button"
          className="pick-start"
          aria-pressed={pickTarget === 'START'}
          onClick={() => onPickTargetChange(pickTarget === 'START' ? null : 'START')}
        >
          Chọn START
        </button>
        <button
          type="button"
          className="pick-goal"
          aria-pressed={pickTarget === 'GOAL'}
          onClick={() => onPickTargetChange(pickTarget === 'GOAL' ? null : 'GOAL')}
        >
          Chọn GOAL
        </button>
        {pickTarget && (
          <button type="button" className="pick-cancel" onClick={() => onPickTargetChange(null)}>
            Hủy chọn
          </button>
        )}
      </div>
      {pickTarget && <div className="map-pick-hint">Click một node để đặt {pickTarget} · Esc để hủy</div>}
      <button
        type="button"
        className="map-reset-button"
        title="Đưa bản đồ về toàn bộ graph"
        aria-label="Đưa bản đồ về toàn bộ graph"
        onClick={resetView}
      >
        <img src={recenterGraphIcon} alt="" aria-hidden="true" />
      </button>
      {basemapWarning && <div className="basemap-warning" role="status">{basemapWarning}</div>}
      <div className="map-note">{graph.data_status} · {graph.graph_id}</div>
    </div>
  )
}
