import {
  Activity,
  CheckCircle2,
  Lock,
  LogOut,
  Shield,
  User as UserIcon,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

interface NavbarProps {
  currentView: "home" | "login" | "register" | "dashboard" | "chat" | "admin";
  onNavigate: (view: "home" | "login" | "register" | "dashboard" | "chat" | "admin") => void;
}

export function Navbar({ currentView, onNavigate }: NavbarProps) {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const [healthStatus, setHealthStatus] = useState<"checking" | "connected" | "offline">("checking");

  useEffect(() => {
    api
      .checkDbHealth()
      .then((res) => {
        if (res.status === "ok" && res.database === "connected") {
          setHealthStatus("connected");
        } else {
          setHealthStatus("offline");
        }
      })
      .catch(() => setHealthStatus("offline"));
  }, []);

  return (
    <header className="navbar-container">
      <div className="navbar-content">
        {/* Brand */}
        <button
          type="button"
          onClick={() => onNavigate("home")}
          className="navbar-brand"
        >
          <span className="brand-logo">CI</span>
          <div className="brand-text">
            <span className="brand-title">JCET CampusIQ</span>
            <span className="brand-subtitle">Institutional RAG Platform</span>
          </div>
        </button>

        
        {/* Navigation & User Actions */}
        <div className="navbar-actions">
          <button
            type="button"
            onClick={() => onNavigate("home")}
            className={`nav-link ${currentView === "home" ? "active" : ""}`}
          >
            Home
          </button>

          {isAuthenticated && (
            <button
              type="button"
              onClick={() => onNavigate("chat")}
              className={`nav-link chat-nav-link ${currentView === "chat" ? "active" : ""}`}
            >
              Ask CampusIQ
            </button>
          )}

          {isAuthenticated && (
            <button
              type="button"
              onClick={() => onNavigate("dashboard")}
              className={`nav-link ${currentView === "dashboard" ? "active" : ""}`}
            >
              Dashboard
            </button>
          )}

          {isAuthenticated && isAdmin && (
            <button
              type="button"
              onClick={() => onNavigate("admin")}
              className={`nav-link admin-nav-link ${currentView === "admin" ? "active" : ""}`}
            >
              <Shield size={14} /> Admin
            </button>
          )}

          <div className="auth-separator" />

          {isAuthenticated && user ? (
            <div className="user-profile-menu">
              <button
                type="button"
                onClick={() => onNavigate("dashboard")}
                className="user-profile-button"
              >
                <div className="user-avatar">
                  <UserIcon size={16} />
                </div>
                <div className="user-info-text">
                  <span className="user-name">{user.name}</span>
                  <span className={`role-chip ${user.role}`}>
                    {user.role === "admin" ? "ADMIN" : "STUDENT"}
                  </span>
                </div>
              </button>
              <button
                type="button"
                onClick={logout}
                className="btn-logout"
                title="Logout"
              >
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="auth-buttons-group">
              <button
                type="button"
                onClick={() => onNavigate("login")}
                className={`btn-auth-signin ${currentView === "login" ? "active" : ""}`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => onNavigate("register")}
                className="btn-auth-register"
              >
                Register
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
