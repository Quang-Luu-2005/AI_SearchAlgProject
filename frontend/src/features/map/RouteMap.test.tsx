import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { GraphPayload, ThuDucBoundary } from '../../lib/graph'
import { RouteMap } from './RouteMap'

const maplibreMock = vi.hoisted(() => {
  type Handler = (event: Record<string, unknown>) => void

  class FakeSource {
    setData = vi.fn()
  }

  class FakeBounds {
    extend = vi.fn(() => this)
  }

  class FakePopup {
    remove = vi.fn(() => this)
    setLngLat = vi.fn(() => this)
    setDOMContent = vi.fn(() => this)
    addTo = vi.fn(() => this)
  }

  class FakeMarker {
    static instances: FakeMarker[] = []
    element: HTMLElement
    options: Record<string, unknown>
    setLngLat = vi.fn(() => this)
    addTo = vi.fn(() => this)
    remove = vi.fn(() => this)

    constructor(options: Record<string, unknown>) {
      this.options = options
      this.element = options.element as HTMLElement
      FakeMarker.instances.push(this)
    }
  }

  class FakeMap {
    static instances: FakeMap[] = []
    handlers = new Map<string, Handler>()
    sources = new Map<string, FakeSource>()
    layers = new Set<string>()
    layerDefinitions = new Map<string, Record<string, unknown>>()
    addControl = vi.fn()
    remove = vi.fn()
    resize = vi.fn()
    fitBounds = vi.fn()
    flyTo = vi.fn()
    easeTo = vi.fn()
    setLight = vi.fn()
    getStyle = vi.fn(() => ({ layers: [] }))
    setStyle = vi.fn()
    getZoom = vi.fn(() => 14)
    setCenter = vi.fn()
    setZoom = vi.fn()
    setMinZoom = vi.fn()
    setMaxBounds = vi.fn()
    stop = vi.fn()
    queryRenderedFeatures = vi.fn(() => [])
    canvas = document.createElement('canvas')
    options: Record<string, unknown>

    constructor(options: Record<string, unknown>) {
      this.options = options
      FakeMap.instances.push(this)
    }

    on(event: string, layerOrHandler: string | Handler, possibleHandler?: Handler) {
      const layer = typeof layerOrHandler === 'string' ? layerOrHandler : ''
      const handler = typeof layerOrHandler === 'function' ? layerOrHandler : possibleHandler!
      this.handlers.set(`${event}:${layer}`, handler)
      return this
    }

    emit(event: string, layer = '', payload: Record<string, unknown> = {}) {
      this.handlers.get(`${event}:${layer}`)?.(payload)
    }

    addSource(id: string) {
      this.sources.set(id, new FakeSource())
    }

    getSource(id: string) {
      return this.sources.get(id)
    }

    addLayer(layer: { id: string } & Record<string, unknown>) {
      this.layers.add(layer.id)
      this.layerDefinitions.set(layer.id, layer)
    }

    getLayer(id: string) {
      return this.layers.has(id) ? { id } : undefined
    }

    getCanvas() {
      return this.canvas
    }
  }

  return { FakeBounds, FakeMap, FakeMarker, FakePopup }
})

vi.mock('maplibre-gl', () => ({
  Map: maplibreMock.FakeMap,
  Marker: maplibreMock.FakeMarker,
  Popup: maplibreMock.FakePopup,
  LngLatBounds: maplibreMock.FakeBounds,
  NavigationControl: class { },
  ScaleControl: class { },
  AttributionControl: class { },
}))

const graph: GraphPayload = {
  graph_id: 'map-test',
  directed: true,
  data_status: 'SIMULATED',
  active_scenario_id: 'DEFAULT',
  metadata: {},
  scenarios: [{ scenario_id: 'DEFAULT', closed_edge_ids: [] }],
  nodes: [
    {
      node_id: 'N1',
      latitude: 10.85,
      longitude: 106.75,
      label: 'Node 1',
      attributes: { node_type: 'POI', data_status: 'SIMULATED' },
    },
    {
      node_id: 'N2',
      latitude: 10.851,
      longitude: 106.751,
      label: 'Node 2',
      attributes: { node_type: 'POI', data_status: 'SIMULATED' },
    },
  ],
  edges: [{
    edge_id: 'E1',
    from_node_id: 'N1',
    to_node_id: 'N2',
    distance_m: 100,
    free_flow_time_min: 1,
    is_closed: false,
    attributes: { road_name: 'Test Road' },
  }],
  active_edge_count: 1,
}

