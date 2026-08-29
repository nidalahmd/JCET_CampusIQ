# JCET CampusIQ

## Intelligent Campus Knowledge & Retrieval System

**Document Type:** Software Product Specification
**Version:** 1.0
**Status:** Development Specification
**Institution:** Jawaharlal College of Engineering and Technology (JCET), Lakkidi, Palakkad, Kerala
**System Type:** Full-Stack RAG-Based Institutional Knowledge Platform

---

# 1. Product Overview

**JCET CampusIQ** is a production-grade Retrieval-Augmented Generation (RAG) platform designed specifically for Jawaharlal College of Engineering and Technology (JCET), Lakkidi, Palakkad.

The system enables students, faculty, and authorized administrative users to interact with official institutional information through natural-language queries.

CampusIQ retrieves information from an indexed collection of official JCET documents and uses the retrieved evidence as the sole factual basis for generating responses.

The system must prioritize:

* Accuracy
* Source traceability
* Strict grounding
* Security
* Role-based access
* Document versioning
* Reliable retrieval
* Transparent citations
* Graceful handling of unknown information

The system must **never fabricate institutional information**.

---

# 2. Core Product Principles

## 2.1 Strict Grounding

All factual answers must be generated exclusively from retrieved official JCET document content.

The LLM must not use unsupported assumptions, general knowledge, or fabricated institutional information.

---

## 2.2 Zero Hardcoded Knowledge

Institutional information must not be hardcoded into frontend components, API routes, prompts, or application logic.

Examples of information that must come from documents:

* Fees
* Eligibility requirements
* Exam dates
* Attendance requirements
* Faculty information
* Hostel rules
* Scholarship criteria
* Academic regulations
* Department information
* Placement statistics
* Event dates

---

## 2.3 Evidence-Based Answers

Every factual answer must provide verifiable source information.

Each citation should contain, where available:

* Document title
* File name
* Document category
* Academic year
* Version
* Section title
* Page number
* Retrieval/relevance score
* Match confidence
* Source excerpt

---

## 2.4 Unknown Information Protocol

If the retrieval system cannot find sufficiently relevant official evidence, the system must not generate an answer based on assumptions.

Instead, it must clearly communicate that the required information could not be verified from the available official JCET documents.

Example:

> "I couldn't find reliable information about this in the available official JCET documents."

The system may optionally suggest related available information or recommend contacting the relevant department.

---

## 2.5 Document Authority

Only documents uploaded through the authorized institutional document-management workflow should be treated as authoritative knowledge sources.

Each document must have metadata describing:

* Category
* Department
* Academic year
* Version
* Status
* Upload timestamp
* Uploader

---

# 3. Target Users

## 3.1 Student / Public User

Students and public users can:

* Register
* Login
* Manage their profile
* Change password
* Ask campus-related questions
* Search institutional knowledge
* Conduct multi-turn conversations
* View conversation history
* Inspect source citations
* Copy answers
* Provide feedback
* Submit comments
* View scholarship eligibility assessments

---

## 3.2 JCET Administrator

Administrators can:

* Upload documents
* Parse documents
* Process documents
* Index documents
* Re-index documents
* Archive documents
* Delete documents
* Assign document metadata
* Manage document versions
* Monitor RAG performance
* Monitor system latency
* Analyze feedback
* Identify knowledge gaps
* Review audit logs

---

# 4. Knowledge Domains

The system must support at least the following institutional knowledge domains.

## 4.1 Admissions

Example:

> What are the eligibility criteria and documents required for B.Tech CSE admission?

---

## 4.2 Academics & Syllabus

Example:

> What are the passing criteria for KTU semester examinations?

---

## 4.3 Examinations & Academic Calendar

Example:

> When do the end-semester examinations begin?

---

## 4.4 Fees & Payments

Example:

> What is the tuition fee refund policy for B.Tech programs?

---

## 4.5 Hostel & Housing

Example:

> What are the hostel entry timings and mess regulations?

---

