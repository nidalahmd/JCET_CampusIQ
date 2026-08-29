export interface SourceCitation {
  document_id: string;
  chunk_id: string;
  document_title: string;
  section_title: string | null;
  page_number: number | null;
  source_excerpt: string;
  relevance_score: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  latency_ms?: number;
  sources?: SourceCitation[];
}

export interface ChatRequestPayload {
  prompt: string;
  conversation_id?: string | null;
}

export interface ChatResponseData {
  conversation_id: string;
  message: ChatMessage;
  sources: SourceCitation[];
  latency_ms: number;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationFull {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}
