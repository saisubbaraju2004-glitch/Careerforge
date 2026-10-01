# Deployment

The same repository contains the Flask/Jinja app for Render and Vercel. Both production deployments must use the same Supabase PostgreSQL project. Do not configure Render PostgreSQL as the app database.

## RENDER DEPLOYMENT

Use the existing GitHub repository and existing Render web service:

- Repository: `saisubbaraju2004-glitch/Careerforge`
- Branch: `master`
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`
- Health check path: `/api/health`

`render.yaml` describes one Python web service, links the existing `careerforge-production` environment group, and declares `DATABASE_URL` as a dashboard-supplied value. It does not declare or provision a Render database. Ensure `DATABASE_URL` is the Supabase direct/session-pooler URL, `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set in Render’s server-side environment, and `SUPABASE_STORAGE_BUCKET=resumes`. Keep `FLASK_SECRET_KEY` in the linked group. Set `SESSION_COOKIE_SECURE=True` and `FLASK_DEBUG=False`.

The app requires the PostgreSQL migration to be applied before serving authenticated data routes. After deploying, `/api/health` should return HTTP 200 with `{"success":true,"status":"healthy","database":"connected"}`. Database failures return HTTP 503 without credentials or stack traces in the response.

## VERCEL DEPLOYMENT

Create a Vercel project connected to the same repository and select branch `master`. Vercel’s Python runtime detects the top-level `app.py` and its exported Flask `app`; it does not need a second Flask app or a `vercel.json` for this layout. `wsgi.py` remains the Render/Gunicorn entry point.

Set these in Vercel’s server-side Production environment:

- `DATABASE_URL`: Supabase transaction-pooler URL (port 6543)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET=resumes`
- `FLASK_SECRET_KEY`
- `FLASK_DEBUG=False`
- `SESSION_COOKIE_SECURE=True`
- `GEMINI_API_KEY` if AI-backed responses are desired

Vercel serves static files from `public/`. Existing templates keep using Flask’s `/static/...` URLs; run `python scripts/sync_public_assets.py` after changing `static/` and commit the generated `public/static/` mirror. This preserves the existing UI and provides CDN-served CSS, JavaScript, logo, and favicon files.

Vercel Function request bodies are limited to 4.5 MB. CareerForge therefore enforces a 4 MB total request limit on Vercel to leave room for multipart form overhead; Render and local development retain the 10 MB limit. Larger Vercel uploads require a future direct-to-Supabase signed-upload flow.

Vercel’s serverless filesystem is not used for durable app data. SQLite is a local-development fallback only; Vercel requires `DATABASE_URL`. User sessions are signed cookies and each authenticated request revalidates its user against PostgreSQL, so authentication does not depend on process memory.