## 4.6 Library

Example:

> How many books can a B.Tech student borrow at a time?

---

## 4.7 Placement Cell

Example:

> What placement training programs are available for Data Science students?

---

## 4.8 Scholarships & Financial Aid

Example:

> What are the criteria for MCM and government scholarships?

---

## 4.9 Departments & Faculty

Example:

> Who is the HOD of the Computer Science and Engineering department?

---

## 4.10 Code of Conduct

Example:

> What attendance percentage is required to write end-semester examinations?

---

## 4.11 Events & Hackathons

Example:

> When is the annual college technical fest scheduled?

---

# 5. High-Level System Architecture

```text
                    OFFICIAL JCET DOCUMENTS
              PDF / DOCX / TXT / MARKDOWN
                            │
                            ▼
                  ┌───────────────────┐
                  │ Document Parser   │
                  │ Text + Metadata   │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Header-Aware      │
                  │ Chunker           │
                  │ ~650 chars        │
                  │ ~120 overlap      │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Embedding Engine  │
                  └─────────┬─────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │ PostgreSQL + pgvector      │
              │                            │
              │ Vector Search              │
              │ Full-Text Search           │
              └────────────┬───────────────┘
                           │
                           ▼
                  ┌───────────────────┐
                  │ Hybrid Retriever  │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Candidate         │
                  │ Re-ranker         │
                  │ Top 3–8 chunks    │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Context & Prompt  │
                  │ Assembler         │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Gemini Provider   │
                  │ AI Abstraction    │
                  └─────────┬─────────┘
                            │
                            ▼
            ┌────────────────────────────────┐
            │ Grounded Answer                │
            │ + Citations                    │
            │ + Confidence                    │
            │ + Telemetry                    │
            └────────────────────────────────┘
```

---

# 6. Technical Stack

## 6.1 Frontend

* React / Next.js
* TypeScript
* Tailwind CSS
* Lucide React
* React Hook Form
* Zod
* Zustand
* TanStack Query
* Axios
* Recharts

The frontend must be responsive and optimized for:

* Desktop
* Tablet
* Mobile

---

# 6.2 Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* PostgreSQL
* pgvector
* PyPDF / pdfplumber
* python-docx
* LangChain utilities where appropriate
* Pytest

---

# 6.3 AI Layer

Primary AI provider:

**Google Gemini API**

The application must use an abstraction layer rather than coupling the RAG service directly to Gemini.

Example architecture:

```text
RAG Service
     │
     ▼
AIProvider Interface
     │
     ├── GeminiProvider
     │
     └── FutureProvider
```

This allows another LLM provider to be introduced without rewriting the RAG pipeline.

---

# 7. RAG Architecture

## 7.1 Document Ingestion

Supported formats:

* PDF
* DOCX
* TXT
* Markdown

Each document must first pass through a parser.

The parser must extract:

* Text
* Page number where available
* Heading/section information
* File metadata
* Document metadata

---

# 7.2 Header-Aware Chunking

Documents must be divided into semantically meaningful chunks.

Target configuration:

```text
Chunk size: approximately 650 characters
Overlap: approximately 120 characters
```

Chunking must attempt to preserve:

* Headings
* Paragraph boundaries
* Lists
* Tables where possible
* Related contextual information

Each chunk must maintain its original document and page relationship.

---

# 7.3 Embeddings

Each chunk must be converted into a vector embedding.

Embeddings must be stored in PostgreSQL using `pgvector`.

The embedding provider must be abstracted behind an embedding interface.

---

# 7.4 Hybrid Retrieval

The retrieval engine must combine:

### Vector Search

Uses semantic similarity between the user query and document chunks.

### Keyword Search

Uses PostgreSQL full-text search or equivalent keyword matching.

### Metadata Filtering

Retrieval should support filtering by:

* Category
* Department
* Academic year
* Document version
* Document status

---

# 7.5 Candidate Re-ranking

The initial retrieval stage may return a larger candidate set.

