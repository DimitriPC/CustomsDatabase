import { useState, useEffect } from 'react'
import './App.css'
import Navbar from './Navbar'


function App() {
  const [users, setUsers] = useState([])
  const [teams, setTeams] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchUsers = async () => {
      const response = await fetch("/api/users")
      const data = await response.json()
      setUsers(data)
    }
    fetchUsers()
  }, [])

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

  const prob1 = teams ? (teams.quality).toFixed(2) : 50
  


  return (
    <>
        <Navbar />
        <div className="page">

          <header>
            <h1>Quick Teams</h1>
            <p>Select players · find fairest split</p>
          </header>

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
                <button className="reshuffle-btn" type="button"
                  onClick={() => document.querySelector('form').requestSubmit()}>
                  🔀 Reshuffle
                </button>
              </div>
            </>
          )}

        </div>
    </>
  )
}

export default App