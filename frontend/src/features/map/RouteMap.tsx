import { useEffect, useMemo, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import {
  type GeoJSONSource,
  type MapGeoJSONFeature,
  type MapLayerMouseEvent,
  type MapMouseEvent,
  type StyleSpecification,
} from 'maplibre-gl'
import recenterGraphIcon from '../../assets/recenter-graph.png'
import type { GraphPayload, ThuDucBoundary } from '../../lib/graph'
import { MAX_TOUR_STOPS } from '../../lib/tourSelection'
import {
  buildClosedEdgeMarkers,
  buildEdgeFeatureCollection,
  buildNodeFeatureCollection,
  buildRouteFeatureCollection,
  findNearestGraphNode,
  type ClosedEdgeMarkerData,
  type EdgeFeatureProperties,
  type NodeFeatureProperties,
} from './mapData'

export type EndpointPickTarget = 'START' | 'GOAL'

export type TourStopMarker = {
  nodeId: string
  name: string
  stopIndex: number
  latitude: number
  longitude: number
  isVisited: boolean
}

import { t, type Language } from '../../lib/i18n'

type RouteMapProps = {
  graph: GraphPayload
  boundary?: ThuDucBoundary | null
  boundaryWarning?: string
  pathEdgeIds?: string[]
  visiblePathEdgeCount?: number
  pathNodeIds?: string[]
  frontierNodeIds?: string[]
  closedNodeIds?: string[]
  currentNodeId?: string | null
  startId?: string
  goalId?: string
  pickTarget: EndpointPickTarget | null
  onNodePick: (target: EndpointPickTarget, nodeId: string) => void
  onPickTargetChange: (target: EndpointPickTarget | null) => void
  activeAnimatedNodeId?: string | null
  activeAnimatedNodeLabel?: string | null
  tourStopMarkers?: TourStopMarker[]
  tourStopCount?: number
  hideEndpoints?: boolean
  isTourMode?: boolean
  isSidebarCollapsed?: boolean
  lang?: Language
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
const SOURCE_BOUNDARY = 'floodroute-thu-duc-boundary'
const LAYER_NODE_HITBOX = 'floodroute-node-hitbox'
const LAYER_SELECTABLE_NODE = 'floodroute-selectable-node'
const LAYER_CLOSED_EDGE_HITBOX = 'floodroute-edge-closed-hitbox'
const DEFAULT_CENTER: [number, number] = [106.756, 10.849]
const MIN_CITY_ZOOM = 10.5
const MAX_BASEMAP_SNAP_DISTANCE_M = 200

function addGraphLayers(map: maplibregl.Map) {
  if (!map.getSource(SOURCE_BOUNDARY)) {
    map.addSource(SOURCE_BOUNDARY, { type: 'geojson', data: EMPTY_FEATURE_COLLECTION })
  }
  if (!map.getSource(SOURCE_EDGES)) {
    map.addSource(SOURCE_EDGES, { type: 'geojson', data: EMPTY_FEATURE_COLLECTION })
  }
  if (!map.getSource(SOURCE_ROUTE)) {
    map.addSource(SOURCE_ROUTE, { type: 'geojson', data: EMPTY_FEATURE_COLLECTION })
  }
  if (!map.getSource(SOURCE_NODES)) {
    map.addSource(SOURCE_NODES, { type: 'geojson', data: EMPTY_FEATURE_COLLECTION })
  }

  if (!map.getLayer('floodroute-thu-duc-boundary-fill')) {
    map.addLayer({
      id: 'floodroute-thu-duc-boundary-fill',
      type: 'fill',
      source: SOURCE_BOUNDARY,
      paint: {
        'fill-color': '#d52b1e',
        'fill-opacity': 0.035,
      },
    })
  }
  if (!map.getLayer('floodroute-thu-duc-boundary-line')) {
    map.addLayer({
      id: 'floodroute-thu-duc-boundary-line',
      type: 'line',
      source: SOURCE_BOUNDARY,
      paint: {
        'line-color': '#d52b1e',
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 2, 15, 4],
        'line-opacity': 0.95,
      },
      layout: { 'line-cap': 'round', 'line-join': 'round' },
    })
  }



  if (!map.getLayer('floodroute-edge-open')) {
    map.addLayer({
      id: 'floodroute-edge-open',
      type: 'line',
      source: SOURCE_EDGES,
      filter: ['==', ['get', 'is_closed'], false],
      paint: {
        'line-color': '#00714d',
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.2, 13, 1.8, 17, 3.8],
        'line-opacity': 0.65,
      },
      layout: { 'line-cap': 'round', 'line-join': 'round' },
    })
  }
  if (!map.getLayer('floodroute-edge-closed-halo')) {
    map.addLayer({
      id: 'floodroute-edge-closed-halo',
      type: 'line',
      source: SOURCE_EDGES,
      filter: ['==', ['get', 'is_closed'], true],
      paint: {
        'line-color': '#ff4d4f',
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 6, 14, 10, 17, 16],
        'line-opacity': 0.48,
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
        'line-color': '#dc2626',
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 3, 14, 5.5, 17, 8],
        'line-opacity': 1.0,
        'line-dasharray': [2.5, 2],
      },
      layout: { 'line-cap': 'round', 'line-join': 'round' },
    })
  }
  if (!map.getLayer('floodroute-edge-closed-hitbox')) {
    map.addLayer({
      id: 'floodroute-edge-closed-hitbox',
      type: 'line',
      source: SOURCE_EDGES,
      filter: ['==', ['get', 'is_closed'], true],
      paint: {
        'line-width': 24,
        'line-opacity': 0,
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
          'current', 8,
          'frontier', 6,
          'closed', 5,
          ['interpolate', ['linear'], ['zoom'], 13, 2.5, 17, 4],
        ],
        'circle-color': [
          'match', ['get', 'visual_state'],
          'start', '#fef3c7',
          'goal', '#fce7f3',
          'path', '#ede9fe',
          'current', '#fff3b0',
          'frontier', '#bfdbfe',
          'closed', '#d1d5db',
          '#ffffff',
        ],
        'circle-stroke-color': [
          'match', ['get', 'visual_state'],
          'start', '#d97706',
          'goal', '#db2777',
          'path', '#6d28d9',
          'current', '#ea580c',
          'frontier', '#2563eb',
          'closed', '#4b5563',
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
  if (!map.getLayer(LAYER_SELECTABLE_NODE)) {
    map.addLayer({
      id: LAYER_SELECTABLE_NODE,
      type: 'circle',
      source: SOURCE_NODES,
      filter: ['all', ['==', ['get', 'selectable'], true], ['==', ['get', 'visual_state'], 'default']],
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 10.5, 4.5, 15, 7],
        'circle-color': '#ffffff',
        'circle-stroke-color': '#0057b8',
        'circle-stroke-width': 2.4,
        'circle-opacity': 0.98,
        'circle-stroke-opacity': 1,
      },
    })
  }
  if (!map.getLayer(LAYER_NODE_HITBOX)) {
    map.addLayer({
      id: LAYER_NODE_HITBOX,
      type: 'circle',
      source: SOURCE_NODES,
      filter: ['==', ['get', 'selectable'], true],
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

function popupContent(properties: NodeFeatureProperties, snapDistanceM?: number): HTMLElement {
  const root = document.createElement('div')
  root.className = 'map-node-popup'
  const title = document.createElement('strong')
  title.textContent = properties.display_name
  const id = document.createElement('span')
  id.textContent = properties.node_id
  const meta = document.createElement('small')
  const snapText = snapDistanceM === undefined ? '' : ` · SNAP ${snapDistanceM.toFixed(0)} m`
  const category = properties.place_category ? ` · ${properties.place_category}` : ''
  meta.textContent = `${properties.node_type}${category} · ${properties.label_status === 'DERIVED' ? 'DERIVED LABEL' : properties.data_status}${snapText}`
  root.append(title, id, meta)
  return root
}

function edgeFeatureProps(feature: MapGeoJSONFeature | undefined): EdgeFeatureProperties | null {
  const properties = feature?.properties
  if (!properties || typeof properties.edge_id !== 'string') return null
  return properties as EdgeFeatureProperties
}

function closedEdgePopupContent(properties: EdgeFeatureProperties, lang: Language): HTMLElement {
  const root = document.createElement('div')
  root.className = 'map-edge-popup is-closed'

  const header = document.createElement('div')
  header.className = 'map-edge-popup-header'

  const badge = document.createElement('span')
  badge.className = 'map-edge-popup-badge'
  badge.textContent = lang === 'vi' ? '⛔ ĐÃ ĐÓNG ĐƯỜNG' : '⛔ ROAD CLOSED'

  const title = document.createElement('strong')
  title.className = 'map-edge-popup-title'
  title.textContent = properties.road_name || properties.edge_id

  header.append(badge, title)

  const meta = document.createElement('div')
  meta.className = 'map-edge-popup-meta'

  const idRow = document.createElement('div')
  idRow.className = 'map-edge-meta-row'
  idRow.innerHTML = `<span>ID:</span> <code>${properties.edge_id}</code> (${properties.from_node_id} ➔ ${properties.to_node_id})`

  const distKm = ((properties.distance_m || 0) / 1000).toFixed(2)
  const timeMin = (properties.free_flow_time_min || 0).toFixed(1)
  const statsRow = document.createElement('div')
  statsRow.className = 'map-edge-meta-row'
  statsRow.innerHTML = `<span>${lang === 'vi' ? 'Cự ly' : 'Distance'}:</span> <strong>${distKm} km</strong> (${timeMin} ${lang === 'vi' ? 'phút' : 'min'})`

  const reasonRow = document.createElement('div')
  reasonRow.className = 'map-edge-meta-row is-warning'
  reasonRow.innerHTML = `<span>⚠️ ${lang === 'vi' ? 'Lý do' : 'Reason'}:</span> ${
    lang === 'vi'
      ? 'Ngập lụt sâu do mưa lớn / triều cường dâng cao'
      : 'Severe flooding from heavy rainfall & tidal surge'
  }`

  const algRow = document.createElement('div')
  algRow.className = 'map-edge-meta-row is-blocked'
  algRow.innerHTML = `<span>🛡️ ${lang === 'vi' ? 'Thuật toán' : 'Algorithm'}:</span> ${
    lang === 'vi'
      ? 'Chi phí = ∞ (Bị loại bỏ 100%, bắt buộc tìm đường vòng)'
      : 'Cost = ∞ (Excluded from search, forces detour)'
  }`

  meta.append(idRow, statsRow, reasonRow, algRow)
  root.append(header, meta)
  return root
}

function roadClosureMarkerElement(markerData: ClosedEdgeMarkerData, lang: Language, onClick: () => void): HTMLElement {
  const root = document.createElement('div')
  root.className = 'road-closure-marker'
  root.title = `${lang === 'vi' ? 'Đoạn đường đóng' : 'Road closed'}: ${markerData.roadName}`

  const pulse = document.createElement('div')
  pulse.className = 'road-closure-pulse'

  const badge = document.createElement('div')
  badge.className = 'road-closure-badge'
  badge.innerHTML = `<span class="closure-icon">⛔</span><span class="closure-text">${lang === 'vi' ? 'ĐÓNG ĐƯỜNG' : 'CLOSED'}</span>`

  root.append(pulse, badge)
  root.addEventListener('click', (e) => {
    e.stopPropagation()
    onClick()
  })
  return root
}

function endpointPinElement(target: EndpointPickTarget, nodeLabel: string): HTMLElement {
  const marker = document.createElement('div')
  marker.className = `route-endpoint-marker route-endpoint-marker--${target.toLowerCase()}`
  marker.setAttribute('role', 'img')
  marker.setAttribute('aria-label', `${target}: ${nodeLabel}`)
  marker.title = `${target}: ${nodeLabel}`

  const svgNamespace = 'http://www.w3.org/2000/svg'
  const pin = document.createElementNS(svgNamespace, 'svg')
  pin.setAttribute('viewBox', '0 0 48 60')
  pin.setAttribute('aria-hidden', 'true')

  const shape = document.createElementNS(svgNamespace, 'path')
  shape.setAttribute(
    'd',
    'M24 59C20 53 4 40 4 23C4 12.5 12.5 4 24 4S44 12.5 44 23C44 40 28 53 24 59Z',
  )
  shape.setAttribute('class', 'route-endpoint-marker__shape')

  const center = document.createElementNS(svgNamespace, 'circle')
  center.setAttribute('class', 'route-endpoint-marker__center')
  center.setAttribute('cx', '24')
  center.setAttribute('cy', '23')
  center.setAttribute('r', '11')

  const label = document.createElementNS(svgNamespace, 'text')
  label.setAttribute('class', 'route-endpoint-marker__label')
  label.setAttribute('x', '24')
  label.setAttribute('y', '28')
  label.setAttribute('text-anchor', 'middle')
  label.textContent = target === 'START' ? 'S' : 'G'

  pin.append(shape, center, label)
  marker.append(pin)
  return marker
}

type CoordinateExtent = {
  west: number
  south: number
  east: number
  north: number
}

function graphExtent(graph: GraphPayload): CoordinateExtent | null {
  const coordinates = graph.nodes.flatMap<[number, number]>((node) => (
    node.latitude === null || node.longitude === null
      || !Number.isFinite(node.latitude) || !Number.isFinite(node.longitude)
      || node.latitude < -90 || node.latitude > 90
      || node.longitude < -180 || node.longitude > 180
      ? []
      : [[node.longitude, node.latitude]]
  ))
  if (!coordinates.length) return null
  return coordinates.reduce<CoordinateExtent>((extent, [longitude, latitude]) => ({
    west: Math.min(extent.west, longitude),
    south: Math.min(extent.south, latitude),
    east: Math.max(extent.east, longitude),
    north: Math.max(extent.north, latitude),
  }), {
    west: coordinates[0][0],
    south: coordinates[0][1],
    east: coordinates[0][0],
    north: coordinates[0][1],
  })
}

function graphContextBounds(graph: GraphPayload): maplibregl.LngLatBounds | null {
  const extent = graphExtent(graph)
  if (!extent) return null
  const longitudePadding = Math.max((extent.east - extent.west) * 0.25, 0.006)
  const latitudePadding = Math.max((extent.north - extent.south) * 0.25, 0.006)
  return new maplibregl.LngLatBounds(
    [extent.west - longitudePadding, extent.south - latitudePadding],
    [extent.east + longitudePadding, extent.north + latitudePadding],
  )
}

function boundaryContextBounds(boundary: ThuDucBoundary | null | undefined): maplibregl.LngLatBounds | null {
  if (!boundary?.features.length) return null
  const extent: CoordinateExtent = {
    west: Number.POSITIVE_INFINITY,
    south: Number.POSITIVE_INFINITY,
    east: Number.NEGATIVE_INFINITY,
    north: Number.NEGATIVE_INFINITY,
  }

  function visitCoordinates(value: unknown): void {
    if (!Array.isArray(value)) return
    if (value.length >= 2 && typeof value[0] === 'number' && typeof value[1] === 'number') {
      const [longitude, latitude] = value
      if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
        extent.west = Math.min(extent.west, longitude)
        extent.south = Math.min(extent.south, latitude)
        extent.east = Math.max(extent.east, longitude)
        extent.north = Math.max(extent.north, latitude)
      }
      return
    }
    value.forEach(visitCoordinates)
  }

  boundary.features.forEach((feature) => visitCoordinates(feature.geometry.coordinates))
  if (![extent.west, extent.south, extent.east, extent.north].every(Number.isFinite)) return null

  // B is a padded rectangle that fully contains the irregular Thu Duc polygon A.
  const longitudePadding = Math.max((extent.east - extent.west) * 0.03, 0.004)
  const latitudePadding = Math.max((extent.north - extent.south) * 0.03, 0.004)
  return new maplibregl.LngLatBounds(
    [extent.west - longitudePadding, extent.south - latitudePadding],
    [extent.east + longitudePadding, extent.north + latitudePadding],
  )
}



export function RouteMap({
  graph,
  boundary,
  boundaryWarning = '',
  pathEdgeIds = [],
  visiblePathEdgeCount = pathEdgeIds.length,
  pathNodeIds = [],
  frontierNodeIds = [],
  closedNodeIds = [],
  currentNodeId = null,
  startId,
  goalId,
  pickTarget,
  onNodePick,
  onPickTargetChange,
  activeAnimatedNodeId,
  activeAnimatedNodeLabel,
  tourStopMarkers = [],
  tourStopCount = 0,
  hideEndpoints = false,
  isTourMode = false,
  isSidebarCollapsed = false,
  lang = 'en',
}: RouteMapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const hoverPopupRef = useRef<maplibregl.Popup | null>(null)
  const clickPopupRef = useRef<maplibregl.Popup | null>(null)
  const pickTargetRef = useRef(pickTarget)
  const onNodePickRef = useRef(onNodePick)
  const onPickTargetChangeRef = useRef(onPickTargetChange)
  const graphRef = useRef(graph)
  const isTourModeRef = useRef(isTourMode)
  const langRef = useRef<Language>(lang)
  const fallbackAppliedRef = useRef(false)
  const styleReadyRef = useRef(false)
  const [styleRevision, setStyleRevision] = useState(0)
  const [basemapWarning, setBasemapWarning] = useState('')
  const [pickFeedback, setPickFeedback] = useState('')
  const [showMapLegendPopover, setShowMapLegendPopover] = useState(false)

  pickTargetRef.current = pickTarget
  onNodePickRef.current = onNodePick
  onPickTargetChangeRef.current = onPickTargetChange
  graphRef.current = graph
  isTourModeRef.current = isTourMode
  langRef.current = lang

  const edgeData = useMemo(() => buildEdgeFeatureCollection(graph), [graph])
  const nodeData = useMemo(() => buildNodeFeatureCollection(graph, {
    startId,
    goalId,
    pathNodeIds,
    frontierNodeIds,
    closedNodeIds,
    currentNodeId,
  }), [closedNodeIds, currentNodeId, frontierNodeIds, goalId, graph, pathNodeIds, startId])
  const routeData = useMemo(
    () => buildRouteFeatureCollection(graph, pathEdgeIds.slice(0, visiblePathEdgeCount)),
    [graph, pathEdgeIds, visiblePathEdgeCount],
  )
  const nodeDataRef = useRef(nodeData)
  nodeDataRef.current = nodeData

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASEMAP_STYLE_URL,
      center: DEFAULT_CENTER,
      zoom: 14,
      minZoom: MIN_CITY_ZOOM,
      renderWorldCopies: false,
      attributionControl: false,
    })
    mapRef.current = map
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right')
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 400 }), 'bottom-left')

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
        setPickFeedback('')
        onNodePickRef.current(target, properties.node_id)
        if (!(isTourModeRef.current && target === 'GOAL')) {
          onPickTargetChangeRef.current(null)
        }
      }
      clickPopupRef.current?.remove()
      clickPopupRef.current = new maplibregl.Popup({ closeButton: true, offset: 14 })
        .setLngLat(event.lngLat)
        .setDOMContent(popupContent(properties))
        .addTo(map)
    }
    const onMapClick = (event: MapMouseEvent) => {
      const target = pickTargetRef.current
      if (!target) return
      const directNodeHit = map.getLayer(LAYER_NODE_HITBOX)
        ? map.queryRenderedFeatures(event.point, { layers: [LAYER_NODE_HITBOX] }).length > 0
        : false
      if (directNodeHit) return

      const snap = findNearestGraphNode(
        graphRef.current,
        event.lngLat.lng,
        event.lngLat.lat,
        MAX_BASEMAP_SNAP_DISTANCE_M,
      )
      if (!snap) {
        setPickFeedback(`Không có node định tuyến trong ${MAX_BASEMAP_SNAP_DISTANCE_M} m.`)
        return
      }
      const feature = nodeDataRef.current.features.find(
        (item) => item.properties.node_id === snap.nodeId,
      )
      if (!feature) return

      setPickFeedback('')
      onNodePickRef.current(target, snap.nodeId)
      if (!(isTourModeRef.current && target === 'GOAL')) {
        onPickTargetChangeRef.current(null)
      }
      clickPopupRef.current?.remove()
      clickPopupRef.current = new maplibregl.Popup({ closeButton: true, offset: 14 })
        .setLngLat([snap.longitude, snap.latitude])
        .setDOMContent(popupContent(feature.properties, snap.distanceM))
        .addTo(map)
    }

    const onClosedEdgeMouseEnter = (event: MapLayerMouseEvent) => {
      map.getCanvas().style.cursor = 'pointer'
      const properties = edgeFeatureProps(event.features?.[0])
      if (!properties) return
      hoverPopupRef.current?.remove()
      hoverPopupRef.current = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        offset: 14,
      })
        .setLngLat(event.lngLat)
        .setDOMContent(closedEdgePopupContent(properties, langRef.current))
        .addTo(map)
    }

    const onClosedEdgeClick = (event: MapLayerMouseEvent) => {
      const properties = edgeFeatureProps(event.features?.[0])
      if (!properties) return
      clickPopupRef.current?.remove()
      clickPopupRef.current = new maplibregl.Popup({ closeButton: true, offset: 14 })
        .setLngLat(event.lngLat)
        .setDOMContent(closedEdgePopupContent(properties, langRef.current))
        .addTo(map)
    }

    map.on('style.load', onStyleLoad)
    map.on('error', onError)
    map.on('mouseenter', LAYER_NODE_HITBOX, onMouseEnter)
    map.on('mouseleave', LAYER_NODE_HITBOX, onMouseLeave)
    map.on('click', LAYER_NODE_HITBOX, onNodeClick)
    map.on('mouseenter', LAYER_CLOSED_EDGE_HITBOX, onClosedEdgeMouseEnter)
    map.on('mouseleave', LAYER_CLOSED_EDGE_HITBOX, onMouseLeave)
    map.on('click', LAYER_CLOSED_EDGE_HITBOX, onClosedEdgeClick)
    map.on('click', onMapClick)

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
      ; (map.getSource(SOURCE_EDGES) as GeoJSONSource | undefined)?.setData(edgeData)
      ; (map.getSource(SOURCE_NODES) as GeoJSONSource | undefined)?.setData(nodeData)
      ; (map.getSource(SOURCE_ROUTE) as GeoJSONSource | undefined)?.setData(routeData)
      ; (map.getSource(SOURCE_BOUNDARY) as GeoJSONSource | undefined)?.setData(
        boundary ?? EMPTY_FEATURE_COLLECTION,
      )
  }, [boundary, edgeData, nodeData, routeData, styleRevision])

  const cameraGraphKeyRef = useRef('')

  useEffect(() => {
    const map = mapRef.current
    if (!map || !styleReadyRef.current) return
    const bounds = boundaryContextBounds(boundary) ?? graphContextBounds(graph)
    if (!bounds) {
      map.setCenter(DEFAULT_CENTER)
      map.setZoom(14)
      return
    }

    // Rectangle B contains the irregular boundary A plus a small outside context ring.
    // Clamp navigation to B so the map remains a Thu Duc study-area crop.
    map.setMinZoom(MIN_CITY_ZOOM)
    map.setMaxBounds(bounds)
    const cameraKey = `${graph.graph_id}:${styleRevision}:${boundary?.source_id ?? 'graph-fallback'}`
    if (cameraGraphKeyRef.current === cameraKey) return
    cameraGraphKeyRef.current = cameraKey
    map.fitBounds(bounds, { padding: 52, maxZoom: 16, duration: 0 })
  }, [boundary, graph, styleRevision])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    let animationFrameId: number
    const startTime = performance.now()
    const durationMs = 450

    function smoothResizeStep(now: number) {
      mapRef.current?.resize?.()
      if (now - startTime < durationMs) {
        animationFrameId = requestAnimationFrame(smoothResizeStep)
      }
    }

    animationFrameId = requestAnimationFrame(smoothResizeStep)

    const recenterTimer = setTimeout(() => {
      const bounds = boundaryContextBounds(boundary) ?? graphContextBounds(graph)
      if (bounds && mapRef.current) {
        mapRef.current.fitBounds(bounds, { padding: 52, maxZoom: 16, duration: 300 })
      }
    }, 450)

    return () => {
      cancelAnimationFrame(animationFrameId)
      clearTimeout(recenterTimer)
    }
  }, [isSidebarCollapsed, boundary, graph])

  useEffect(() => {
    if (!containerRef.current || typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(() => {
      mapRef.current?.resize?.()
    })
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map || hideEndpoints) return
    const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]))

    const targets = isTourMode
      ? ([['START', startId]] as const)
      : ([['START', startId], ['GOAL', goalId]] as const)

    const markers = targets.flatMap<maplibregl.Marker>(([target, nodeId]) => {
      if (!nodeId) return []
      const node = nodeById.get(nodeId)
      if (!node || node.latitude === null || node.longitude === null
        || !Number.isFinite(node.latitude) || !Number.isFinite(node.longitude)) return []

      const labelText = isTourMode ? `START/GOAL · ${node.label || node.node_id}` : (node.label || node.node_id)
      const marker = new maplibregl.Marker({
        element: endpointPinElement(target, labelText),
        anchor: 'bottom',
      })
        .setLngLat([node.longitude, node.latitude])
        .addTo(map)
      return [marker]
    })

    return () => markers.forEach((marker) => marker.remove())
  }, [goalId, graph, startId, hideEndpoints, isTourMode])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !activeAnimatedNodeId) return
    const node = graph.nodes.find((item) => item.node_id === activeAnimatedNodeId)
    if (!node || node.latitude === null || node.longitude === null
      || !Number.isFinite(node.latitude) || !Number.isFinite(node.longitude)) return

    const el = document.createElement('div')
    el.className = 'animated-node-pin'
    el.innerHTML = `
      <div class="pin-tooltip">${activeAnimatedNodeLabel || node.label || node.node_id}</div>
      <div class="pin-pulse"></div>
    `

    const marker = new maplibregl.Marker({ element: el, anchor: 'bottom' })
      .setLngLat([node.longitude, node.latitude])
      .addTo(map)

    return () => {
      marker.remove()
    }
  }, [activeAnimatedNodeId, activeAnimatedNodeLabel, graph])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !tourStopMarkers || !tourStopMarkers.length) return

    const markers = tourStopMarkers.flatMap((item) => {
      // Khi đã hoàn thành đi đến điểm dừng, không vẽ marker màu vàng đậm nữa
      if (item.isVisited) return []
      if (!item.latitude || !item.longitude || !Number.isFinite(item.latitude) || !Number.isFinite(item.longitude)) return []

      const el = document.createElement('div')
      el.className = 'visited-stop-marker'
      const badge = document.createElement('div')
      badge.className = 'visited-stop-badge'
      badge.textContent = `#${item.stopIndex}`
      const name = document.createElement('div')
      name.className = 'visited-stop-name'
      name.textContent = item.name
      el.append(badge, name)

      const marker = new maplibregl.Marker({ element: el, anchor: 'bottom' })
        .setLngLat([item.longitude, item.latitude])
        .addTo(map)

      return [marker]
    })

    return () => {
      markers.forEach((marker) => marker.remove())
    }
  }, [tourStopMarkers])

  // Render Road Closure Barrier Markers (⛔) on map
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const closedMarkersData = buildClosedEdgeMarkers(graph)
    if (!closedMarkersData.length) return

    const markers = closedMarkersData.map((data) => {
      const el = roadClosureMarkerElement(data, lang, () => {
        clickPopupRef.current?.remove()
        clickPopupRef.current = new maplibregl.Popup({ closeButton: true, offset: 14 })
          .setLngLat(data.midpoint)
          .setDOMContent(
            closedEdgePopupContent(
              {
                edge_id: data.edgeId,
                from_node_id: data.fromNodeId,
                to_node_id: data.toNodeId,
                road_name: data.roadName,
                is_closed: true,
                route_index: -1,
                distance_m: data.distanceM,
                free_flow_time_min: data.freeFlowTimeMin,
              },
              lang,
            ),
          )
          .addTo(map)
      })

      const marker = new maplibregl.Marker({
        element: el,
        anchor: 'center',
      })
        .setLngLat(data.midpoint)
        .addTo(map)

      return marker
    })

    return () => {
      markers.forEach((m) => m.remove())
    }
  }, [graph, lang])






  useEffect(() => {
    setPickFeedback('')
    if (!pickTarget) return
    const cancel = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onPickTargetChange(null)
    }
    window.addEventListener('keydown', cancel)
    return () => window.removeEventListener('keydown', cancel)
  }, [onPickTargetChange, pickTarget])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    map.resize()
    if (isSidebarCollapsed) {
      const bounds = boundaryContextBounds(boundary) ?? graphContextBounds(graph)
      if (bounds) {
        map.fitBounds(bounds, { padding: 48, maxZoom: 12.0, duration: 450 })
      }
    }
  }, [boundary, graph, isSidebarCollapsed])

  function resetView() {
    const map = mapRef.current
    const bounds = boundaryContextBounds(boundary) ?? graphContextBounds(graph)
    if (map && bounds) {
      map.setMaxBounds(bounds)
      map.fitBounds(bounds, { padding: 52, maxZoom: isSidebarCollapsed ? 12.0 : 16.0, duration: 500 })
    }
  }

  return (
    <div className={`route-map-shell${pickTarget ? ' is-picking' : ''}`}>
      <div ref={containerRef} className="route-map" aria-label={t('map_aria', lang)} />
      {!hideEndpoints && (
        <div className="map-pick-toolbar" aria-label={t('pick_toolbar', lang)}>
          {isTourMode ? (
            <>
              <button
                type="button"
                className="pick-start"
                aria-pressed={pickTarget === 'START'}
                onClick={() => onPickTargetChange(pickTarget === 'START' ? null : 'START')}
              >
                {pickTarget === 'START' ? t('picking_tour_start', lang) : t('pick_tour_start', lang)}
              </button>
              <button
                type="button"
                className="pick-goal"
                aria-pressed={pickTarget === 'GOAL'}
                disabled={tourStopCount >= MAX_TOUR_STOPS}
                onClick={() => onPickTargetChange(pickTarget === 'GOAL' ? null : 'GOAL')}
              >
                {pickTarget === 'GOAL' ? t('picking_tour_goal', lang) : t('pick_tour_goal', lang)}
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                className="pick-start"
                aria-pressed={pickTarget === 'START'}
                onClick={() => onPickTargetChange(pickTarget === 'START' ? null : 'START')}
              >
                {t('pick_start', lang)}
              </button>
              <button
                type="button"
                className="pick-goal"
                aria-pressed={pickTarget === 'GOAL'}
                onClick={() => onPickTargetChange(pickTarget === 'GOAL' ? null : 'GOAL')}
              >
                {t('pick_goal', lang)}
              </button>
            </>
          )}
          {pickTarget && (
            <button type="button" className="pick-cancel" onClick={() => onPickTargetChange(null)}>
              {t('cancel', lang)}
            </button>
          )}
        </div>
      )}
      {pickTarget && (
        <div className="map-pick-hint">
          {pickFeedback || (isTourMode
            ? pickTarget === 'START'
              ? t('pick_hint_tour_start', lang)
              : t('pick_hint_tour_goal', lang, { count: tourStopCount, max: MAX_TOUR_STOPS })
            : t('pick_hint_generic', lang, { target: pickTarget }))}
        </div>
      )}
      <div className="map-controls-group">
        <button
          type="button"
          className="map-legend-toggle-btn"
          title={t('legend_title', lang)}
          aria-label={t('legend_title', lang)}
          aria-expanded={showMapLegendPopover}
          onClick={() => setShowMapLegendPopover((prev) => !prev)}
        >
          <span className="legend-icon" aria-hidden="true">📌</span>
          <span className="legend-label">{t('legend_title', lang)}</span>
          <span className="legend-chevron" aria-hidden="true">▾</span>
        </button>
        <button
          type="button"
          className="map-reset-button"
          title={t('reset_view', lang)}
          aria-label={t('reset_view', lang)}
          onClick={resetView}
        >
          <img src={recenterGraphIcon} alt="" aria-hidden="true" />
        </button>
      </div>
      {showMapLegendPopover && (
        <div className="map-legend-popover" role="dialog" aria-label={t('legend_title', lang)}>
          <div className="popover-header">
            <strong>📌 {t('legend_title', lang)}</strong>
            <button
              type="button"
              className="close-popover-btn"
              onClick={() => setShowMapLegendPopover(false)}
              aria-label="Close"
            >
              ✕
            </button>
          </div>
          <div className="popover-legend-items">
            <span className="legend-item legend-item--open"><i className="legend-line open" />{t('legend_normal_road', lang)}</span>
            <span className="legend-item legend-item--blocked"><i className="legend-line blocked" />⛔ {t('legend_blocked_road', lang)}</span>
            <span className="legend-item legend-item--node"><i className="legend-node" />{t('legend_node', lang)}</span>
            <span className="legend-item"><i className="legend-node legend-node--frontier" />{t('legend_frontier', lang)}</span>
            <span className="legend-item"><i className="legend-node legend-node--current" />{t('legend_current', lang)}</span>
            <span className="legend-item"><i className="legend-node legend-node--closed" />{t('legend_closed', lang)}</span>
            <span className="legend-item legend-item--path"><i className="legend-line path" />{t('legend_optimal_path', lang)}</span>
            <span className="legend-item legend-item--boundary"><i className="legend-line boundary" />{t('legend_boundary', lang)}</span>
          </div>
        </div>
      )}
      {(basemapWarning || boundaryWarning) && (
        <div className="basemap-warning" role="status">{basemapWarning || boundaryWarning}</div>
      )}
      <div className="map-note">
        <span className="map-note-dot" />
        <span className="map-note-status">{graph.data_status}</span>
        <span className="map-note-sep">·</span>
        <span className="map-note-stats">
          {graph.nodes.length.toLocaleString(lang)} nodes · {graph.edges.length.toLocaleString(lang)} edges
        </span>
      </div>
    </div>
  )
}
