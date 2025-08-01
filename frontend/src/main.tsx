/**
Traceability:
- See docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Section 4) Frontend (React + Vite): Deep links and CSV export
This is a minimal React + Vite + TS entry with routing stubs. No business logic.
*/

import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'
import PlayersPage from './routes/PlayersPage'
import GamePbpPage from './routes/GamePbpPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { path: '/players', element: <PlayersPage /> },
      { path: '/games/:gameId/pbp', element: <GamePbpPage /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)