The re-ranking layer must identify approximately:

```text
Top 3–8 most relevant chunks
```

The final context should prioritize:

1. Semantic relevance
2. Keyword relevance
3. Document authority
4. Metadata match
5. Academic-year relevance
6. Version validity

---

# 7.6 Context Assembly

Only the final selected chunks should be provided to the generation model.

The context assembler must include source identifiers so that generated claims can be associated with their supporting evidence.

---

# 8. Grounded Generation Rules

The RAG prompt must enforce the following rules:

1. Use only supplied retrieved context.
2. Do not invent facts.
3. Do not infer unsupported institutional policies.
4. Do not treat model knowledge as institutional knowledge.
5. Do not fabricate citations.
6. Clearly distinguish between information explicitly stated in documents and information that cannot be verified.
7. If evidence is insufficient, use the unknown-information fallback.
8. Cite the source supporting each factual answer.
9. Prefer newer valid document versions where applicable.
10. Do not use archived documents as authoritative sources unless explicitly requested or configured.

---

# 9. Citation System

Every factual response must include source citations.

A citation should expose:

```text
Document:
JCET Academic Regulations 2026

Section:
Attendance Requirements

Page:
42

Confidence:
94%

Excerpt:
"...students are required to maintain..."
```

The UI must allow the user to inspect the citation without leaving the conversation.

---

# 10. Confidence System

The application must calculate a retrieval confidence/relevance score.

The score must be based on retrieval evidence and must not be fabricated by the LLM.

Example classification:

```text
90–100% → Very High
75–89%  → High
60–74%  → Moderate
Below 60% → Low / Insufficient
```

The exact thresholds should be configurable.

Low-confidence retrievals should trigger additional validation or the unknown-information protocol.

---

# 11. Database Architecture

The system uses PostgreSQL with the `pgvector` extension.

## 11.1 users

```text
id
name
email
password_hash
role
created_at
updated_at
```

Roles:

```text
student
admin
```

---

## 11.2 documents

```text
id
title
file_name
file_type
storage_path
category
department
academic_year
processing_status
version
uploaded_by
created_at
updated_at
```

Processing states:

```text
UPLOADED
PROCESSING
PROCESSED
FAILED
ARCHIVED
```

---

## 11.3 document_chunks

```text
id
document_id
version_id
chunk_index
content
token_count
page_number
section_title
metadata
embedding
created_at
```

`embedding` must use PostgreSQL `vector`.

---

## 11.4 conversations

```text
id
user_id
title
created_at
updated_at
```

---

## 11.5 messages

```text
id
conversation_id
role
content
retrieval_metadata
latency_ms
created_at
```

Roles:

```text
user
assistant
```

---

## 11.6 message_sources

```text
id
message_id
document_id
chunk_id
relevance_score
page_number
source_excerpt
```

---

## 11.7 feedback

```text
id
user_id
message_id
rating
comment
created_at
```

Ratings:

```text
positive
negative
```

---

## 11.8 questions

```text
id
user_id
message_id
category
intent
resolved
retrieval_score
created_at
```

---

## 11.9 audit_logs

```text
id
user_id
action
resource_type
resource_id
created_at
```

Administrative operations must generate audit records.

---

# 12. Authentication & Authorization

## 12.1 Registration

Users must be able to create accounts using:

* Name
* Email
* Password

Input validation must be performed using Pydantic/Zod.

---

## 12.2 Password Security

Passwords must never be stored as plaintext.

Use a modern password hashing algorithm such as:

* Argon2id
* bcrypt

---

## 12.3 JWT Authentication

The backend must issue JWT access tokens after successful authentication.

Protected API routes must validate tokens before processing requests.

---

## 12.4 Role-Based Access Control

Student users must not be able to access administrative APIs.

Administrative endpoints must verify:

```text
authenticated user
+
admin role
```

---

# 13. Document Management

Administrators must have a document management interface.

Supported operations:

* Upload
* View
* Process
* Re-process
* Re-index
* Archive
* Delete
* Update metadata
* View processing status
* View version history

