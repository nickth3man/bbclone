/**
Vite configuration scaffold for React + TS app.

Traceability:
- See docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md section 4) Frontend

Notes:
- This file enables JSX/TSX with React plugin. No business logic is included.
*/

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
})