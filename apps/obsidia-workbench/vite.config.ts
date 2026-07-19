import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/brody': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/status': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/os-trad': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/ir': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/os-reverse': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },      // Proxy /api/* â†’ ObsidiaShell to avoid CORS issues in dev (optional)
      '/api/obsidia': {
        target: 'http://127.0.0.1:8011',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/obsidia/, ''),
      },
      '/api/engine': {
        target: 'http://127.0.0.1:8012',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/engine/, ''),
      },
      '/api/runtime-wiring': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