---

# 14. Document Processing Pipeline

```text
Upload
   │
   ▼
Validate File
   │
   ▼
Create Document Record
   │
   ▼
PROCESSING
   │
   ▼
Parse Document
   │
   ▼
Extract Metadata
   │
   ▼
Chunk Text
   │
   ▼
Generate Embeddings
   │
   ▼
Store Chunks + Vectors
   │
   ▼
Create Search Index
   │
   ▼
PROCESSED
```

If processing fails:

```text
PROCESSING → FAILED
```

The failure reason must be logged.

---

# 15. Background Processing

Document indexing should not block the HTTP request for large files.

The architecture should support background processing through a queue or worker mechanism.

The implementation must allow future migration to:

* Celery
* Redis Queue
* Dramatiq
* Cloud task workers

without redesigning the ingestion service.

---

# 16. Chat System

Students should have a conversational interface.

Features:

* New conversation
* Conversation title
* Multi-turn messages
* Message timestamps
* Streaming assistant responses where supported
* Source citations
* Citation drawer
* Copy answer
* Feedback
* Conversation history
* Error handling

---

# 17. Multi-Language Support

The system should support:

* English
* Malayalam

The RAG architecture must preserve grounding regardless of query language.

Example:

```text
User asks in Malayalam
        ↓
Retrieve relevant JCET documents
        ↓
Generate grounded response
        ↓
Respond in Malayalam
```

The language conversion must not introduce unsupported facts.

---

# 18. Scholarship Eligibility System

Students may optionally provide:

* Academic information
* Qualification information
* Income-related information
* Relevant profile details

The system can assess potential scholarship eligibility against official scholarship criteria contained in the knowledge base.

The result must clearly distinguish:

```text
Eligible
Potentially Eligible
Not Eligible
Insufficient Information
```

Eligibility must always be based on retrieved official criteria.

The system must not claim eligibility when required information is unavailable.

---

# 19. Admin Analytics

The administrator dashboard must provide system telemetry.

Metrics should include:

* Total queries
* Queries per day
* Average RAG latency
* Retrieval scores
* Low-confidence queries
* Unresolved queries
* Positive feedback rate
* Negative feedback rate
* Document processing status
* Most queried categories
* Knowledge gaps

---

# 20. Knowledge Gap Detection

The system must identify questions where:

* Retrieval confidence is low
* No relevant source exists
* Users repeatedly ask similar unanswered questions
* Negative feedback is frequent
* Retrieved sources are insufficient

Administrators should be able to review these questions and determine whether additional official documentation is required.

---

# 21. Audit Logging

The system must record administrative actions.

Examples:

```text
DOCUMENT_UPLOADED
DOCUMENT_UPDATED
DOCUMENT_REINDEXED
DOCUMENT_ARCHIVED
DOCUMENT_DELETED
USER_ROLE_CHANGED
```

Audit records should include:

* User
* Action
* Resource type
* Resource ID
* Timestamp

---

# 22. API Architecture

FastAPI routes should remain thin.

Business logic must live inside service modules.

Recommended structure:

```text
API Router
   ↓
Service Layer
   ↓
Repository / Database
```

RAG requests:

```text
Chat Router
   ↓
Chat Service
   ↓
Retrieval Service
   ↓
Re-ranking Service
   ↓
RAG Service
   ↓
AI Provider
```

---

