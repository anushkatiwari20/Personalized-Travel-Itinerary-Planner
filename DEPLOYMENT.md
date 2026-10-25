# DEPLOYMENT — Render (backend) + Vercel (frontend)

Prerequisite: code pushed to GitHub (`SETUP.md` → Activity 1.1) and Supabase tables created.

---

## Activity 6.1 — Deploy backend to Render

1. https://render.com → sign in with GitHub → **Dashboard** → **Add new → Web Service**.
2. **Import your project from GitHub** → pick `Personalized-Travel-Itinerary-Planner`.
3. Configure the service:

   | Field | Value |
   |---|---|
   | Name | `personalized-travel-itinerary-planner` (any name) |
   | Language / Environment | **Python 3** |
   | Region | closest to your users (e.g. Singapore) |
   | Branch | `main` |
   | Root Directory | `backend` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT` |
   | Instance type | Free |

   (Or click **Add new → Blueprint** and let Render read `render.yaml`.)

4. **Environment variables** → **Add from .env** → paste the contents of `backend/.env`, then change:
   ```
   ENVIRONMENT=production
   DEBUG=False
   BACKEND_URL=https://<your-service>.onrender.com
   FRONTEND_URL=http://localhost:5173        # update after Vercel step
   ```
   → **Add variables**.
5. **Deploy Web Service** → wait for logs to show `Uvicorn running` and the status badge **Live**.
6. Copy the service URL, e.g. `https://personalized-travel-itinerary-planner.onrender.com`. Test: open `<url>/health` → `{"status":"healthy", "database":"supabase", ...}` and `<url>/docs`.

> Free Render instances sleep after inactivity; the first request may take ~50 s.

---

## Activity 6.2 — Deploy frontend to Vercel

1. https://vercel.com → sign in with GitHub → **Add New → Project**.
2. **Import Git Repository** → `Personalized-Travel-Itinerary-Planner` → **Import**.
3. **Root Directory** → **Edit** → select **`frontend`** → **Continue**.
4. Framework preset: **Vite** (auto-detected). **Build and Output Settings**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
5. **Environment Variables** → Key `VITE_API_URL` → Value `https://<your-render-service>.onrender.com/api` (note the `/api`).
6. **Deploy** → wait for *Production Deployment is done*.
7. **Domains** → copy the https URL, e.g. `https://personalized-travel-itinerary-planner.vercel.app`.

---

## Connect the two

1. Render → your service → **Environment** → set `FRONTEND_URL=https://<your-vercel-app>.vercel.app` → **Save, rebuild and deploy**.
2. Wait until Render shows **Live** again.
3. Open the Vercel URL → Register → Create a trip → Generate. Check Supabase **Table Editor** → `users`, `trips`, `itineraries`, `history` have new rows.

Render + Vercel are now connected to Supabase and the deployment is complete.

---

## Add the links in SkillWallet

Project page → **Add Demo Link** = Vercel URL, **Add Github Link** = repository URL.

## Redeploys

Every `git push` to `main` triggers an automatic redeploy on both Render and Vercel.
