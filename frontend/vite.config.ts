import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Electron desktop dev uses 8765; standalone backend debugging can still use 8000.
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
