function Navbar() {
  return (
    <nav className="navbar">
      <a href="http://localhost:5000/matches" className="nav-logo">R6 Stats</a>
      <div className="nav-links">
        <a href="http://localhost:5000/matches" className="nav-link">Matches</a>
        <a href="http://localhost:5000/quick-teams" className="nav-link">Quick Teams</a>
      </div>
    </nav>
  )
}

export default Navbar