# 23. Recommended API Modules

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/change-password
GET  /api/auth/me
```

## Chat

```text
POST /api/chat/query
GET  /api/chat/conversations
GET  /api/chat/conversations/{id}
POST /api/chat/feedback
```

## Documents

```text
POST   /api/documents
GET    /api/documents
GET    /api/documents/{id}
POST   /api/documents/{id}/process
POST   /api/documents/{id}/reindex
PATCH  /api/documents/{id}
POST   /api/documents/{id}/archive
DELETE /api/documents/{id}
```

## Admin Analytics

```text
GET /api/admin/analytics/overview
GET /api/admin/analytics/queries
GET /api/admin/analytics/latency
GET /api/admin/analytics/knowledge-gaps
GET /api/admin/audit-logs
```

---

# 24. Frontend Application Structure

Recommended structure:

```text
frontend/
└── src/
    ├── components/
    │   ├── layout/
    │   ├── chat/
    │   ├── citations/
    │   ├── documents/
    │   ├── analytics/
    │   └── common/
    │
    ├── pages/
    │   ├── Landing
    │   ├── Login
    │   ├── Register
    │   ├── Dashboard
    │   ├── Chat
    │   ├── Settings
    │   └── Admin
    │
    ├── services/
    │   └── api/
    │
    ├── store/
    │
    ├── hooks/
    │
    ├── types/
    │
    └── utils/
```

---

# 25. Backend Repository Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   ├── conversations.py
│   │   ├── analytics.py
│   │   └── admin.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── ingestion_service.py
│   │   ├── retrieval_service.py
│   │   ├── rag_service.py
│   │   └── analytics_service.py
│   │
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   ├── prompt_builder.py
│   │   └── citation_engine.py
│   │
│   ├── ingestion/
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── txt_parser.py
│   │   └── markdown_parser.py
│   │
│   └── providers/
│       ├── base.py
│       ├── gemini.py
│       └── embeddings.py
│
├── data/
│   ├── sample_docs/
│   └── uploads/
│
├── tests/
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

# 26. Root Repository Structure

```text
jcet-campusiq/
│
├── backend/
├── frontend/
├── docs/
├── README.md
├── SPEC.md
├── .gitignore
└── start.bat
```

---

# 27. Environment Configuration

Secrets must never be committed to Git.

The project must provide:

```text
.env.example
```

Example configuration categories:

```text
DATABASE_URL
JWT_SECRET_KEY
GEMINI_API_KEY
EMBEDDING_API_KEY
UPLOAD_DIRECTORY
CORS_ORIGINS
```

Actual secret values must remain in `.env`.

---

# 28. Database Hosting Architecture

The development environment uses an external PostgreSQL provider with the `pgvector` extension enabled. Supabase, Neon, or another PostgreSQL provider with vector support may be used.

The architecture should allow additional services such as Redis or workers to be added later.

---

# 29. Security Requirements

The system must implement:

* Password hashing
* JWT authentication
* Role-based authorization
* Request validation
* File type validation
* File size limits
* Secure file storage
* CORS configuration
* SQL injection protection through ORM/query parameterization
* Rate limiting where appropriate
* Audit logging
* Secret management
* Secure error responses

Internal stack traces must not be returned to public users.

---

# 30. File Upload Security

Uploaded files must be validated before processing.

Validation must include:

* Allowed extensions
* MIME type
* File size
* Filename sanitization

Supported extensions:

```text
.pdf
.docx
.txt
.md
```

Invalid files must be rejected.

---

# 31. Testing Requirements

The backend must include automated tests.

## Unit Tests

Test:

* Authentication
* Password hashing
* JWT validation
* Document parsing
* Chunking
* Retrieval
* Re-ranking
* Citation generation
* Unknown-question handling

## Integration Tests

Test:

* Database operations
* Document ingestion
* Vector retrieval
* API authentication
* Chat pipeline

## End-to-End Tests

Test:

```text
Register
   ↓
Login
   ↓
Ask Question
   ↓
Retrieve Document
   ↓
Generate Grounded Answer
   ↓
Display Citation
   ↓
