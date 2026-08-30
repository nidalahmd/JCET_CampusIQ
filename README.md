# JCET CampusIQ

**AI-powered institutional knowledge assistant for Jawaharlal College of Engineering and Technology (JCET).**

JCET CampusIQ is a Retrieval-Augmented Generation (RAG) platform designed to help students and staff find reliable information from official institutional documents through grounded, source-aware responses.

## 🎯 Problem Statement

Educational institutions generate and maintain a large amount of institutional information such as academic documents, notices, policies, guidelines, and other official resources. However, this information is often distributed across different sources, making it difficult for students and staff to quickly find reliable and relevant information.

JCET CampusIQ aims to address this problem by providing a centralized institutional knowledge platform where users can access and interact with campus-related information through a structured and intelligent interface.

### Key Problems Addressed

- 📚 **Scattered Information**  
  Institutional information may be distributed across multiple documents and sources, making it difficult to locate.

- 🔎 **Difficulty Finding Relevant Information**  
  Users may spend significant time manually searching through lengthy documents to find specific information.

- 🤖 **Limited Intelligent Access**  
  Traditional document repositories provide storage but do not offer an intelligent way to retrieve and understand relevant information.

- 🏫 **Lack of a Centralized Knowledge Platform**  
  Students and staff need a single platform for accessing reliable institutional knowledge.

- 🔐 **Future Institutional Access Requirements**  
  Different types of users may require different levels of access to institutional resources.

### Proposed Solution

JCET CampusIQ is designed as a centralized institutional knowledge platform that combines a modern web interface with a FastAPI backend, PostgreSQL database, and pgvector-based infrastructure. The platform is being developed to support document ingestion, semantic retrieval, source-based responses, citations, and controlled institutional access.

The current implementation establishes the foundational architecture required to build these capabilities in later development phases.

## 🌐 Live Application

Frontend: https://jcet-campus-iq.vercel.app/

Backend API: https://jcet-campusig-backend.onrender.com/

API Documentation: https://jcet-campusig-backend.onrender.com/docs

GitHub Repository: https://github.com/nidalahmd/JCET_CampusIQ

✨ Key Features

🤖 AI-powered institutional question answering

🔎 Retrieval-Augmented Generation (RAG)

📚 Document-based knowledge retrieval

🔗 Source-grounded responses and citations

🛡️ Role-based access control

🗂️ Institutional document management

🧠 Semantic search with PostgreSQL and pgvector

❤️ Backend and database health monitoring

🔐 Environment-based configuration

🛠️ Tech Stack

Frontend

React

TypeScript

Vite

CSS

Backend

Python

FastAPI

SQLAlchemy

Alembic

Uvicorn

Database

PostgreSQL

pgvector

AI / RAG

Retrieval-Augmented Generation

Vector-based semantic retrieval

Gemini

Deployment

Vercel — Frontend

Render — Backend

GitHub — Source Code

🏗️ System Architecture

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

📁 Project Structure

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

🚀 Local Setup

1. Clone the Repository

git clone https://github.com/nidalahmd/JCET_CampusIQ.git
cd JCET_CampusIQ

2. Database Setup

JCET CampusIQ uses PostgreSQL with the pgvector extension.

Create a PostgreSQL database, enable the vector extension, and configure the database connection in backend/.env.

DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE

Do not commit real credentials or .env files containing secrets.

3. Backend Setup

Create a virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r backend/requirements.txt

Create the environment file:

Copy-Item backend/.env.example backend/.env

Run database migrations:

Set-Location backend
alembic upgrade head

Start the backend:

uvicorn app.main:app --reload --port 8000

Backend:

http://localhost:8000

4. Frontend Setup

Open another terminal from the project root:

Set-Location frontend
npm install

Create the frontend environment file:

Copy-Item .env.example .env

Set the API URL in frontend/.env:

VITE_API_URL=http://localhost:8000

Start the frontend:

npm run dev

Frontend:

http://localhost:5173

❤️ Health Checks

The backend provides health endpoints for monitoring API and database connectivity.

API Health

https://jcet-campusig-backend.onrender.com/api/health

Database Health

https://jcet-campusig-backend.onrender.com/api/health/db

API Documentation

https://jcet-campusig-backend.onrender.com/docs

🔐 Environment Variables

Frontend

VITE_API_URL=https://jcet-campusig-backend.onrender.com

For local development:

VITE_API_URL=http://localhost:8000

Backend

DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE

Production environment variables should be configured through the hosting platform rather than committed to GitHub.

🌍 Deployment

Frontend — Vercel

The production frontend is deployed on Vercel:

https://jcet-campus-iq.vercel.app/

The frontend uses:

VITE_API_URL=https://jcet-campusig-backend.onrender.com

Whenever the production environment variable or frontend code is changed, redeploy the Vercel project.

Backend — Render

The FastAPI backend is deployed on Render:

https://jcet-campusig-backend.onrender.com/

The backend should be configured with the required production environment variables, including the PostgreSQL connection string.

🔄 Frontend–Backend Flow

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

🔎 API Endpoints

Method

Endpoint

Purpose

GET

/api/health

Check API availability

GET

/api/health/db

Check database connectivity

GET

/docs

Open FastAPI interactive documentation

📚 Intended Knowledge Sources

The platform is designed to work with official institutional information such as:

College notices

Academic information

Regulations

Policies

Administrative information

Institutional guidelines

Approved college documents

The goal is to provide answers grounded in available institutional sources rather than relying only on general-purpose knowledge.

🔒 Security

Never commit .env files containing secrets.

Keep database credentials private.

Store production secrets in deployment environment variables.

Use HTTPS for production services.

Restrict access to protected institutional information.

Validate uploaded documents and user input.

Do not expose private credentials in frontend code.

📌 Project Status

JCET CampusIQ is currently in its Phase 1 foundation and prototype stage.

The current implementation includes:

Frontend application

FastAPI backend

PostgreSQL integration

pgvector support

Health monitoring

Frontend deployment on Vercel

Backend deployment on Render

Environment-based configuration

The platform is being developed toward a complete institutional knowledge system with document ingestion, semantic retrieval, grounded responses, citations, and expanded access controls.

👤 Author

Nidal Ahamed

Jawaharlal College of Engineering and Technology

📄 License

This project is currently developed as an academic/project prototype.