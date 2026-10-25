# SETUP — step by step (Epics 1, 2 & 5.4)

Follow in order. Every step maps to an activity in the SkillWallet workspace.

---

## Epic 1 — Vibe-coding environment

### Activity 1.1 — Cursor IDE, Node.js, GitHub repo
1. Install Cursor → https://cursor.com/download (Windows `.exe`, macOS `.dmg`, Linux `.AppImage` — `chmod +x` then run; install `libfuse2` if it fails).
2. Install Node.js 18+ → https://nodejs.org/en/download. Verify: `node -v`, `npm -v`.
3. Install Python 3.11+ → verify `python --version`.
4. GitHub → sign in → **+ → New repository** → name `Personalized-Travel-Itinerary-Planner`, Public, no README (this project already has one) → **Create**.
5. Push this folder:
   ```bash
   git init
   git add .
   git commit -m "Personalized Travel Itinerary Planner — initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/Personalized-Travel-Itinerary-Planner.git
   git push -u origin main
   ```

### Activity 1.2 — Enable AI coding tools
- Cursor: `Ctrl/Cmd + I` opens the **Agent** panel; `Ctrl/Cmd + K` inline edit; `Ctrl/Cmd + L` chat. Sign in and pick a model.
- Use the ChatGPT/Claude prompts in `PROJECT_COMPLETION.md` → "Prompts used" when you want to extend features.

### Activity 1.3 — Folder structure
Already generated (see `README.md`). The prompt used to generate it is recorded in `PROJECT_COMPLETION.md`.

---

## Epic 2 — Supabase database

### Activity 2.1 — Create Supabase project
1. https://supabase.com → **Start your project** → sign up (GitHub/Google/email).
2. **New Project** → Name: `travel-planner` · DB password: strong (SAVE IT) · Region: closest (e.g. Asia-Pacific / Singapore) · Free plan → **Create new project** (2–3 min).
3. Dashboard → **Project Status** → all services *Healthy*. If not: **Project Settings → General → Restart project**, wait a few minutes.

### Activity 2.2 — Create tables
1. Left sidebar → **SQL Editor** → **New**.
2. Open `database/schema.sql`, copy **everything**, paste, **Run** (Ctrl+Enter).
3. Expect `Success. No rows returned`.
4. **Table Editor** → you should see 6 tables: `history`, `itineraries`, `preferences`, `saved_places`, `trips`, `users`.

### Activity 2.3 — Store API keys in `.env`
1. Go to the project root (folder containing `frontend` and `backend`).
2. `cd backend` → copy `.env.example` → `.env` (name exactly `.env`, not `.env.txt`).
3. **SUPABASE_URL** → Project Settings → **Data API** → *Project URL*.
4. **SUPABASE_KEY** / **SUPABASE_SERVICE_ROLE_KEY** → Project Settings → **API Keys** → tab *Legacy anon, service_role API keys* → copy `anon public` and `service_role secret`.
5. Fill them into `backend/.env`.

---

## Epic 5.4 — Environment & configuration (AI keys)

### Groq (recommended, free)
1. https://console.groq.com → sign in → **API Keys** → **Create API Key** → copy.
2. `.env`: `AI_PROVIDER=groq`, `GROQ_API_KEY=gsk_...`

### SECRET_KEY (JWT)
```bash
cd backend
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Paste the output as `SECRET_KEY=` in `.env`.

### Hugging Face (alternative, free)
https://huggingface.co/settings/tokens → **New token** → Role *Read*, Name `travel-planner` → copy → `.env`: `AI_PROVIDER=huggingface`, `HUGGINGFACE_API_KEY=hf_...`

### Ollama (local / offline)
1. https://ollama.com/download → install → restart terminal.
2. `ollama pull llama3` (or `ollama pull mistral`), test with `ollama run llama3`.
3. `.env`: `AI_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434`, `OLLAMA_MODEL=llama3`.

Final `backend/.env` should look like:
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SECRET_KEY=<random 32+ chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...
HUGGINGFACE_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
DEBUG=True
ENVIRONMENT=development
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
REDIS_URL=
LOG_LEVEL=INFO
```

---

## Run locally

```bash
# Backend (terminal 1)
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload    # http://localhost:8000  → Swagger at /docs

# Frontend (terminal 2)
cd frontend
cp .env.example .env             # VITE_API_URL=http://localhost:8000/api
npm install
npm run dev                      # http://localhost:5173
```

Run the backend tests: `cd backend && python tests/test_services.py` (or `pip install pytest && pytest -q`).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `database: in-memory` in `/health` | `SUPABASE_URL` or keys missing in `backend/.env` |
| Itinerary says "Set AI_PROVIDER…" | No `GROQ_API_KEY` → template provider is being used |
| CORS error in browser | `FRONTEND_URL` in backend `.env` must match the frontend origin |
| 401 after a while | Token expired (`ACCESS_TOKEN_EXPIRE_MINUTES`) → sign in again |
| Supabase "Not Healthy" | Project Settings → Restart project |
