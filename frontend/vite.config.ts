import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // In Electron dev mode, backend runs on 8765; in web dev mode on 8000
        target: process.env.VITE_BACKEND_PORT
          ? `http://127.0.0.1:${process.env.VITE_BACKEND_PORT}`
          : 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
