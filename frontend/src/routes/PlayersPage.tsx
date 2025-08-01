/**
 * Players page stub.
 *
 * Traceability:
 * - docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
 *   Frontend Scenarios:
 *     * Deep links mirror Basketball-Reference and drive API queries
 *     * CSV export streams current table view with API field headers
 * Acceptance notes (to be implemented in Red/Green):
 *   - URL /players triggers API GET /players?season=YYYY&team=ABC
 *   - Pagination controls visible; metadata preserved through navigation
 *   - CSV export respects current filters/sorting; leading zeros in jersey retained
 */

import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom' // type: ignore

// Define a type for player data matching the backend serializer
interface Player {
  player_id: number
  name: string
  season: string
  team: string
  jersey: string // Assuming jersey might be text, not purely numeric
  games_played: number
  minutes: number
  points: number
  rebounds: number
  assists: number
  steals: number
  blocks: number
  fg_pct: number
  ft_pct: number
  three_pt_pct: number
}

// Define a type for API response, including pagination metadata
interface PlayersApiResponse {
  count: number
  next: string | null
  previous: string | null
  results: Player[]
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/'

export default function PlayersPage() {
  const [players, setPlayers] = useState<Player[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()

  const [seasonFilter, setSeasonFilter] = useState<string>(searchParams.get('season') || '')
  const [teamFilter, setTeamFilter] = useState<string>(searchParams.get('team') || '')
  const [currentPage, setCurrentPage] = useState<number>(
    parseInt(searchParams.get('page') || '1', 10)
  )
  const [pageSize, setPageSize] = useState<number>( // Default to backend page size, or common default
    parseInt(searchParams.get('page_size') || '50', 10)
  )
  const [totalItems, setTotalItems] = useState<number>(0)


  const totalPages = Math.ceil(totalItems / pageSize)

  // Effect for fetching players data
  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true)
      setError(null)
      try {
        const params = new URLSearchParams()
        if (seasonFilter) params.append('season', seasonFilter)
        if (teamFilter) params.append('team', teamFilter)
        params.append('page', currentPage.toString())
        params.append('page_size', pageSize.toString())

        const response = await fetch(`${API_BASE_URL}players?${params.toString()}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data: PlayersApiResponse = await response.json()
        setPlayers(data.results)
        setTotalItems(data.count)
        // Update URL to reflect current state
        setSearchParams(params)
      } catch (e: any) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }

    fetchPlayers()
  }, [seasonFilter, teamFilter, currentPage, pageSize, setSearchParams]) // Dependencies

  const handleSeasonChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSeasonFilter(e.target.value)
    setCurrentPage(1) // Reset to first page on filter change
  }

  const handleTeamChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTeamFilter(e.target.value)
    setCurrentPage(1) // Reset to first page on filter change
  }

  const handlePreviousPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1))
  }

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1))
  }

  const handleExportCsv = () => {
    // TODO: Implement CSV export with current filters and pagination parameters
    const params = new URLSearchParams()
    if (seasonFilter) params.append('season', seasonFilter)
    if (teamFilter) params.append('team', teamFilter)
    params.append('page', currentPage.toString())
    params.append('page_size', pageSize.toString())
    // Direct link to the backend endpoint for CSV, possibly with a 'format=csv' param
    window.open(`${API_BASE_URL}players.csv?${params.toString()}`, '_blank')
  }

  return (
    <section>
      <h1>Players</h1>

      <div style={{ marginBottom: 12 }}>
        <label>
          Season:
          <input
            type="text"
            placeholder="1996"
            style={{ marginLeft: 8 }}
            value={seasonFilter}
            onChange={handleSeasonChange}
          />
        </label>
        <label style={{ marginLeft: 16 }}>
          Team:
          <input
            type="text"
            placeholder="BOS"
            style={{ marginLeft: 8 }}
            value={teamFilter}
            onChange={handleTeamChange}
          />
        </label>
        <button style={{ marginLeft: 16 }} onClick={handleExportCsv}>Export CSV</button>
      </div>

      {loading && <p>Loading players...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {!loading && !error && players.length === 0 && <p>No players found for the selected filters.</p>}

      {!loading && !error && players.length > 0 && (
        <table border={1} cellPadding={6} cellSpacing={0} width="100%">
          <thead>
            <tr>
              <th>player_id</th>
              <th>player_name</th>
              <th>season</th>
              <th>team</th>
              <th>jersey</th>
              <th>games_played</th>
              <th>points</th>
              <th>rebounds</th>
              <th>assists</th>
              <th>steals</th>
              <th>blocks</th>
              <th>FG%</th>
              <th>FT%</th>
              <th>3P%</th>
            </tr>
          </thead>
          <tbody>
            {players.map(player => (
              <tr key={player.player_id + player.season + player.team}>
                <td>{player.player_id}</td>
                <td>{player.name}</td>
                <td>{player.season}</td>
                <td>{player.team}</td>
                <td>{player.jersey || 'N/A'}</td>
                <td>{player.games_played}</td>
                <td>{player.points}</td>
                <td>{player.rebounds}</td>
                <td>{player.assists}</td>
                <td>{player.steals}</td>
                <td>{player.blocks}</td>
                <td>{player.fg_pct?.toFixed(3) || 'N/A'}</td>
                <td>{player.ft_pct?.toFixed(3) || 'N/A'}</td>
                <td>{player.three_pt_pct?.toFixed(3) || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ marginTop: 12 }}>
        <button onClick={handlePreviousPage} disabled={currentPage === 1}>
          Previous
        </button>
        <span style={{ margin: '0 8px' }}>Page {currentPage} / {totalPages || 1}</span>
        <button onClick={handleNextPage} disabled={currentPage === totalPages || totalPages === 0}>
          Next
        </button>
      </div>
    </section>
  )
}