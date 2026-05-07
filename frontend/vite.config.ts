import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/ask': 'http://localhost:8000',
      '/ask_voice': 'http://localhost:8000',
      '/transcribe': 'http://localhost:8000',
      '/voice_to_voice': 'http://localhost:8000',
      '/retrieve': 'http://localhost:8000',
    }
  }
})
