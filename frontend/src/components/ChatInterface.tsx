import {
  AlertCircle,
  ArrowRight,
  BookOpen,
  ChevronDown,
  ChevronRight,
  Clock,
  ExternalLink,
  FileText,
  HelpCircle,
  Layers,
  Loader2,
  MessageSquare,
  Plus,
  Send,
  Sparkles,
  Trash2,
  User as UserIcon,
} from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import type {
  ChatMessage,
  ConversationSummary,
  SourceCitation,
} from "../types/chat";

interface ChatInterfaceProps {
  initialPrompt?: string | null;
  onClearInitialPrompt?: () => void;
}

export function ChatInterface({ initialPrompt, onClearInitialPrompt }: ChatInterfaceProps) {
  const { token, user } = useAuth();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchConversations = async () => {
    if (!token) return;
    try {
      const convList = await api.getConversations(token);
      setConversations(convList);
    } catch (err: unknown) {
      if (err instanceof Error) console.error("Error fetching conversations:", err.message);
    }
  };

  const loadConversation = async (convId: string) => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const conv = await api.getConversation(convId, token);
      setActiveConvId(conv.id);
      setMessages(conv.messages);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setPrompt("");
    setError(null);
    inputRef.current?.focus();
  };

  const deleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!token || !confirm("Delete this conversation?")) return;
    try {
      await api.deleteConversation(convId, token);
      if (activeConvId === convId) {
        startNewChat();
      }
      await fetchConversations();
    } catch (err: unknown) {
      if (err instanceof Error) alert(err.message);
    }
  };

  const toggleSources = (msgId: string) => {
    setExpandedSources((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim() || !token || isSending) return;

    const userPrompt = textToSend.trim();
    setPrompt("");
    setError(null);
    setIsSending(true);

    // Optimistic user message update
    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: userPrompt,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await api.sendChatMessage(
        {
          prompt: userPrompt,
          conversation_id: activeConvId,
        },
        token
      );

      setActiveConvId(res.conversation_id);
      setMessages((prev) => [...prev.filter((m) => m.id !== tempUserMsg.id), tempUserMsg, res.message]);
      await fetchConversations();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to generate answer. Please try again.");
      }
    } finally {
      setIsSending(false);
    }
  };

  const onSubmitForm = (e: FormEvent) => {
    e.preventDefault();
    handleSendMessage(prompt);
  };

  useEffect(() => {
    fetchConversations();
  }, [token]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  // Handle initial prompt passed from Dashboard
  useEffect(() => {
    if (initialPrompt && initialPrompt.trim()) {
      handleSendMessage(initialPrompt);
      onClearInitialPrompt?.();
    }
  }, [initialPrompt]);

  const quickQuestions = [
    "What is the minimum attendance requirement at JCET?",
    "What are the passing marks and grading system for B.Tech?",
    "What are the working hours and book borrowing rules of the Central Library?",
    "What are the eligibility criteria for CSE campus placements?",
    "How is Continuous Internal Evaluation (CIE) calculated?",
    "What scholarships and fee waivers are offered at JCET?",
  ];

  return (
    <div className="chat-container-layout">
      {/* Sidebar: Conversation Threads */}
      <aside className="chat-sidebar">
        <div className="sidebar-header">
          <button
            type="button"
            onClick={startNewChat}
            className="btn-new-chat"
          >
            <Plus size={16} />
            <span>New Chat</span>
          </button>
        </div>

        <div className="conversations-list">
          <span className="sidebar-section-title">Recent Conversations</span>
          {conversations.length === 0 ? (
            <p className="no-chats-hint">No saved conversations</p>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                type="button"
                className={`conv-item-btn ${activeConvId === conv.id ? "active" : ""}`}
                onClick={() => loadConversation(conv.id)}
              >
                <MessageSquare size={15} className="conv-icon" />
                <div className="conv-text-group">
                  <span className="conv-title">{conv.title}</span>
                  <span className="conv-date">{new Date(conv.updated_at).toLocaleDateString()}</span>
                </div>
                <button
                  type="button"
                  className="btn-conv-delete"
                  onClick={(e) => deleteConversation(conv.id, e)}
                  title="Delete chat"
                >
                  <Trash2 size={13} />
                </button>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Main Chat Stream Area */}
      <main className="chat-main-panel">
        <header className="chat-panel-header">
          <div className="chat-header-title">
            <div className="chat-bot-avatar">
              <Sparkles size={18} />
            </div>
            <div>
              <h2>JCET CampusIQ Intelligence</h2>
              <span className="chat-sub-badge">Grounded RAG Engine Active</span>
            </div>
          </div>
        </header>

        {/* Message Stream */}
        <div className="chat-messages-scroll">
          {isLoading ? (
            <div className="chat-loading-thread">
              <Loader2 className="animate-spin" size={26} />
              <span>Loading conversation...</span>
            </div>
          ) : messages.length === 0 ? (
            <div className="chat-empty-welcome">
              <div className="empty-spark-icon">
                <Sparkles size={36} />
              </div>
              <h3>What would you like to know about JCET?</h3>
              <p>
                Ask questions about official college policies, academic regulations, examination schedules, library rules, CSE department details, or admissions.
              </p>

              <div className="empty-suggestions-group">
                <span className="suggestions-prompt-label">Quick Suggestions:</span>
                <div className="empty-chips-grid">
                  {quickQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="empty-suggestion-chip"
                      onClick={() => handleSendMessage(q)}
                    >
                      <span>{q}</span>
                      <ArrowRight size={14} />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="chat-bubbles-flow">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`chat-bubble-row ${msg.role === "user" ? "user-row" : "assistant-row"}`}
                >
                  <div className="bubble-avatar">
                    {msg.role === "user" ? <UserIcon size={16} /> : <Sparkles size={16} />}
                  </div>

                  <div className="bubble-content-wrapper">
                    <div className="bubble-card">
                      <p className="bubble-text">{msg.content}</p>

                      {msg.role === "assistant" && msg.latency_ms !== undefined && (
                        <div className="bubble-meta-footer">
                          <span className="meta-latency">
                            <Clock size={12} />
                            {msg.latency_ms}ms response
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Expandable Citations / Sources Panel */}
                    {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                      <div className="sources-container">
                        <button
                          type="button"
                          className="btn-toggle-sources"
                          onClick={() => toggleSources(msg.id)}
                        >
                          {expandedSources[msg.id] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                          <BookOpen size={14} />
                          <span>
                            {msg.sources.length} Grounded Source{msg.sources.length > 1 ? "s" : ""} & Citation{msg.sources.length > 1 ? "s" : ""}
                          </span>
                        </button>

                        {expandedSources[msg.id] && (
                          <div className="sources-drawer-list">
                            {msg.sources.map((src, sIdx) => (
                              <article key={sIdx} className="source-citation-card">
                                <div className="citation-header">
                                  <FileText size={14} className="citation-icon" />
                                  <strong className="citation-title">{src.document_title}</strong>
                                  {src.page_number && (
                                    <span className="citation-page">Page {src.page_number}</span>
                                  )}
                                  {src.relevance_score > 0 && (
                                    <span className="citation-score">
                                      {Math.round(src.relevance_score * 100)}% Match
                                    </span>
                                  )}
                                </div>
                                <p className="citation-excerpt">"{src.source_excerpt}"</p>
                              </article>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isSending && (
                <div className="chat-bubble-row assistant-row">
                  <div className="bubble-avatar">
                    <Sparkles size={16} />
                  </div>
                  <div className="bubble-content-wrapper">
                    <div className="bubble-card loading-bubble">
                      <Loader2 className="animate-spin" size={18} />
                      <span>Retrieving pgvector context & generating grounded answer...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar */}
        <footer className="chat-input-footer">
          {error && (
            <div className="chat-error-banner">
              <AlertCircle size={15} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={onSubmitForm} className="chat-input-form">
            <input
              ref={inputRef}
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask anything about JCET academics, exams, regulations, library, departments..."
              disabled={isSending}
              autoFocus
            />
            <button
              type="submit"
              className="btn-send-chat"
              disabled={isSending || !prompt.trim()}
              title="Send question"
            >
              {isSending ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
            </button>
          </form>
        </footer>
      </main>
    </div>
  );
}
