# JCET CampusIQ

**AI-powered institutional knowledge assistant for Jawaharlal College of Engineering and Technology (JCET).**

JCET CampusIQ is a Retrieval-Augmented Generation (RAG) platform designed to help students and staff find reliable information from official institutional documents through grounded, source-aware responses.

## 🎯 Problem Statement

Students and staff often need to search through scattered college documents to find information about academics, examinations, admissions, regulations, library rules, and other institutional policies. Traditional document searching can be time-consuming and may make it difficult to identify the exact official source for an answer.

JCET CampusIQ addresses this problem by providing a centralized AI-powered institutional knowledge platform. It uses Retrieval-Augmented Generation (RAG) and semantic search to retrieve relevant information from official JCET documents and provide source-grounded answers with citations. This helps users find reliable institutional information faster while keeping the factual foundation tied to approved documents.

## 🌐 Live Application

**Frontend:** https://jcet-campus-iq.vercel.app/

**Backend API:** https://jcet-campusiq-backend.onrender.com/

**API Documentation:** https://jcet-campusiq-backend.onrender.com/docs

**GitHub Repository:** https://github.com/nidalahmd/JCET_CampusIQ

## ✨ Key Features

- 🤖 AI-powered institutional question answering
- 🔎 Retrieval-Augmented Generation (RAG)
- 📚 Document-based knowledge retrieval
- 🔗 Source-grounded responses and citations
- 🛡️ Role-based access control
- 🗂️ Institutional document management
- 🧠 Semantic search with PostgreSQL and pgvector
- ❤️ Backend and database health monitoring
- 🔐 Environment-based configuration

## 🛠️ Tech Stack

### Frontend
- React
- TypeScript
- Vite
- CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- Alembic
- Uvicorn

### Database
- PostgreSQL
- pgvector

### AI / RAG
- Retrieval-Augmented Generation
- Vector-based semantic retrieval
- Gemini

### Deployment
- Vercel — Frontend
- Render — Backend
- GitHub — Source Code

## 📸 Screenshots

### 🏠 Home / Landing Page

The main JCET CampusIQ landing page introduces the institutional knowledge platform and provides access to the AI assistant and workspace.

![JCET CampusIQ Home Page](screenshots/home.png)

### 💬 Ask CampusIQ

The AI question-answering interface where students can ask questions about official JCET academic, examination, regulatory, library, and institutional information.

![Ask CampusIQ Interface](screenshots/ask-campus-iq.png)

### 📚 Dashboard / Official Knowledge Base

The dashboard displays the indexed official knowledge base, including verified academic, admissions, examination, regulation, brochure, and library documents.

![JCET CampusIQ Knowledge Base Dashboard](screenshots/dashboard.png)

## 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  React + TypeScript │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                              REST API
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI Backend  │
                         │     on Render       │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐             ┌──────────────────┐
          │    PostgreSQL    │             │     pgvector     │
          │     Database     │             │  Vector Search   │
          └──────────────────┘             └──────────────────┘
```

## 📁 Project Structure

```text
JCET_CampusIQ/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── __init__.py
│   ├── scripts/
│   ├── tests/
│   ├── uploads/
│   ├── .env.example
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── services/
│   │   ├── types/
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
│
├── .env.example
├── .gitignore
├── README.md
├── SPEC.md
├── start.bat
└── start.ps1
```

## 🚀 Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nidalahmd/JCET_CampusIQ.git
cd JCET_CampusIQ
```

### 2. Database Setup

JCET CampusIQ uses PostgreSQL with the `pgvector` extension.

Create a PostgreSQL database, enable the `vector` extension, and configure the database connection in `backend/.env`.

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Do not commit real credentials or `.env` files containing secrets.

### 3. Backend Setup

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r backend/requirements.txt
```

Create the environment file:

```powershell
Copy-Item backend/.env.example backend/.env
```

Run database migrations:

```powershell
Set-Location backend
alembic upgrade head
```

Start the backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

### 4. Frontend Setup

Open another terminal from the project root:

```powershell
Set-Location frontend
npm install
```

Create the frontend environment file:

```powershell
Copy-Item .env.example .env
```

Set the API URL in `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Start the frontend:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## ❤️ Health Checks

The backend provides health endpoints for monitoring API and database connectivity.

### API Health

```text
https://jcet-campusiq-backend.onrender.com/api/health
```

### Database Health

```text
https://jcet-campusiq-backend.onrender.com/api/health/db
```

### API Documentation

```text
https://jcet-campusiq-backend.onrender.com/docs
```

## 🔐 Environment Variables

### Frontend

```env
VITE_API_URL=https://jcet-campusiq-backend.onrender.com
```

For local development:

```env
VITE_API_URL=http://localhost:8000
```

### Backend

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Production environment variables should be configured through the hosting platform rather than committed to GitHub.

## 🌍 Deployment

### Frontend — Vercel

The production frontend is deployed on Vercel:

**https://jcet-campus-iq.vercel.app/**

The frontend uses:

```env
VITE_API_URL=https://jcet-campusiq-backend.onrender.com
```

Whenever the production environment variable or frontend code is changed, redeploy the Vercel project.

### Backend — Render

The FastAPI backend is deployed on Render:

**https://jcet-campusiq-backend.onrender.com/**

The backend should be configured with the required production environment variables, including the PostgreSQL connection string.

## 🔄 Frontend–Backend Flow

```text
User
  ↓
Vercel Frontend
  ↓
VITE_API_URL
  ↓
Render FastAPI Backend
  ↓
PostgreSQL + pgvector
  ↓
Institutional Knowledge
```

## 🔎 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check API availability |
| GET | `/api/health/db` | Check database connectivity |
| GET | `/docs` | Open FastAPI interactive documentation |

## 📚 Intended Knowledge Sources

The platform is designed to work with official institutional information such as:

- College notices
- Academic information
- Regulations
- Policies
- Administrative information
- Institutional guidelines
- Approved college documents

The goal is to provide answers grounded in available institutional sources rather than relying only on general-purpose knowledge.

## 🔒 Security

- Never commit `.env` files containing secrets.
- Keep database credentials private.
- Store production secrets in deployment environment variables.
- Use HTTPS for production services.
- Restrict access to protected institutional information.
- Validate uploaded documents and user input.
- Do not expose private credentials in frontend code.

## 📌 Project Status

JCET CampusIQ is currently in its **Phase 1 foundation and prototype stage**.

The current implementation includes:

- Frontend application
- FastAPI backend
- PostgreSQL integration
- pgvector support
- Health monitoring
- Frontend deployment on Vercel
- Backend deployment on Render
- Environment-based configuration

The platform is being developed toward a complete institutional knowledge system with document ingestion, semantic retrieval, grounded responses, citations, and expanded access controls.

## 👤 Author

**Nidal Ahamed**

Jawaharlal College of Engineering and Technology

## 📄 License

This project is currently developed as an academic/project prototype.
