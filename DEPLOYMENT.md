# Deployment Guide

This is a local reference for deploying the app so anyone outside your machine can access it.

---

## Services Used (all free)

| Tier     | Service  | Free limits                          |
|----------|----------|--------------------------------------|
| Database | Render   | 1 GB PostgreSQL, 90-day expiry       |
| Backend  | Render   | 512 MB RAM, sleeps after 15 min idle |
| Frontend | Vercel   | Unlimited for personal projects      |

The backend sleeps after 15 minutes of inactivity on the free tier. The first request after idle takes about 30 seconds to wake up.

---

## Step 1 — Push to GitHub

Both Vercel and Render deploy directly from a GitHub repository. Make sure your latest code is pushed:

```bash
git add .
git commit -m "your message"
git push
```

---

## Step 2 — Create the Database on Render

1. Go to https://render.com and sign in with your GitHub account.
2. Click "New" and select "PostgreSQL".
3. Fill in:
   - Name: `tracker-db`
   - Region: pick the one closest to you
   - Plan: Free
4. Click "Create Database".
5. Once created, copy the "Internal Database URL" — you will need it in Step 3.

---

## Step 3 — Deploy the Backend on Render

1. On Render, click "New" and select "Web Service".
2. Connect your GitHub repository.
3. Configure the service:
   - Name: `tracker-backend`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2`
   - Plan: Free
4. Under "Environment Variables", add:

   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | any long random string |
   | `JWT_SECRET_KEY` | any long random string (32+ chars) |
   | `DATABASE_URL` | the Internal Database URL from Step 2 |
   | `JWT_ACCESS_TOKEN_EXPIRES` | `3600` |
   | `FRONTEND_URL` | leave blank for now, fill in after Step 4 |

5. Click "Create Web Service". Render will build and deploy.
6. Once deployed, copy your backend URL — it looks like `https://tracker-backend.onrender.com`.

After the first deploy, run migrations using the Render shell tab on your service:

```bash
flask db upgrade
```

Optionally seed demo data:

```bash
python seed.py
```

---

## Step 4 — Deploy the Frontend on Vercel

1. Go to https://vercel.com and sign in with your GitHub account.
2. Click "Add New Project" and import your GitHub repository.
3. Configure the project:
   - Root Directory: `frontend`
   - Framework Preset: Next.js (auto-detected)
4. Under "Environment Variables", add:

   | Key | Value |
   |-----|-------|
   | `BACKEND_URL` | your Render backend URL from Step 3 |

5. Click "Deploy".
6. Once deployed, copy your Vercel URL — it looks like `https://your-app.vercel.app`.

---

## Step 5 — Connect Frontend and Backend

Go back to Render, open your backend service, and update the `FRONTEND_URL` environment variable to your Vercel URL. Render will automatically redeploy.

---

## Step 6 — Verify

Open your Vercel URL in a browser. Register an account, create a team, and create a project. If the backend is asleep the first request may take up to 30 seconds — subsequent requests will be fast.
