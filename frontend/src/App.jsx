import { useState, useEffect } from 'react'
import './App.css'
import Navbar from './Navbar'

function App() {
  const [users, setUsers] = useState([])
  const [teams, setTeams] = useState(null)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState('auto') // 'auto' | 'manual'
  const [manualA, setManualA] = useState([])
  const [manualB, setManualB] = useState([])

  useEffect(() => {
    const fetchUsers = async () => {
      const response = await fetch("/api/users")
      const data = await response.json()
      setUsers(data)
    }
    fetchUsers()
  }, [])

  // Reset results when switching modes
  const switchMode = (m) => {
    setMode(m)
    setTeams(null)
    setManualA([])
    setManualB([])
  }

  // --- AUTO MODE ---
  const makeTeams = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    const players = []
    for (let i = 0; i < 10; i++) {
      const val = form.get(`slot${i}`)
      if (val) players.push(val)
    }
    if (players.length < 2) {
      alert('Select at least 2 players')
      return
    }
    setLoading(true)
    const response = await fetch("/api/maketeams", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ players })
    })
    const data = await response.json()
    setTeams(data)
    setLoading(false)
  }

  // --- MANUAL MODE ---
  const addToTeam = (team, username) => {
    if (!username) return
    if (team === 'A') setManualA(prev => [...prev, username])
    else setManualB(prev => [...prev, username])
  }

  const removeFromTeam = (team, username) => {
    if (team === 'A') setManualA(prev => prev.filter(p => p !== username))
    else setManualB(prev => prev.filter(p => p !== username))
  }

  const calcWinChance = async () => {
    if (manualA.length === 0 || manualB.length === 0) {
      alert('Both teams need at least 1 player')
      return
    }
    setLoading(true)
    const response = await fetch("/api/winchance", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ teamA: manualA, teamB: manualB })
    })
    const data = await response.json()
    setTeams({ ...data, teamA: manualA, teamB: manualB })
    setLoading(false)
  }

  const availablePlayers = users.filter(
    u => ![...manualA, ...manualB].includes(u.username)
  )

  const prob1 = teams ? (teams.quality).toFixed(2) : 50

  return (
    <>
      <Navbar />
      <div className="page">
        <header>
          <h1>Quick Teams</h1>
          <p>Select players · find fairest split</p>
        </header>

        {/* Mode Toggle */}
        <div className="mode-toggle">
          <button
            className={`mode-btn ${mode === 'auto' ? 'active' : ''}`}
            onClick={() => switchMode('auto')}
          >
            ⚡ Auto Split
          </button>
          <button
            className={`mode-btn ${mode === 'manual' ? 'active' : ''}`}
            onClick={() => switchMode('manual')}
          >
            🎯 Manual Teams
          </button>
        </div>

        {/* AUTO MODE */}
        {mode === 'auto' && (
          <form onSubmit={makeTeams}>
            <div className="card">
              <div className="card-label">🎮 Select Players</div>
              <div className="slots-grid">
                {[...Array(10)].map((_, i) =>
                  <div className="slot-wrap" key={i}>
                    <span className="slot-label">Slot {i + 1}</span>
                    <select className="player-select" name={`slot${i}`}>
                      <option value="">— Empty —</option>
                      {users.map(p =>
                        <option key={p.user_id} value={p.username}>{p.username}</option>
                      )}
                    </select>
                  </div>
                )}
              </div>
            </div>
            <button className="submit-btn" type="submit" disabled={loading}>
              {loading ? 'Calculating...' : '⚡ Make Teams'}
            </button>
          </form>
        )}

        {/* MANUAL MODE */}
        {mode === 'manual' && (
          <div>
            <div className="card">
              <div className="card-label">🎮 Build Your Teams</div>

              {availablePlayers.length > 0 && (
                <div className="available-pool">
                  <div className="pool-label">Available Players</div>
                  <div className="pool-players">
                    {availablePlayers.map(u => (
                      <div key={u.user_id} className="pool-player">
                        <span>{u.username}</span>
                        <div className="pool-actions">
                          <button className="add-btn a" onClick={() => addToTeam('A', u.username)}>+ A</button>
                          <button className="add-btn b" onClick={() => addToTeam('B', u.username)}>+ B</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="teams-grid manual-teams">
                <div className="team-block ta">
                  <div className="team-block-title"><span className="dot"></span> Team A</div>
                  {manualA.length === 0 && <div className="empty-team">No players yet</div>}
                  {manualA.map((p, i) => (
                    <div className="team-player" key={i}>
                      <div className="player-avatar">{p.substring(0, 2).toUpperCase()}</div>
                      <span>{p}</span>
                      <button className="remove-btn" onClick={() => removeFromTeam('A', p)}>×</button>
                    </div>
                  ))}
                </div>
                <div className="team-block tb">
                  <div className="team-block-title"><span className="dot"></span> Team B</div>
                  {manualB.length === 0 && <div className="empty-team">No players yet</div>}
                  {manualB.map((p, i) => (
                    <div className="team-player" key={i}>
                      <div className="player-avatar">{p.substring(0, 2).toUpperCase()}</div>
                      <span>{p}</span>
                      <button className="remove-btn" onClick={() => removeFromTeam('B', p)}>×</button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <button className="submit-btn" onClick={calcWinChance} disabled={loading}>
              {loading ? 'Calculating...' : '🎯 Calculate Win Chance'}
            </button>
          </div>
        )}

        {/* RESULTS — shared between both modes */}
        {teams && (
          <>
            <div className="prob-card">
              <div className="prob-title">⚡ Win Probability</div>
              <div className="prob-verdict">
                Team A has a <strong>{prob1}%</strong> chance to win
              </div>
            </div>
            <div className="result-card visible">
              <div className="result-title">Teams</div>
              <div className="teams-grid">
                <div className="team-block ta">
                  <div className="team-block-title"><span className="dot"></span> Team A</div>
                  {teams.teamA.map((p, i) =>
                    <div className="team-player" key={i}>
                      <div className="player-avatar">{p.substring(0, 2).toUpperCase()}</div>
                      {p}
                    </div>
                  )}
                </div>
                <div className="team-block tb">
                  <div className="team-block-title"><span className="dot"></span> Team B</div>
                  {teams.teamB.map((p, i) =>
                    <div className="team-player" key={i}>
                      <div className="player-avatar">{p.substring(0, 2).toUpperCase()}</div>
                      {p}
                    </div>
                  )}
                </div>
              </div>
              {mode === 'auto' && (
                <button className="reshuffle-btn" type="button"
                  onClick={() => document.querySelector('form').requestSubmit()}>
                  🔀 Reshuffle
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </>
  )
}

export default App