# CareerForge AI

CareerForge AI is the existing Flask/Jinja career planning and placement preparation application. Its V1–V15 routes and UI remain in the current `app.py`, `routes/`, `services/`, `templates/`, and `static/` structure.

## Local development

Use Python 3.10 or later and create a local `.env` from `.env.example`. Set a unique local `FLASK_SECRET_KEY`; `.env` is ignored by Git. For local SQLite development, remove or leave `DATABASE_URL` empty in `.env`. For HTTP development, set `SESSION_COOKIE_SECURE=False` locally. SQLite is used only when no database URL is configured outside Render/Vercel production.

```powershell
python -m pip install -r requirements.txt
python app.py
```

The local server defaults to `127.0.0.1:5000`. The application health endpoint is `/api/health`. Run `python scripts/check_local_schema.py` to validate the SQLite bootstrap in an isolated temporary directory.

## Production architecture

Production uses Supabase PostgreSQL as the single application database and Supabase Storage’s private `resumes` bucket for original resume files. Render runs the app with Gunicorn; Vercel discovers the Flask `app` exported from root `app.py` and serves CDN assets from `public/static/`.

See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for applying the schema and creating the private bucket, and [DEPLOYMENT.md](DEPLOYMENT.md) for Render and Vercel environment settings. The repository does not run remote migrations or deploy to either service automatically.

Vercel Function requests are limited to 4.5 MB, so CareerForge enforces a 4 MB total request limit there; Render/local keep the 10 MB limit. A direct-to-Supabase upload flow would be needed to support larger Vercel uploads.

Keep production secrets and database URLs in the Render/Vercel environment settings. Never commit `.env` or expose `SUPABASE_SERVICE_ROLE_KEY` to browser code.
