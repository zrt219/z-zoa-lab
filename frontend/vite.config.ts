import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/calculate': 'http://127.0.0.1:8000',
      '/catalogs': 'http://127.0.0.1:8000',
      '/experiments': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/ledger': 'http://127.0.0.1:8000',
      '/reconstruction': 'http://127.0.0.1:8000',
      '/validation': 'http://127.0.0.1:8000',
      '/reproducibility': 'http://127.0.0.1:8000',
    }
  }
})
