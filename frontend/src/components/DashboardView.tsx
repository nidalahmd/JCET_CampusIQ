import {
  Activity,
  AlertCircle,
  ArrowRight,
  BookOpen,
  Calendar,
  CheckCircle2,
  Database,
  FileCheck,
  GraduationCap,
  HelpCircle,
  KeyRound,
  Layers,
  Loader2,
  Lock,
  Mail,
  MessageSquare,
  Save,
  Search,
  Settings as SettingsIcon,
  Shield,
  Sparkles,
  User as UserIcon,
} from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import type { DocumentItem } from "../types/document";

interface DashboardViewProps {
  onStartChat?: (query: string) => void;
}

export function DashboardView({ onStartChat }: DashboardViewProps = {}) {
  const { user, token, updateProfile, changePassword } = useAuth();

  // Knowledge & System Stats State
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [dbStatus, setDbStatus] = useState<string>("Checking...");
  const [activeTab, setActiveTab] = useState<"workspace" | "profile">("workspace");

  // Query Input State
  const [searchQuery, setSearchQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);

  // Profile Edit State
  const [name, setName] = useState(user?.name ?? "");
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);

  // Change Password State
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    // Fetch live documents count and db health
    api
      .getDocuments(token)
      .then((res) => {
        setDocuments(res.items);
      })
      .catch(() => {})
      .finally(() => setIsLoadingDocs(false));

    api
      .checkDbHealth()
      .then((res) => {
        if (res.status === "ok") {
          setDbStatus("Online & pgvector Ready");
        } else {
          setDbStatus("Offline");
        }
      })
      .catch(() => setDbStatus("Offline"));
  }, [token]);

  if (!user) {
    return null;
  }

  const handleProfileUpdate = async (e: FormEvent) => {
    e.preventDefault();
    setProfileError(null);
    setProfileSuccess(null);
    setIsUpdatingProfile(true);

    try {
      await updateProfile({ name: name.trim() });
      setProfileSuccess("Profile updated successfully!");
      setTimeout(() => setProfileSuccess(null), 4000);
    } catch (err: unknown) {
      if (err instanceof Error) setProfileError(err.message);
      else setProfileError("Failed to update profile.");
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(null);

    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters long.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }

    setIsChangingPassword(true);

    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setPasswordSuccess("Password changed successfully!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setPasswordSuccess(null), 4000);
    } catch (err: unknown) {
      if (err instanceof Error) setPasswordError(err.message);
      else setPasswordError("Failed to change password. Check your current password.");
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleSearchSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    if (onStartChat) {
      onStartChat(searchQuery.trim());
    } else {
      setSubmittedQuery(searchQuery.trim());
    }
  };

  const handleSelectSuggestion = (suggestion: string) => {
    if (onStartChat) {
      onStartChat(suggestion);
    } else {
      setSearchQuery(suggestion);
      setSubmittedQuery(suggestion);
    }
  };

  const totalChunks = documents.reduce((acc, d) => acc + (d.chunks_count || 0), 0);
  const processedDocs = documents.filter((d) => d.processing_status === "PROCESSED").length;

  const quickQuestions = [
    "What is the minimum attendance requirement at JCET?",
    "What are the passing marks and grading system for B.Tech?",
    "What are the working hours and borrowing rules of the Central Library?",
    "What are the eligibility criteria for CSE campus placements?",
    "How is Continuous Internal Evaluation (CIE) calculated?",
    "What scholarships and fee waivers are offered at JCET?",
  ];

  const formattedDate = new Date(user.created_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="dashboard-container">
      {/* Top Navigation & Profile Bar */}
      <div className="dashboard-top-nav">
        <div className="dashboard-title-group">
          <h1>Student Knowledge Workspace</h1>
          <p>Explore official Jawaharlal College of Engineering and Technology institutional knowledge</p>
        </div>

        <div className="dashboard-view-toggles">
          <button
            type="button"
            className={`view-tab-btn ${activeTab === "workspace" ? "active" : ""}`}
            onClick={() => setActiveTab("workspace")}
          >
            <BookOpen size={16} />
            <span>Workspace</span>
          </button>
          <button
            type="button"
            className={`view-tab-btn ${activeTab === "profile" ? "active" : ""}`}
            onClick={() => setActiveTab("profile")}
          >
            <SettingsIcon size={16} />
            <span>Account Settings</span>
          </button>
        </div>
      </div>

      {activeTab === "workspace" ? (
        <div className="student-workspace-view">
          {/* Welcome Banner */}
          <section className="student-hero-banner">
            <div className="hero-banner-content">
              <div className="hero-badge">
                <GraduationCap size={16} />
                <span>JCET CampusIQ Active Session</span>
              </div>
              <h2>Welcome, {user.name}</h2>
              <p>
                Access verified citations, academic regulations, examination schedules, and departmental policies directly from official JCET records.
              </p>
            </div>

            <div className="hero-system-status">
              <div className="status-mini-card">
                <Database size={18} className="text-emerald" />
                <div>
                  <span className="stat-mini-label">System State</span>
                  <strong className="stat-mini-val">{dbStatus}</strong>
                </div>
              </div>
              <div className="status-mini-card">
                <Layers size={18} className="text-indigo" />
                <div>
                  <span className="stat-mini-label">Knowledge Base</span>
                  <strong className="stat-mini-val">
                    {isLoadingDocs ? "..." : `${processedDocs} Documents (${totalChunks} Chunks)`}
                  </strong>
                </div>
              </div>
            </div>
          </section>

          {/* Search / Chat Entry Point */}
          <section className="query-entry-section">
            <div className="query-card">
              <div className="query-card-header">
                <Sparkles size={20} className="query-icon" />
                <div>
                  <h3>CampusIQ Intelligence Query</h3>
                  <p>Ask factual questions grounded in official JCET documents</p>
                </div>
              </div>

              <form onSubmit={handleSearchSubmit} className="query-form">
                <div className="query-input-wrapper">
                  <Search className="search-icon" size={20} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Ask about attendance rules, exam dates, library policies, CSE department..."
                  />
                  <button type="submit" className="btn-query-submit">
                    <span>Ask CampusIQ</span>
                    <ArrowRight size={16} />
                  </button>
                </div>
              </form>

              {/* Submitted Query Preview (Demo feedback before Phase 4 RAG integration) */}
              {submittedQuery && (
                <div className="query-preview-banner">
                  <div className="query-preview-header">
                    <MessageSquare size={16} />
                    <span>Query Received: "<strong>{submittedQuery}</strong>"</span>
                  </div>
                  <p className="query-preview-desc">
                    ⚡ <strong>Phase 3 Vector Index Ready:</strong> In Phase 4, CampusIQ will execute hybrid retrieval across {totalChunks} pgvector chunks and generate grounded answers with precise section and page citations.
                  </p>
                </div>
              )}

              {/* Suggestion Chips */}
              <div className="query-suggestions">
                <div className="suggestions-label">
                  <HelpCircle size={14} />
                  <span>Popular Question Suggestions:</span>
                </div>
                <div className="suggestion-chips-grid">
                  {quickQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="suggestion-chip"
                      onClick={() => handleSelectSuggestion(q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Available Knowledge Documents Grid */}
          <section className="available-knowledge-section">
            <div className="section-header-compact">
              <BookOpen size={18} />
              <h3>Indexed Official Knowledge Base</h3>
              <span className="docs-count-pill">{documents.length} Documents Available</span>
            </div>

            {isLoadingDocs ? (
              <div className="doc-loading">
                <Loader2 className="animate-spin" size={24} />
                <p>Loading available knowledge items...</p>
              </div>
            ) : (
              <div className="knowledge-cards-grid">
                {documents.map((doc) => (
                  <article key={doc.id} className="knowledge-item-card">
                    <div className="item-header">
                      <FileCheck size={18} className="item-icon" />
                      <span className="item-category">{doc.category || "General"}</span>
                      <span className="item-chunks">{doc.chunks_count} chunks</span>
                    </div>
                    <h4>{doc.title}</h4>
                    <span className="item-dept">{doc.department || "Institutional"}</span>
                    <div className="item-footer">
                      <span>Academic Year: {doc.academic_year || "2025-2026"}</span>
                      <span className="status-dot-green">● Verified</span>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          {/* Recent Conversations / Activity */}
          <section className="conversations-section">
            <div className="section-header-compact">
              <MessageSquare size={18} />
              <h3>Recent Conversations</h3>
            </div>
            <div className="conversations-empty-card">
              <MessageSquare size={36} className="empty-chat-icon" />
              <h4>No conversation history yet</h4>
              <p>Type a question in the search box above to start exploring JCET knowledge.</p>
            </div>
          </section>
        </div>
      ) : (
        /* Profile & Account Settings Tab */
        <div className="dashboard-grid">
          {/* Account Details Card */}
          <section className="dashboard-card profile-card">
            <div className="card-header">
              <UserIcon size={20} className="card-icon" />
              <h2>Profile Details</h2>
            </div>

            <div className="account-meta-list">
              <div className="meta-item">
                <span className="meta-label">Email</span>
                <div className="meta-value">
                  <Mail size={15} />
                  <span>{user.email}</span>
                </div>
              </div>

              <div className="meta-item">
                <span className="meta-label">Role</span>
                <div className="meta-value">
                  <Shield size={15} />
                  <span className="capitalize">{user.role}</span>
                </div>
              </div>

              <div className="meta-item">
                <span className="meta-label">Member Since</span>
                <div className="meta-value">
                  <Calendar size={15} />
                  <span>{formattedDate}</span>
                </div>
              </div>
            </div>

            <form onSubmit={handleProfileUpdate} className="dashboard-form">
              {profileSuccess && (
                <div className="alert-banner success">
                  <CheckCircle2 size={16} />
                  <span>{profileSuccess}</span>
                </div>
              )}
              {profileError && (
                <div className="alert-banner error">
                  <AlertCircle size={16} />
                  <span>{profileError}</span>
                </div>
              )}

              <div className="form-group">
                <label htmlFor="profile-name">Full Name</label>
                <input
                  id="profile-name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={isUpdatingProfile}
                />
              </div>

              <button
                type="submit"
                className="btn-secondary"
                disabled={isUpdatingProfile || name.trim() === user.name}
              >
                {isUpdatingProfile ? (
                  <>
                    <Loader2 className="animate-spin" size={16} />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save size={16} />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
            </form>
          </section>

          {/* Security & Password Card */}
          <section className="dashboard-card security-card">
            <div className="card-header">
              <KeyRound size={20} className="card-icon" />
              <h2>Change Password</h2>
            </div>

            <form onSubmit={handleChangePassword} className="dashboard-form">
              {passwordSuccess && (
                <div className="alert-banner success">
                  <CheckCircle2 size={16} />
                  <span>{passwordSuccess}</span>
                </div>
              )}
              {passwordError && (
                <div className="alert-banner error">
                  <AlertCircle size={16} />
                  <span>{passwordError}</span>
                </div>
              )}

              <div className="form-group">
                <label htmlFor="current-password">Current Password</label>
                <input
                  id="current-password"
                  type="password"
                  required
                  placeholder="••••••••"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  disabled={isChangingPassword}
                />
              </div>

              <div className="form-group">
                <label htmlFor="new-password">New Password (min 8 chars)</label>
                <input
                  id="new-password"
                  type="password"
                  required
                  minLength={8}
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  disabled={isChangingPassword}
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirm-password">Confirm New Password</label>
                <input
                  id="confirm-password"
                  type="password"
                  required
                  minLength={8}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={isChangingPassword}
                />
              </div>

              <button
                type="submit"
                className="btn-secondary"
                disabled={isChangingPassword || !currentPassword || !newPassword || !confirmPassword}
              >
                {isChangingPassword ? (
                  <>
                    <Loader2 className="animate-spin" size={16} />
                    <span>Updating Password...</span>
                  </>
                ) : (
                  <>
                    <KeyRound size={16} />
                    <span>Update Password</span>
                  </>
                )}
              </button>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