Submit Feedback
```

---

# 32. RAG Evaluation

The system should maintain a small evaluation dataset containing representative JCET questions and expected source documents.

Evaluation metrics should include:

* Retrieval precision
* Retrieval recall
* Citation accuracy
* Answer groundedness
* Unknown-answer accuracy
* Average latency

The system should prioritize citation correctness over fluent but unsupported answers.

---

# 33. Error Handling

The application must gracefully handle:

### Invalid authentication

Return an appropriate authentication error.

### Invalid document

Return a clear document validation error.

### Parsing failure

Mark document as `FAILED` and store the failure reason.

### Embedding failure

Do not mark the document as successfully indexed.

### Retrieval failure

Return a controlled error or unknown-information response.

### LLM failure

Do not fabricate a response.

### Database failure

Return a generic server error while logging the internal failure.

---

# 34. Performance Requirements

Target performance:

```text
Authentication API:
< 500 ms under normal conditions

Database retrieval:
< 500 ms target

RAG retrieval + processing:
< 2 seconds target where infrastructure permits

Complete AI response:
Dependent on provider/network latency
```

Actual production performance must be measured through telemetry rather than assumed.

---

# 35. Observability

The backend should record:

* Request latency
* Retrieval latency
* Embedding latency
* LLM latency
* Database latency
* Retrieval scores
* Number of retrieved chunks
* Final context size
* Query category
* Resolution status

Sensitive user information and secrets must not be logged.

---

# 36. User Experience Requirements

The interface should have a clean enterprise-style design.

Primary experience:

```text
                    JCET CampusIQ

        "Ask anything about JCET..."

                 [ Ask Question ]

------------------------------------------------

Assistant Response

Answer...

Sources
────────────────────────────
📄 Academic Regulations
Page 42
Confidence: 94%

