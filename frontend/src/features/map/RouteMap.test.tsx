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

  class FakeMap {
    static instances: FakeMap[] = []
    handlers = new Map<string, Handler>()
    sources = new Map<string, FakeSource>()
    layers = new Set<string>()
    addControl = vi.fn()
    remove = vi.fn()
    fitBounds = vi.fn()
    flyTo = vi.fn()
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

    addLayer(layer: { id: string }) {
      this.layers.add(layer.id)
    }

    getLayer(id: string) {
      return this.layers.has(id) ? { id } : undefined
    }

    getCanvas() {
      return this.canvas
    }
  }

  return { FakeBounds, FakeMap, FakePopup }
})

vi.mock('maplibre-gl', () => ({
  Map: maplibreMock.FakeMap,
  Popup: maplibreMock.FakePopup,
  LngLatBounds: maplibreMock.FakeBounds,
  NavigationControl: class {},
  ScaleControl: class {},
  AttributionControl: class {},
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
      expect(map.layers).toContain('floodroute-thu-duc-boundary-line')
      expect(map.sources.get('floodroute-nodes')?.setData).toHaveBeenCalled()
      expect(map.sources.get('floodroute-thu-duc-boundary')?.setData).toHaveBeenCalledWith(boundary)
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
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Chọn START' }))
    fireEvent.click(screen.getByRole('button', { name: 'Chọn GOAL' }))
    expect(onPickTargetChange.mock.calls).toEqual([['START'], ['GOAL']])
  })

  it('clamps navigation to the city crop and focuses a single endpoint', async () => {
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
      expect(map.flyTo).toHaveBeenCalledWith(expect.objectContaining({
        center: [106.75, 10.85],
        zoom: 16.5,
      }))
    })
  })

  it('flies to the endpoint that was just changed instead of centering both endpoints', async () => {
    const view = render(
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
    await waitFor(() => expect(map.flyTo).toHaveBeenCalled())
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
      expect(map.flyTo).toHaveBeenCalledWith(expect.objectContaining({
        center: [106.751, 10.851],
        zoom: 16.5,
      }))
    })
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
