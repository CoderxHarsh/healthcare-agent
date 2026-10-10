import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // The backend's CORS allow-list and its OAuth callback redirect are both
    // hardcoded to http://localhost:8501, so the dev server must use that port.
    port: 8501,
    strictPort: true,
  },
  preview: {
    port: 8501,
    strictPort: true,
  },
})
