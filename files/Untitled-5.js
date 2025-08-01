/**
 * Vite configuration with proxy setup for backend API calls.
 * 
 * Addresses CORS issues during development by proxying API calls
 * to the Django backend running on port 8000.
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Path aliases for cleaner imports
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  
  // Development server configuration
  server: {
    port: 5173,
    host: true, // Listen on all addresses
    
    // Proxy API calls to Django backend
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Remove /api prefix when forwarding to backend
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  
  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: true,
    
    // Performance optimizations
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
        },
      },
    },
  },
  
  // Environment variables prefix
  envPrefix: 'VITE_',
})