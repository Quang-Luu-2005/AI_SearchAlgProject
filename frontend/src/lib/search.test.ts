import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchLocations, runComparison, runSearch } from './search'

afterEach(() => {
  vi.unstubAllGlobals()
})

function mockJson(payload: unknown) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(payload),
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('BE-03 frontend client', () => {
  it('loads locations for the selected graph', async () => {
    const fetchMock = mockJson({ graph_id: 'toy_graph_v0.1', locations: [] })

    await fetchLocations('toy_graph_v0.1')

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/locations?graph_id=toy_graph_v0.1',
      { signal: undefined },
    )
  })

  it('posts the selected algorithm to search', async () => {
    const fetchMock = mockJson({ path: ['N01', 'N06'] })
    const input = {
      graph_id: 'toy_graph_v0.1',
      start: 'N01',
      goal: 'N06',
      scenario: 'HEAVY_RAIN_SAFE',
      algorithm: 'A_STAR' as const,
    }

    await runSearch(input)

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/search',
      expect.objectContaining({ method: 'POST', body: JSON.stringify(input) }),
    )
  })

  it('compares UCS and A* on the same input', async () => {
    const fetchMock = mockJson({ results: [] })
    const input = {
      graph_id: 'toy_graph_v0.1',
      start: 'N01',
      goal: 'N06',
      scenario: 'OFFPEAK_BALANCED',
    }

    await runComparison(input)

    const request = fetchMock.mock.calls[0][1] as RequestInit
    expect(JSON.parse(request.body as string)).toEqual({
      ...input,
      algorithms: ['UCS', 'A_STAR'],
    })
  })
})
