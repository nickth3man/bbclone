/**
Traceability:
- See docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Section 4) Frontend: Deep links mirror Basketball-Reference and drive API queries.
This component provides a layout shell and an outlet for child routes.
*/

import React from 'react'
import { Outlet, Link } from 'react-router-dom'

export default function App() {
  return (
    <div style={{ fontFamily: 'sans-serif', padding: 16 }}>
      <header style={{ marginBottom: 16 }}>
        <nav style={{ display: 'flex', gap: 12 }}>
          <Link to="/players">Players</Link>
          <Link to="/games/00000001/pbp">Sample Game PBP</Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}