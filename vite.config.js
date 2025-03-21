import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5002', // Backend server
        changeOrigin: true, // Ensure the request appears to come from the frontend server
      },
    },
  },
})
