
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['localhost', '127.0.0.1', '0.0.0.0', 'ec2-107-20-211-209.compute-1.amazonaws.com'],
    port: 5173,
    host: true
  }
})
