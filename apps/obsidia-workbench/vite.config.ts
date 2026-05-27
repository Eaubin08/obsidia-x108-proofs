import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy /api/* → ObsidiaShell to avoid CORS issues in dev (optional)
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
    },
  },
})
