import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { setWorkerUrl } from 'maplibre-gl'
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import 'maplibre-gl/dist/maplibre-gl.css'
import './styles.css'
import { App } from './App'

// MapLibre v6 ships as ESM and its worker must go through Vite's worker pipeline.
// This prevents Vite from looking for a stale optimized worker in `.vite/deps`.
setWorkerUrl(maplibreWorkerUrl)

createRoot(document.getElementById('app')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
