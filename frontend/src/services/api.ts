import type {
  ChangePasswordPayload,
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  UpdateProfilePayload,
  User,
} from "../types/auth";
import type {
  ChatRequestPayload,
  ChatResponseData,
  ConversationFull,
  ConversationSummary,
} from "../types/chat";
import type {
  DocumentChunk,
  DocumentItem,
  DocumentListResponse,
  DocumentUploadPayload,
} from "../types/document";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errorMessage = `HTTP error ${response.status}`;
    try {
      const errorData = await response.json();
      if (typeof errorData.detail === "string") {
        errorMessage = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((d: { msg?: string }) => d.msg || "Validation error").join(", ");
      } else if (errorData.message) {
        errorMessage = errorData.message;
      }
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new ApiError(errorMessage, response.status);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

export const api = {
  // Auth Endpoints
  async register(payload: RegisterPayload): Promise<TokenResponse> {
    return request<TokenResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async login(payload: LoginPayload): Promise<TokenResponse> {
    return request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getMe(token: string): Promise<User> {
    return request<User>("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async updateProfile(payload: UpdateProfilePayload, token: string): Promise<User> {
    return request<User>("/api/auth/me", {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
  },

  async changePassword(payload: ChangePasswordPayload, token: string): Promise<{ status: string; message: string }> {
    return request<{ status: string; message: string }>("/api/auth/change-password", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
  },

  async checkAdmin(token: string): Promise<{ status: string; message: string; admin: User }> {
    return request<{ status: string; message: string; admin: User }>("/api/auth/admin-check", {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  // Document Endpoints
  async uploadDocument(payload: DocumentUploadPayload, token: string): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("file", payload.file);
    formData.append("title", payload.title);
    if (payload.category) formData.append("category", payload.category);
    if (payload.department) formData.append("department", payload.department);
    if (payload.academic_year) formData.append("academic_year", payload.academic_year);

    return request<DocumentItem>("/api/documents", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
  },

  async getDocuments(
    token: string,
    filters?: { category?: string; department?: string; status?: string }
  ): Promise<DocumentListResponse> {
    const params = new URLSearchParams();
    if (filters?.category) params.append("category", filters.category);
    if (filters?.department) params.append("department", filters.department);
    if (filters?.status) params.append("status", filters.status);

    const queryStr = params.toString() ? `?${params.toString()}` : "";
    return request<DocumentListResponse>(`/api/documents${queryStr}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async getDocument(id: string, token: string): Promise<DocumentItem> {
    return request<DocumentItem>(`/api/documents/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async getDocumentChunks(id: string, token: string): Promise<DocumentChunk[]> {
    return request<DocumentChunk[]>(`/api/documents/${id}/chunks`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async processDocument(id: string, token: string): Promise<DocumentItem> {
    return request<DocumentItem>(`/api/documents/${id}/process`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async reindexDocument(id: string, token: string): Promise<DocumentItem> {
    return request<DocumentItem>(`/api/documents/${id}/reindex`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async archiveDocument(id: string, token: string): Promise<DocumentItem> {
    return request<DocumentItem>(`/api/documents/${id}/archive`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async deleteDocument(id: string, token: string): Promise<void> {
    return request<void>(`/api/documents/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  // Chat Endpoints
  async sendChatMessage(payload: ChatRequestPayload, token: string): Promise<ChatResponseData> {
    return request<ChatResponseData>("/api/chat", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
  },

  async getConversations(token: string): Promise<ConversationSummary[]> {
    return request<ConversationSummary[]>("/api/chat/conversations", {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async getConversation(id: string, token: string): Promise<ConversationFull> {
    return request<ConversationFull>(`/api/chat/conversations/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async deleteConversation(id: string, token: string): Promise<void> {
    return request<void>(`/api/chat/conversations/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  // Health Endpoints
  async checkHealth(): Promise<{ status: string; service: string }> {
    return request<{ status: string; service: string }>("/api/health");
  },

  async checkDbHealth(): Promise<{ status: string; database: string; pgvector: string }> {
    return request<{ status: string; database: string; pgvector: string }>("/api/health/db");
  },
};