[ View Source ]
------------------------------------------------
```

The interface should emphasize:

* Trust
* Simplicity
* Readability
* Source transparency

---

# 37. Admin Dashboard

The administrator dashboard should contain:

### Overview

* Total documents
* Processed documents
* Failed documents
* Total queries
* Average latency
* Unresolved questions

### Documents

* Upload
* Search
* Filter
* Process
* Re-index
* Archive
* Delete

### Analytics

* Query volume
* Retrieval confidence
* Latency
* Feedback
* Knowledge gaps

### Audit Logs

* Administrative actions
* User
* Timestamp
* Resource

---

# 38. Development Phases

## Phase 1 — Foundation

Tasks:

* [ ] Initialize monorepo
* [ ] Configure backend
* [ ] Configure frontend
* [ ] Configure PostgreSQL
* [ ] Enable pgvector
* [ ] Configure SQLAlchemy
* [ ] Configure Alembic
* [ ] Create database models
* [ ] Configure external PostgreSQL environment

---

## Phase 2 — Authentication

Tasks:

* [ ] User registration
* [ ] Login
* [ ] Password hashing
* [ ] JWT authentication
* [ ] Protected routes
* [ ] Role-based access control
* [ ] Profile management
* [ ] Password change

---

## Phase 3 — Document Ingestion

Tasks:

* [ ] PDF parser
* [ ] DOCX parser
* [ ] TXT parser
* [ ] Markdown parser
* [ ] Metadata extraction
* [ ] Header-aware chunking
* [ ] Embedding generation
* [ ] Vector storage
* [ ] Processing status tracking
* [ ] Background processing

---

## Phase 4 — Retrieval

Tasks:

* [ ] Vector search
* [ ] PostgreSQL full-text search
* [ ] Hybrid retrieval
* [ ] Metadata filtering
* [ ] Candidate generation
* [ ] Re-ranking
* [ ] Confidence calculation

---

## Phase 5 — Grounded RAG

Tasks:

* [ ] Context assembler
* [ ] Grounding prompt
* [ ] Gemini provider
* [ ] AI abstraction layer
* [ ] Citation engine
* [ ] Unknown-question fallback
* [ ] Latency telemetry

---

## Phase 6 — Student Interface

Tasks:

* [ ] Dashboard
* [ ] Chat interface
* [ ] Conversation history
* [ ] Multi-turn chat
* [ ] Streaming responses
* [ ] Citation drawer
* [ ] Source excerpts
* [ ] Copy response
* [ ] Feedback system
* [ ] Malayalam support

---

## Phase 7 — Admin System

Tasks:

* [ ] Admin dashboard
* [ ] Document management
* [ ] Document versioning
* [ ] Processing controls
* [ ] Analytics
* [ ] Knowledge-gap detection
* [ ] Audit logs

---

## Phase 8 — Testing & Deployment

Tasks:

* [ ] Unit tests
* [ ] Integration tests
* [ ] End-to-end tests
* [ ] RAG evaluation
* [ ] Security testing
* [ ] Performance testing
* [ ] Production infrastructure configuration
* [ ] Production environment configuration
* [ ] Deployment documentation

---

# 39. Definition of Done

The project is considered production-ready only when all of the following are satisfied:

* [ ] Users can securely register and login.
* [ ] JWT authentication is implemented.
* [ ] Admin and student permissions are enforced.
* [ ] Administrators can upload official JCET documents.
* [ ] PDF, DOCX, TXT and Markdown documents can be processed.
* [ ] Documents are chunked with source metadata.
* [ ] Embeddings are stored in pgvector.
* [ ] Hybrid retrieval works.
* [ ] Relevant chunks are re-ranked.
* [ ] Gemini receives only retrieved context.
* [ ] Unsupported information is rejected.
* [ ] Unknown questions trigger the fallback protocol.
* [ ] Answers contain source citations.
* [ ] Citations contain page/section information where available.
* [ ] Users can inspect source excerpts.
* [ ] Conversation history works.
* [ ] Feedback works.
* [ ] Admin analytics work.
* [ ] Knowledge gaps can be identified.
* [ ] Administrative actions are audited.
* [ ] Automated tests pass.
* [ ] Hosted PostgreSQL development works.
* [ ] Production configuration is documented.
* [ ] No API keys or secrets are committed to the repository.

---

# 40. Non-Functional Requirements

The application must be:

### Reliable

The system must fail safely rather than provide unsupported information.

### Maintainable

Business logic must remain modular and separated from API routes.

### Scalable

The architecture must support increasing numbers of:

* Users
* Documents
* Chunks
* Queries

### Secure

Authentication, authorization, file handling, secrets, and administrative operations must be protected.

### Observable

RAG and application performance must be measurable.

### Extensible

The architecture must allow future:

* AI providers
* Embedding providers
* Search engines
* Background workers
* Storage providers

without major architectural changes.

---

# 41. Final System Principle

The most important rule in JCET CampusIQ is:

> **If the system cannot verify an answer from official JCET documents, it must not answer as though the information is known.**

CampusIQ is not intended to be a general-purpose chatbot.

It is an **official-document-grounded institutional knowledge system**.

The priority order is:

```text
Accuracy
   ↓
Evidence
   ↓
Traceability
   ↓
Security
   ↓
Reliability
   ↓
User Experience
   ↓
Generative Fluency
```

A concise, evidence-backed answer with a clear "information not found" response is preferable to a fluent but unsupported answer.

---

# 42. Initial Project Acceptance Checklist

* [ ] Repository initialized
* [ ] Backend operational
* [ ] Frontend operational
* [ ] PostgreSQL operational
* [ ] pgvector operational
* [ ] Authentication operational
* [ ] Role authorization operational
* [ ] Document upload operational
* [ ] Document parser operational
* [ ] Chunking operational
* [ ] Embedding pipeline operational
* [ ] Hybrid retrieval operational
* [ ] Re-ranking operational
* [ ] Gemini integration operational
* [ ] Strict grounding operational
* [ ] Citation engine operational
* [ ] Unknown-question fallback operational
* [ ] Student chat operational
* [ ] Malayalam query/response support operational
* [ ] Feedback operational
* [ ] Admin dashboard operational
* [ ] Analytics operational
* [ ] Knowledge-gap detection operational
* [ ] Audit logging operational
* [ ] Automated tests passing
* [ ] Database environment operational
* [ ] Production deployment configuration documented

---

**End of Specification**

**Project:** JCET CampusIQ
**Version:** 1.0
**Status:** Production Development Specification
