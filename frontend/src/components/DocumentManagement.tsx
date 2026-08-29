import {
  AlertCircle,
  Archive,
  CheckCircle2,
  FileCode,
  FileSpreadsheet,
  FileText,
  Layers,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import type {
  DocumentChunk,
  DocumentItem,
  ProcessingStatus,
} from "../types/document";

interface DocumentManagementProps {
  onDocumentsChanged?: () => void;
}

export function DocumentManagement({ onDocumentsChanged }: DocumentManagementProps = {}) {
  const { token } = useAuth();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  // Upload Modal State
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("Academics");
  const [department, setDepartment] = useState("Computer Science & Engineering");
  const [academicYear, setAcademicYear] = useState("2025-2026");
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Chunk Inspector Drawer State
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [isLoadingChunks, setIsLoadingChunks] = useState(false);

  const fetchDocuments = async () => {
    if (!token) return;
    try {
      setError(null);
      const res = await api.getDocuments(token);
      setDocuments(res.items);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Auto refresh if any document is in PROCESSING state
    const interval = setInterval(() => {
      if (documents.some((d) => d.processing_status === "PROCESSING" || d.processing_status === "UPLOADED")) {
        fetchDocuments();
      }
    }, 4000);
    return () => clearInterval(interval);
  }, [token, documents]);

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!file || !token) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      await api.uploadDocument(
        {
          file,
          title: title.trim() || file.name,
          category,
          department,
          academic_year: academicYear,
        },
        token
      );
      setShowUploadModal(false);
      setFile(null);
      setTitle("");
      await fetchDocuments();
      onDocumentsChanged?.();
    } catch (err: unknown) {
      if (err instanceof Error) setUploadError(err.message);
      else setUploadError("Failed to upload document.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcess = async (docId: string) => {
    if (!token) return;
    try {
      await api.processDocument(docId, token);
      await fetchDocuments();
      onDocumentsChanged?.();
    } catch (err: unknown) {
      if (err instanceof Error) alert(err.message);
    }
  };

  const handleReindex = async (docId: string) => {
    if (!token) return;
    try {
      await api.reindexDocument(docId, token);
      await fetchDocuments();
      onDocumentsChanged?.();
    } catch (err: unknown) {
      if (err instanceof Error) alert(err.message);
    }
  };

  const handleArchive = async (docId: string) => {
    if (!token) return;
    try {
      await api.archiveDocument(docId, token);
      await fetchDocuments();
      onDocumentsChanged?.();
    } catch (err: unknown) {
      if (err instanceof Error) alert(err.message);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!token || !confirm("Are you sure you want to delete this document and all its chunks?")) return;
    try {
      await api.deleteDocument(docId, token);
      if (selectedDoc?.id === docId) setSelectedDoc(null);
      await fetchDocuments();
      onDocumentsChanged?.();
    } catch (err: unknown) {
      if (err instanceof Error) alert(err.message);
    }
  };

  const handleViewChunks = async (doc: DocumentItem) => {
    if (!token) return;
    setSelectedDoc(doc);
    setIsLoadingChunks(true);
    try {
      const data = await api.getDocumentChunks(doc.id, token);
      setChunks(data);
    } catch (err: unknown) {
      if (err instanceof Error) alert(err.message);
    } finally {
      setIsLoadingChunks(false);
    }
  };

  const getFormatIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case "pdf":
        return <FileText className="format-icon pdf" size={18} />;
      case "docx":
      case "doc":
        return <FileSpreadsheet className="format-icon docx" size={18} />;
      case "md":
        return <FileCode className="format-icon md" size={18} />;
      default:
        return <FileText className="format-icon txt" size={18} />;
    }
  };

  const getStatusBadge = (status: ProcessingStatus) => {
    switch (status) {
      case "PROCESSED":
        return <span className="doc-status-badge processed"><CheckCircle2 size={12} /> PROCESSED</span>;
      case "PROCESSING":
        return <span className="doc-status-badge processing"><Loader2 className="animate-spin" size={12} /> PROCESSING</span>;
      case "UPLOADED":
        return <span className="doc-status-badge uploaded">UPLOADED</span>;
      case "ARCHIVED":
        return <span className="doc-status-badge archived"><Archive size={12} /> ARCHIVED</span>;
      case "FAILED":
        return <span className="doc-status-badge failed"><AlertCircle size={12} /> FAILED</span>;
    }
  };

  return (
    <div className="doc-management-wrapper">
      <div className="doc-management-header">
        <div>
          <h2>Institutional Knowledge Base</h2>
          <p>Upload, chunk, embed, and index official JCET documents into pgvector</p>
        </div>

        <div className="doc-header-actions">
          <button
            type="button"
            onClick={fetchDocuments}
            className="btn-refresh"
            title="Refresh list"
          >
            <RefreshCw size={15} />
            <span>Refresh</span>
          </button>

          <button
            type="button"
            onClick={() => setShowUploadModal(true)}
            className="btn-primary-doc"
          >
            <Plus size={16} />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="alert-banner error">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Documents Table */}
      <div className="doc-table-container">
        {isLoading ? (
          <div className="doc-loading">
            <Loader2 className="animate-spin" size={28} />
            <p>Loading documents repository...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="doc-empty-state">
            <UploadCloud size={48} className="empty-icon" />
            <h3>No Documents Ingested</h3>
            <p>Upload official college handbooks, regulations, and curricula (PDF, DOCX, TXT, MD).</p>
            <button
              type="button"
              onClick={() => setShowUploadModal(true)}
              className="btn-primary-doc"
            >
              <Plus size={16} />
              <span>Upload First Document</span>
            </button>
          </div>
        ) : (
          <table className="doc-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Category / Dept</th>
                <th>Status</th>
                <th>Chunks (pgvector)</th>
                <th>Version</th>
                <th>Uploaded</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td>
                    <div className="doc-name-cell">
                      {getFormatIcon(doc.file_type)}
                      <div>
                        <strong>{doc.title}</strong>
                        <span className="doc-file-sub">{doc.file_name}</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="doc-meta-cell">
                      <span className="doc-category">{doc.category || "General"}</span>
                      <span className="doc-dept">{doc.department || "All Departments"}</span>
                    </div>
                  </td>
                  <td>{getStatusBadge(doc.processing_status)}</td>
                  <td>
                    <span className="chunk-count-badge">
                      <Layers size={13} />
                      {doc.chunks_count} chunks
                    </span>
                  </td>
                  <td>v{doc.version}</td>
                  <td className="doc-date">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <div className="doc-row-actions">
                      <button
                        type="button"
                        onClick={() => handleViewChunks(doc)}
                        className="btn-action-view"
                        title="View Chunks & Embeddings"
                      >
                        Chunks
                      </button>

                      {doc.processing_status === "PROCESSED" && (
                        <button
                          type="button"
                          onClick={() => handleReindex(doc.id)}
                          className="btn-action-icon"
                          title="Re-index / Update Version"
                        >
                          <RefreshCw size={14} />
                        </button>
                      )}

                      {(doc.processing_status === "FAILED" || doc.processing_status === "UPLOADED") && (
                        <button
                          type="button"
                          onClick={() => handleProcess(doc.id)}
                          className="btn-action-process"
                          title="Process Ingestion Pipeline"
                        >
                          Process
                        </button>
                      )}

                      {doc.processing_status !== "ARCHIVED" && (
                        <button
                          type="button"
                          onClick={() => handleArchive(doc.id)}
                          className="btn-action-icon"
                          title="Archive Document"
                        >
                          <Archive size={14} />
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() => handleDelete(doc.id)}
                        className="btn-action-icon delete"
                        title="Delete Document"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <div className="modal-title-group">
                <UploadCloud size={22} className="modal-icon" />
                <h3>Ingest New Document</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowUploadModal(false)}
                className="btn-modal-close"
              >
                <X size={18} />
              </button>
            </div>

            {uploadError && (
              <div className="alert-banner error">
                <AlertCircle size={16} />
                <span>{uploadError}</span>
              </div>
            )}

            <form onSubmit={handleUpload} className="modal-form">
              <div className="form-group">
                <label>Select File (PDF, DOCX, TXT, MD)</label>
                <input
                  type="file"
                  required
                  accept=".pdf,.docx,.doc,.txt,.md"
                  onChange={(e) => {
                    const selected = e.target.files?.[0] || null;
                    setFile(selected);
                    if (selected && !title) {
                      setTitle(selected.name.replace(/\.[^/.]+$/, ""));
                    }
                  }}
                  disabled={isUploading}
                />
              </div>

              <div className="form-group">
                <label>Document Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. JCET B.Tech Academic Regulations 2026"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={isUploading}
                />
              </div>

              <div className="modal-grid-2">
                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    disabled={isUploading}
                  >
                    <option value="Academics">Academics</option>
                    <option value="Regulations">Regulations</option>
                    <option value="Examinations">Examinations</option>
                    <option value="Admissions">Admissions</option>
                    <option value="Placement">Placement & Internships</option>
                    <option value="Hostel & Campus">Hostel & Campus</option>
                    <option value="Scholarships">Scholarships</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Academic Year</label>
                  <input
                    type="text"
                    value={academicYear}
                    placeholder="2025-2026"
                    onChange={(e) => setAcademicYear(e.target.value)}
                    disabled={isUploading}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Target Department</label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  disabled={isUploading}
                >
                  <option value="All Departments">All Departments (Institutional)</option>
                  <option value="Computer Science & Engineering">Computer Science & Engineering</option>
                  <option value="Electronics & Communication">Electronics & Communication</option>
                  <option value="Mechanical Engineering">Mechanical Engineering</option>
                  <option value="Civil Engineering">Civil Engineering</option>
                  <option value="Electrical & Electronics">Electrical & Electronics</option>
                </select>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="btn-modal-cancel"
                  disabled={isUploading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary-doc"
                  disabled={isUploading || !file}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="animate-spin" size={16} />
                      <span>Uploading & Queuing...</span>
                    </>
                  ) : (
                    <>
                      <UploadCloud size={16} />
                      <span>Upload & Ingest</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Chunks Inspector Drawer */}
      {selectedDoc && (
        <div className="modal-backdrop">
          <div className="chunks-drawer-card">
            <div className="modal-header">
              <div>
                <h3>Chunks & Vector Embeddings</h3>
                <p className="chunks-doc-title">{selectedDoc.title} ({selectedDoc.file_name})</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedDoc(null)}
                className="btn-modal-close"
              >
                <X size={18} />
              </button>
            </div>

            <div className="chunks-list-container">
              {isLoadingChunks ? (
                <div className="doc-loading">
                  <Loader2 className="animate-spin" size={24} />
                  <p>Loading chunks from PostgreSQL pgvector...</p>
                </div>
              ) : chunks.length === 0 ? (
                <div className="chunks-empty">
                  <p>No chunks generated for this document yet. Click 'Process' to trigger chunking and embedding.</p>
                </div>
              ) : (
                <div className="chunks-grid">
                  {chunks.map((chunk) => (
                    <article key={chunk.id} className="chunk-card">
                      <div className="chunk-header">
                        <span className="chunk-index-badge">Chunk #{chunk.chunk_index + 1}</span>
                        {chunk.section_title && (
                          <span className="chunk-section-tag">§ {chunk.section_title}</span>
                        )}
                        {chunk.page_number && (
                          <span className="chunk-page-tag">Pg {chunk.page_number}</span>
                        )}
                        <span className={`chunk-vector-badge ${chunk.has_embedding ? "active" : ""}`}>
                          {chunk.has_embedding ? "1536-dim pgvector" : "No Embedding"}
                        </span>
                      </div>
                      <p className="chunk-text">{chunk.content}</p>
                      <div className="chunk-footer">
                        <span>{chunk.content.length} characters</span>
                        <span>~{chunk.token_count || 0} tokens</span>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
