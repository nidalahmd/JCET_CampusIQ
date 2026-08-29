export type ProcessingStatus = "UPLOADED" | "PROCESSING" | "PROCESSED" | "FAILED" | "ARCHIVED";

export interface DocumentItem {
  id: string;
  title: string;
  file_name: string;
  file_type: string;
  storage_path: string;
  category: string | null;
  department: string | null;
  academic_year: string | null;
  processing_status: ProcessingStatus;
  version: number;
  uploaded_by: string | null;
  chunks_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  token_count: number | null;
  page_number: number | null;
  section_title: string | null;
  chunk_metadata: Record<string, any> | null;
  has_embedding: boolean;
  created_at: string;
}

export interface DocumentUploadPayload {
  file: File;
  title: string;
  category?: string;
  department?: string;
  academic_year?: string;
}
