import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Database,
  FileCheck,
  FileText,
  HardDrive,
  Layers,
  Loader2,
  Lock,
  Plus,
  RefreshCw,
  ShieldCheck,
  UserCheck,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import { DocumentManagement } from "./DocumentManagement";
import type { DocumentItem } from "../types/document";

export function AdminView() {
  const { token, user } = useAuth();
  const [adminStatus, setAdminStatus] = useState<"checking" | "authorized" | "denied">("checking");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [dbInfo, setDbInfo] = useState<{ database: string; pgvector: string } | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  const fetchAdminStats = async () => {
    if (!token) {
      setAdminStatus("denied");
      setErrorMessage("No authentication token provided.");
      return;
    }

    setAdminStatus("checking");
    setErrorMessage(null);

    try {
      await api.checkAdmin(token);
      setAdminStatus("authorized");

      // Load DB health
      const health = await api.checkDbHealth();
      setDbInfo({ database: health.database, pgvector: health.pgvector });

      // Load Live Documents
      const docsRes = await api.getDocuments(token);
      setDocuments(docsRes.items);
    } catch (err: unknown) {
      setAdminStatus("denied");
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Access denied: You do not have administrator permissions.");
      }
    } finally {
      setIsLoadingStats(false);
    }
  };

  useEffect(() => {
    fetchAdminStats();
  }, [token]);

  if (adminStatus === "checking") {
    return (
      <div className="admin-loading-container">
        <Loader2 className="animate-spin" size={32} />
        <p>Verifying administrative privileges...</p>
      </div>
    );
  }

  if (adminStatus === "denied") {
    return (
      <div className="admin-denied-container">
        <div className="denied-card">
          <div className="denied-icon">
            <Lock size={32} />
          </div>
          <h2>Access Restricted</h2>
          <p>{errorMessage || "Administrative role required to view this panel."}</p>
          <div className="denied-user-info">
            <span>Signed in as: <strong>{user?.email}</strong></span>
            <span className="role-chip student">Role: {user?.role}</span>
          </div>
        </div>
      </div>
    );
  }

  // Dynamic live calculations from PostgreSQL database
  const totalDocs = documents.length;
  const processedDocs = documents.filter((d) => d.processing_status === "PROCESSED").length;
  const pendingOrFailedDocs = documents.filter(
    (d) => d.processing_status === "PROCESSING" || d.processing_status === "UPLOADED" || d.processing_status === "FAILED"
  ).length;
  const totalChunks = documents.reduce((acc, d) => acc + (d.chunks_count || 0), 0);

  return (
    <div className="admin-container">
      <div className="admin-header">
        <div className="admin-title-group">
          <div className="admin-badge">
            <ShieldCheck size={18} />
            <span>Administrator Authorized</span>
          </div>
          <h1>JCET Knowledge Management Console</h1>
          <p>Institutional document ingestion, RAG vector index, and system telemetry</p>
        </div>

        <button
          type="button"
          onClick={fetchAdminStats}
          className="btn-refresh"
          title="Refresh authorization and statistics"
        >
          <RefreshCw size={16} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Dynamic Live Admin Statistics Grid */}
      <div className="admin-stats-grid">
        <article className="stat-card">
          <div className="stat-icon-wrapper blue">
            <FileText size={22} />
          </div>
          <div className="stat-info">
            <span className="stat-label">Total Documents</span>
            <strong className="stat-value">{isLoadingStats ? "..." : totalDocs}</strong>
            <span className="stat-sub">Indexed in Catalog</span>
          </div>
        </article>

        <article className="stat-card">
          <div className="stat-icon-wrapper green">
            <FileCheck size={22} />
          </div>
          <div className="stat-info">
            <span className="stat-label">Processed & Ready</span>
            <strong className="stat-value">{isLoadingStats ? "..." : processedDocs}</strong>
            <span className="stat-sub">Active in Knowledge Base</span>
          </div>
        </article>

        <article className="stat-card">
          <div className="stat-icon-wrapper purple">
            <Layers size={22} />
          </div>
          <div className="stat-info">
            <span className="stat-label">Total pgvector Chunks</span>
            <strong className="stat-value">{isLoadingStats ? "..." : totalChunks}</strong>
            <span className="stat-sub">1536-dim Vector Embeddings</span>
          </div>
        </article>

        <article className="stat-card">
          <div className={`stat-icon-wrapper ${pendingOrFailedDocs > 0 ? "orange" : "emerald"}`}>
            <Clock size={22} />
          </div>
          <div className="stat-info">
            <span className="stat-label">Pending / Processing</span>
            <strong className="stat-value">{isLoadingStats ? "..." : pendingOrFailedDocs}</strong>
            <span className="stat-sub">Ingestion Queue Status</span>
          </div>
        </article>
      </div>

      {/* Embedded Full Document Management */}
      <DocumentManagement onDocumentsChanged={fetchAdminStats} />
    </div>
  );
}
