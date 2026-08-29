import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowRight,
  Database,
  FileText,
  Lock,
  MessageSquare,
  Shield,
  ShieldCheck,
  Sparkles,
  UserCheck,
} from "lucide-react";
import { Navbar } from "./components/Navbar";
import { LoginPage } from "./components/LoginPage";
import { RegisterPage } from "./components/RegisterPage";
import { DashboardView } from "./components/DashboardView";
import { ChatInterface } from "./components/ChatInterface";
import { AdminView } from "./components/AdminView";
import { AuthProvider, useAuth } from "./context/AuthContext";
import "./styles.css";

type View = "home" | "login" | "register" | "dashboard" | "chat" | "admin";

function MainApp() {
  const [currentView, setCurrentView] = useState<View>("home");
  const [initialChatPrompt, setInitialChatPrompt] = useState<string | null>(null);
  const { user, isAuthenticated, isAdmin, isLoading } = useAuth();

  const handleNavigate = (view: View) => {
    if ((view === "dashboard" || view === "chat" || view === "admin") && !isAuthenticated) {
      setCurrentView("login");
      return;
    }
    setCurrentView(view);
  };

  const handleStartChatFromQuery = (queryText: string) => {
    setInitialChatPrompt(queryText);
    setCurrentView("chat");
  };

  return (
    <div className="app-container">
      <Navbar currentView={currentView} onNavigate={handleNavigate} />

      <main className="main-content">
        {currentView === "home" && (
          <div className="home-view">
            <section className="hero-section">
              <p className="eyebrow">JCET Institutional Knowledge Platform</p>
              <h1 className="hero-title">Find what the campus knows.</h1>
              <p className="hero-lede">
                A grounded workspace for exploring official Jawaharlal College of Engineering and
                Technology documents with verified citations, precision retrieval, and strict access controls.
              </p>

              <div className="hero-actions">
                {isAuthenticated ? (
                  <>
                    <button
                      type="button"
                      onClick={() => handleNavigate("chat")}
                      className="btn-hero-primary"
                    >
                      <Sparkles size={17} />
                      <span>Ask CampusIQ Intelligence</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleNavigate("dashboard")}
                      className="btn-hero-secondary"
                    >
                      <span>Workspace Dashboard</span>
                    </button>
                    {isAdmin && (
                      <button
                        type="button"
                        onClick={() => handleNavigate("admin")}
                        className="btn-hero-secondary"
                      >
                        <Shield size={16} />
                        <span>Admin Console</span>
                      </button>
                    )}
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => handleNavigate("register")}
                      className="btn-hero-primary"
                    >
                      <span>Get Started</span>
                      <ArrowRight size={17} />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleNavigate("login")}
                      className="btn-hero-secondary"
                    >
                      <Lock size={16} />
                      <span>Sign In</span>
                    </button>
                  </>
                )}
              </div>
            </section>

            <section className="signals-section" aria-label="Core Foundations">
              <article className="signal-card">
                <Database size={24} />
                <strong>PostgreSQL + pgvector</strong>
                <span>1536-dimensional vector embedding store ready for semantic search.</span>
              </article>

              <article className="signal-card">
                <ShieldCheck size={24} />
                <strong>Role-Based Access Control</strong>
                <span>Argon2/bcrypt password hashing with JWT access tokens for Student and Admin roles.</span>
              </article>

              <article className="signal-card">
                <FileText size={24} />
                <strong>Strict Source Grounding</strong>
                <span>Official JCET documents form the sole factual foundation for responses.</span>
              </article>
            </section>
          </div>
        )}

        {currentView === "login" && (
          <LoginPage
            onSuccess={() => setCurrentView("chat")}
            onNavigateToRegister={() => setCurrentView("register")}
          />
        )}

        {currentView === "register" && (
          <RegisterPage
            onSuccess={() => setCurrentView("chat")}
            onNavigateToLogin={() => setCurrentView("login")}
          />
        )}

        {currentView === "chat" && (
          isAuthenticated ? (
            <ChatInterface
              initialPrompt={initialChatPrompt}
              onClearInitialPrompt={() => setInitialChatPrompt(null)}
            />
          ) : (
            <LoginPage
              onSuccess={() => setCurrentView("chat")}
              onNavigateToRegister={() => setCurrentView("register")}
            />
          )
        )}

        {currentView === "dashboard" && (
          isAuthenticated ? (
            <DashboardView onStartChat={handleStartChatFromQuery} />
          ) : (
            <LoginPage
              onSuccess={() => setCurrentView("dashboard")}
              onNavigateToRegister={() => setCurrentView("register")}
            />
          )
        )}

        {currentView === "admin" && (
          isAuthenticated ? (
            <AdminView />
          ) : (
            <LoginPage
              onSuccess={() => setCurrentView("admin")}
              onNavigateToRegister={() => setCurrentView("register")}
            />
          )
        )}
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  </StrictMode>
);
