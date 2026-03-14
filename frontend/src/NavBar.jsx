function Navbar() {
  return (
    <nav className="navbar">
      <a href="/matches" className="nav-logo">R6 Stats</a>
      <div className="nav-links">
        <a href="/matches" className="nav-link">Matches</a>
        <a href="/ranking" className="nav-link">Ranking</a>
        <a href="/quick-teams" className="nav-link active">Quick Teams</a>
      </div>
    </nav>
  )
}

export default Navbar