/**
Game Play-by-Play page stub.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Frontend Scenarios:
    * Deep links: /games/:gameId/pbp triggers API GET /games/<game_id>/pbp
    * Performance p90 < 1s, chronological ordering, normalized IDs
Acceptance notes (to be implemented in Red/Green):
  - Render chronological events with required fields
  - Handle large OT games under performance target
  - 404/error handling for missing game_id
*/

import React from 'react'
import { useParams } from 'react-router-dom'

export default function GamePbpPage() {
  const { gameId } = useParams()

  return (
    <section>
      <h1>Game Play-by-Play (Stub)</h1>
      <p>Game ID: {gameId}</p>

      <div>{/* TODO: Controls like period filter or search */}</div>

      <ol>
        {/* TODO: Render chronological events: ensure ordering by period and clock */}
        <li>Event row placeholder</li>
      </ol>

      <p style={{ marginTop: 12 }}>
        {/* TODO: Performance: ensure fetch and render meet p90 < 1s */}
        This is a non-functional stub to anchor tests.
      </p>
    </section>
  )
}