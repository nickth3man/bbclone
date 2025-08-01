/**
Players page stub.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Frontend Scenarios:
    * Deep links mirror Basketball-Reference and drive API queries
    * CSV export streams current table view with API field headers
Acceptance notes (to be implemented in Red/Green):
  - URL /players triggers API GET /players?season=YYYY&team=ABC
  - Pagination controls visible; metadata preserved through navigation
  - CSV export respects current filters/sorting; leading zeros in jersey retained
*/

import React from 'react'

export default function PlayersPage() {
  const handleExportCsv = () => {
    // TODO: Wire to backend CSV export endpoint or client-side stream
    throw new Error('NotImplementedError: PlayersPage Export CSV')
  }

  return (
    <section>
      <h1>Players (Stub)</h1>

      <div style={{ marginBottom: 12 }}>
        <label>
          Season:
          <input type="text" placeholder="1996" style={{ marginLeft: 8 }} />
        </label>
        <label style={{ marginLeft: 16 }}>
          Team:
          <input type="text" placeholder="BOS" style={{ marginLeft: 8 }} />
        </label>
        <button style={{ marginLeft: 16 }} onClick={handleExportCsv}>Export CSV</button>
      </div>

      <table border={1} cellPadding={6} cellSpacing={0} width="100%">
        <thead>
          <tr>
            <th>player_id</th>
            <th>player_name</th>
            <th>season</th>
            <th>team</th>
            <th>jersey (TEXT)</th>
            <th>metric DECIMAL(9,3)</th>
          </tr>
        </thead>
        <tbody>
          {/* TODO: Render rows from API. Ensure pagination and performance p90 < 1s. */}
        </tbody>
      </table>

      <div style={{ marginTop: 12 }}>
        {/* TODO: Pagination controls (count, next, previous) */}
        <button disabled>Previous</button>
        <span style={{ margin: '0 8px' }}>Page 1 / N</span>
        <button disabled>Next</button>
      </div>
    </section>
  )
}