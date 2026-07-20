export const PROJECT_NAME = 'FloodRoute HCMC'
export const API_PREFIX = '/api/v1'

export const COST_PRESETS = {
  BALANCED: {
    distance: 0.25,
    freeflowTime: 0.3,
    congestion: 0.2,
    floodRisk: 0.25,
  },
  RAIN_SAFE: {
    distance: 0.1,
    freeflowTime: 0.25,
    congestion: 0.15,
    floodRisk: 0.5,
  },
} as const

