# JCET CampusIQ

Phase 1 foundation for the JCET CampusIQ platform.

## Database setup

This project uses an external PostgreSQL provider with the `pgvector` extension; Docker is not required. Supabase and Neon are suitable options. Create a database, enable `vector`, and copy the connection URL into `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Copy the templates first:

```powershell
Copy-Item .env.example .env
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

Install and migrate the backend:

```powershell
python -m pip install -r backend/requirements.txt
Set-Location backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

The API health checks are available at `http://localhost:8000/api/health` and `http://localhost:8000/api/health/db`.

## Frontend

```powershell
Set-Location frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173`. The frontend uses `VITE_API_URL` to connect to the API and does not contain institutional data or mock answers.