const boundary: ThuDucBoundary = {
  type: 'FeatureCollection',
  snapshot_date: '2026-08-09',
  source_url: 'https://www.openstreetmap.org/relation/19407794',
  source_id: 'OSM-THU-DUC-BOUNDARY-2026-08-09',
  license: 'ODbL-1.0',
  attribution: '© OpenStreetMap contributors',
  scope_note: 'Historic former Thu Duc City boundary.',
  features: [{
    type: 'Feature',
    properties: { osm_id: 19407794, boundary_status: 'HISTORIC_OSM_RELATION' },
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [106.69, 10.74],
        [106.89, 10.74],
        [106.89, 10.90],
        [106.69, 10.90],
        [106.69, 10.74],
      ]],
    },
  }],
}

describe('MapLibre RouteMap', () => {
  afterEach(() => {
    maplibreMock.FakeMap.instances.length = 0
    maplibreMock.FakeMarker.instances.length = 0
  })

  it('installs graph layers, updates sources and dispatches an active node pick', async () => {
    const onNodePick = vi.fn()
    const onPickTargetChange = vi.fn()
    const view = render(
      <RouteMap
        graph={graph}
        boundary={boundary}
        startId="N1"
        goalId="N2"
        pickTarget="START"
        onNodePick={onNodePick}
        onPickTargetChange={onPickTargetChange}
      />,
    )
    const map = maplibreMock.FakeMap.instances[0]
    map.emit('style.load')

    await waitFor(() => {
      expect(map.layers).toContain('floodroute-node-hitbox')
      expect(map.layers).toContain('floodroute-selectable-node')
      expect(map.layers).toContain('floodroute-thu-duc-boundary-line')
      expect(map.sources.get('floodroute-nodes')?.setData).toHaveBeenCalled()
      expect(map.sources.get('floodroute-thu-duc-boundary')?.setData).toHaveBeenCalledWith(boundary)
      expect(map.layerDefinitions.get('floodroute-selectable-node')?.filter).toEqual([
        '==', ['get', 'selectable'], true,
      ])
    })

    map.emit('click', 'floodroute-node-hitbox', {
      lngLat: { lng: 106.75, lat: 10.85 },
      features: [{
        properties: {
          node_id: 'N1',
          display_name: 'Node 1',
          node_type: 'POI',
          data_status: 'SIMULATED',
          label_status: 'SOURCE_BACKED',
          visual_state: 'start',
        },
      }],
    })

    expect(onNodePick).toHaveBeenCalledWith('START', 'N1')
    expect(onPickTargetChange).toHaveBeenCalledWith(null)
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onPickTargetChange).toHaveBeenCalledTimes(2)

    view.unmount()
    expect(map.remove).toHaveBeenCalled()
  })

  it('toggles explicit START and GOAL pick modes', () => {
    const onPickTargetChange = vi.fn()
    render(
      <RouteMap
        graph={graph}
        pickTarget={null}
        onNodePick={vi.fn()}
        onPickTargetChange={onPickTargetChange}
        lang="vi"
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Chọn START' }))
    fireEvent.click(screen.getByRole('button', { name: 'Chọn GOAL' }))
    expect(onPickTargetChange.mock.calls).toEqual([['START'], ['GOAL']])
  })

  it('exposes separate START depot and GOAL stop pick modes for tours', () => {
    const onPickTargetChange = vi.fn()
    render(
      <RouteMap
        graph={graph}
        pickTarget={null}
        onNodePick={vi.fn()}
        onPickTargetChange={onPickTargetChange}
        isTourMode
        tourStopCount={2}
        lang="vi"
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Chọn START (Depot)' }))
    fireEvent.click(screen.getByRole('button', { name: 'Thêm GOAL (Điểm dừng)' }))
    expect(onPickTargetChange.mock.calls).toEqual([['START'], ['GOAL']])
  })

  it('keeps tour GOAL mode active while adding consecutive stops', async () => {
    const onNodePick = vi.fn()
    const onPickTargetChange = vi.fn()
    render(
      <RouteMap
        graph={graph}
        pickTarget="GOAL"
        onNodePick={onNodePick}
        onPickTargetChange={onPickTargetChange}
        isTourMode
        tourStopCount={1}
      />,
    )
    const map = maplibreMock.FakeMap.instances[0]
    map.emit('style.load')
    await waitFor(() => expect(map.layers).toContain('floodroute-node-hitbox'))

    map.emit('click', 'floodroute-node-hitbox', {
      lngLat: { lng: 106.75, lat: 10.85 },
      features: [{
        properties: {
          node_id: 'N2',
          display_name: 'Node 2',
          node_type: 'POI',
          data_status: 'SIMULATED',
          label_status: 'SOURCE_BACKED',
          visual_state: 'normal',
        },
      }],
    })

    expect(onNodePick).toHaveBeenCalledWith('GOAL', 'N2')
    expect(onPickTargetChange).not.toHaveBeenCalled()
  })

  it('renders selected tour stops before execution as safe text markers', async () => {
    render(
      <RouteMap
        graph={graph}
        pickTarget={null}
        onNodePick={vi.fn()}
        onPickTargetChange={vi.fn()}
        isTourMode
        tourStopCount={1}
        tourStopMarkers={[{
          nodeId: 'N2',
          name: '<b>Stop 2</b>',
          stopIndex: 1,
          latitude: 10.86,
          longitude: 106.76,
          isVisited: false,
        }]}
      />,
    )

    await waitFor(() => expect(maplibreMock.FakeMarker.instances).toHaveLength(1))
    const marker = maplibreMock.FakeMarker.instances[0].element
    expect(marker).toHaveTextContent('#1')
    expect(marker).toHaveTextContent('<b>Stop 2</b>')
    expect(marker.querySelector('b')).toBeNull()
  })

  it('clamps navigation to the city crop without focusing a selected endpoint', async () => {
    render(
      <RouteMap
        graph={graph}
        startId="N1"
        pickTarget={null}
        onNodePick={vi.fn()}
        onPickTargetChange={vi.fn()}
      />,
    )
    const map = maplibreMock.FakeMap.instances[0]
    map.emit('style.load')

    await waitFor(() => {
      expect(map.setMinZoom).toHaveBeenCalledWith(10.5)
      expect(map.setMaxBounds).toHaveBeenCalled()
      expect(map.options).toMatchObject({ minZoom: 10.5, renderWorldCopies: false })
      expect(map.flyTo).not.toHaveBeenCalled()
    })
    expect(maplibreMock.FakeMarker.instances).toHaveLength(1)
    expect(maplibreMock.FakeMarker.instances[0].options).toMatchObject({ anchor: 'bottom' })
    expect(maplibreMock.FakeMarker.instances[0].setLngLat).toHaveBeenCalledWith([106.75, 10.85])
    expect(maplibreMock.FakeMarker.instances[0].element).toHaveClass(
      'route-endpoint-marker--start',
    )
    expect(maplibreMock.FakeMarker.instances[0].element.querySelector('svg')).not.toBeNull()
  })

  it('keeps the camera unchanged and highlights both endpoints when selection changes', async () => {
    const view = render(
      <RouteMap
        graph={graph}
        pickTarget={null}
        onNodePick={vi.fn()}
        onPickTargetChange={vi.fn()}
      />,
    )
    const map = maplibreMock.FakeMap.instances[0]
    map.emit('style.load')
    await waitFor(() => expect(map.fitBounds).toHaveBeenCalled())
    map.fitBounds.mockClear()
    map.flyTo.mockClear()

    view.rerender(
      <RouteMap
        graph={graph}
        startId="N1"
        goalId="N2"
        pickTarget={null}
        onNodePick={vi.fn()}
        onPickTargetChange={vi.fn()}
      />,
    )

    await waitFor(() => {
      const latestNodeData = map.sources.get('floodroute-nodes')?.setData.mock.calls.at(-1)?.[0]
      expect(latestNodeData.features.map((feature: { properties: { visual_state: string } }) => (
        feature.properties.visual_state
      ))).toEqual(['start', 'goal'])
      expect(maplibreMock.FakeMarker.instances).toHaveLength(2)
    })
    expect(maplibreMock.FakeMarker.instances.map((marker) => marker.element.textContent))
      .toEqual(['S', 'G'])
    expect(maplibreMock.FakeMarker.instances.map((marker) => marker.element.className))
      .toEqual([
        'route-endpoint-marker route-endpoint-marker--start',
        'route-endpoint-marker route-endpoint-marker--goal',
      ])
    expect(map.flyTo).not.toHaveBeenCalled()
    expect(map.fitBounds).not.toHaveBeenCalled()
  })

  it('snaps a basemap click to the nearest graph node while picking', async () => {
    const onNodePick = vi.fn()
    const onPickTargetChange = vi.fn()
    render(
      <RouteMap
        graph={graph}
        pickTarget="GOAL"
        onNodePick={onNodePick}
        onPickTargetChange={onPickTargetChange}
      />,
    )
    const map = maplibreMock.FakeMap.instances[0]
    map.emit('style.load')

    await waitFor(() => expect(map.layers).toContain('floodroute-node-hitbox'))
    map.emit('click', '', {
      point: { x: 100, y: 100 },
      lngLat: { lng: 106.75002, lat: 10.85002 },
    })

    expect(onNodePick).toHaveBeenCalledWith('GOAL', 'N1')
    expect(onPickTargetChange).toHaveBeenCalledWith(null)
  })
})
