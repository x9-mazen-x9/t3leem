import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Bell, Home, LogOut, Newspaper, User } from "lucide-react";
import ThemeSwitch from "./ThemeSwitch";

const NavBar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(false);

  const isActive = (path) => location.pathname === path;

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_type");
    navigate("/login");
  };

  useEffect(() => {
    const isDarkMode = document.body.classList.contains("dark-mode");
    setIsDark(isDarkMode);
  }, []);

  const handleThemeChange = () => {
    document.body.classList.toggle("dark-mode");
    setIsDark(!isDark);
  };

  return (
    <header className="social-header glass-card" style={{ borderRadius: 0, position: "sticky", top: 0, zIndex: 100 }}>
      <div className="nav-content" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 50px" }}>
        <Link to="/dashboard" className="logo" style={{ fontSize: "1.5rem" }}>
          MAJMA
        </Link>

        {["/social", "/dashboard"].includes(location.pathname) && (
          <div style={{ flex: 1, margin: "0 40px" }}>
            <input
              type="text"
              placeholder="ابحث..."
              className="input-field"
              style={{ background: "var(--input-bg)", height: "40px", marginBottom: 0 }}
            />
          </div>
        )}

        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <Link
            to="/dashboard"
            className="icon-btn-nav"
            style={{
              padding: "8px 12px",
              borderRadius: "12px",
              background: isActive("/dashboard") ? "var(--primary-gradient)" : "transparent",
              color: isActive("/dashboard") ? "white" : "inherit",
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              textDecoration: "none",
            }}
          >
            <Home size={18} /> لوحة التحكم
          </Link>
          <Link
            to="/social"
            className="icon-btn-nav"
            style={{
              padding: "8px 12px",
              borderRadius: "12px",
              background: isActive("/social") ? "var(--primary-gradient)" : "transparent",
              color: isActive("/social") ? "white" : "inherit",
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              textDecoration: "none",
            }}
          >
            <Newspaper size={18} /> السوشيال
          </Link>
          <Link to="/notifications" className="icon-btn-nav" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
            <Bell size={18} /> الإشعارات
          </Link>
          <Link to="/profile" className="icon-btn-nav" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
            <User size={18} /> بروفايل
          </Link>

          <ThemeSwitch isChecked={isDark} onChange={handleThemeChange} />

          <button
            onClick={logout}
            className="btn"
            style={{ background: "transparent", border: "2px solid #ef4444", color: "#ef4444" }}
          >
            <LogOut size={18} /> خروج
          </button>
        </div>
      </div>
    </header>
  );
};

export default NavBar;
