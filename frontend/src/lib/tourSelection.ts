export const MAX_TOUR_STOPS = 10

export type TourStopSelectionStatus =
  | 'ADDED'
  | 'DEPOT_SELECTED'
  | 'DUPLICATE'
  | 'LIMIT_REACHED'

export type TourStopSelectionResult = {
  stops: string[]
  status: TourStopSelectionStatus
}

export function addTourStop(
  currentStops: readonly string[],
  depotId: string,
  nodeId: string,
): TourStopSelectionResult {
  if (nodeId === depotId) {
    return { stops: [...currentStops], status: 'DEPOT_SELECTED' }
  }
  if (currentStops.includes(nodeId)) {
    return { stops: [...currentStops], status: 'DUPLICATE' }
  }
  if (currentStops.length >= MAX_TOUR_STOPS) {
    return { stops: [...currentStops], status: 'LIMIT_REACHED' }
  }
  return { stops: [...currentStops, nodeId], status: 'ADDED' }
}
