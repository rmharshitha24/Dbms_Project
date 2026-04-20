import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const logout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="navbar">
      <div>
        <div className="navbar-title">Organ Transplant System</div>
        <div className="muted-text" style={{ color: "#dbeafe", marginTop: 4 }}>
          Logged in as: {user?.username} ({user?.role})
        </div>
      </div>

      <div className="navbar-actions">
        <button className="nav-btn" onClick={() => navigate("/")}>
          Home
        </button>
        <button className="nav-btn" onClick={logout}>
          Logout
        </button>
      </div>
    </div>
  );
}

export default Navbar;