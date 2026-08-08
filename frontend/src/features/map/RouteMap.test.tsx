import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { GraphPayload } from '../../lib/graph'
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
    canvas = document.createElement('canvas')

    constructor() {
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
      expect(map.sources.get('floodroute-nodes')?.setData).toHaveBeenCalled()
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
})

