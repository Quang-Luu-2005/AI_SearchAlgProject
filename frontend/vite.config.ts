import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    // Let Vite's worker pipeline handle MapLibre's separate ESM worker.
    exclude: ['maplibre-gl'],
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
    // Polling is more reliable for HMR on Windows/OneDrive/network-mounted folders.
    // It only affects the development server; production builds are unchanged.
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
})
