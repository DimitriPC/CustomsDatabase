import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [users, setUsers] = useState([])
  const [teams, setTeams] = useState([])
  const playernbr = 10

  useEffect (() => {
      const fetchUsers = async () => {
        const response = await fetch("http://127.0.0.1:5001/api/users")
        const data = await response.json()
        setUsers(data)
      }
      fetchUsers()
  }, [])

  const makeTeams = async () => {
      const response = await fetch("http://127.0.0.1:5001/api/maketeams")
      const data = await response.json()
      setTeams(data)
      console.log(teams)
  }

      

  return (
    <>
      <div className="page">

    <header>
        <h1>Quick Teams</h1>
        <p>Select players · randomize teams</p>
    </header>

    <div className="card">
        <div className="card-label">🎮 Select Players</div>
        <div className="slots-grid">
            {[...Array(playernbr)].map((_, i+1) => 
                <div className="slot-wrap">
                    <span className="slot-label">Slot { i }</span>
                    <select className="player-select" id="slot{{ i }}">
                        <option value="">— Empty —</option>
                        {users.map((player, i) =>
                            <option value="{{ player.username }}">player.username</option>
                        )}
                    </select>
                </div>
            )}
        </div>
    </div>

    <button className="submit-btn" onclick="makeTeams()">⚡ Make Teams</button>

    <div className="result-card" id="resultCard">
        <div className="result-title">Teams</div>
        <div className="teams-grid">
            <div className="team-block ta">
                <div className="team-block-title"><span className="dot"></span> Team A</div>
                <div id="teamA"></div>
            </div>
            <div className="team-block tb">
                <div className="team-block-title"><span className="dot"></span> Team B</div>
                <div id="teamB"></div>
            </div>
        </div>
        <button className="reshuffle-btn" onclick="makeTeams()">🔀 Reshuffle</button>
    </div>

</div>
    </>
  )
}

export default App
