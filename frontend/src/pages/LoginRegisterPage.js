import { useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function LoginRegisterPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({
    username: "",
    password: "",
    role: ""
  });
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async () => {
    try {
      setMessage("");

      if (!form.username || !form.password) {
        setMessage("Username and password are required");
        return;
      }

      if (!isLogin && !form.role) {
        setMessage("Please select a role");
        return;
      }

      if (isLogin) {
        const res = await API.post("/login", {
          username: form.username,
          password: form.password
        });

        if (res.data.user) {
          localStorage.setItem("user", JSON.stringify(res.data.user));
          setMessage("Login successful");

          if (res.data.user.role === "donor") navigate("/donor");
          else if (res.data.user.role === "recipient") navigate("/recipient");
          else if (res.data.user.role === "staff") navigate("/staff");
        } else {
          setMessage("Login failed");
        }
      } else {
        const res = await API.post("/register", {
          username: form.username,
          password: form.password,
          role: form.role
        });

        setMessage(res.data.message || "Registered successfully. Please login.");
        setIsLogin(true);
        setForm({
          username: "",
          password: "",
          role: ""
        });
      }
    } catch (err) {
      console.log("FULL ERROR:", err);
      console.log("ERROR RESPONSE:", err.response);

      if (err.response && err.response.data && err.response.data.error) {
        setMessage(err.response.data.error);
      } else if (err.message) {
        setMessage(err.message);
      } else {
        setMessage("Something went wrong");
      }
    }
  };

  return (
    <div className="center-wrap">
      <div className="card auth-card">
        <h2 className="page-title">{isLogin ? "Login" : "Register"}</h2>

        <div className="form-grid">
          <input
            className="input"
            placeholder="Username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />

          <input
            className="input"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />

          {!isLogin && (
            <select
              className="select"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              <option value="">Select Role</option>
              <option value="donor">Donor</option>
              <option value="recipient">Recipient</option>
              <option value="staff">Staff</option>
            </select>
          )}

          <button className="btn btn-primary" onClick={handleSubmit}>
            {isLogin ? "Login" : "Register"}
          </button>
        </div>

        {message && (
          <p style={{ marginTop: "14px" }}>
            {message}
          </p>
        )}

        <p className="auth-switch" onClick={() => {
          setIsLogin(!isLogin);
          setMessage("");
        }}>
          Switch to {isLogin ? "Register" : "Login"}
        </p>
      </div>
    </div>
  );
}

export default LoginRegisterPage;