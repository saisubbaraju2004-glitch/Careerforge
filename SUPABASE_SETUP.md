# Supabase setup

CareerForge uses Supabase PostgreSQL for production records and a private Supabase Storage bucket for uploaded resumes. No Supabase migration or resource creation is run automatically by this repository.

## Apply the database schema

1. Open the intended Supabase project and confirm its project reference before running SQL.
2. Open **SQL Editor** and create a new query.
3. Copy the complete contents of `supabase/migrations/001_initial_schema.sql` into the editor and run it.
4. Verify that `public.users`, `public.user_records`, and `public.rate_limits` exist.

The schema preserves the existing application model: password hashes stay in `users`, and V1–V15 feature records remain JSON-serialized text in `user_records.payload`. It does not import rows from any existing SQLite or Render database. If those databases contain user accounts or production data, take a protected backup and migrate those rows before switching production traffic. Do not delete the source database as part of this setup.

The app bootstraps this schema automatically only for its local SQLite fallback. Production PostgreSQL schema changes are applied through reviewed migration files.

## Create the private resume bucket

1. In Supabase, open **Storage** and create a bucket named `resumes`.
2. Keep the bucket **Private**.
3. Set the file size limit to 10 MB and allowed content types to:
   - `application/pdf`
   - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
   - `text/plain`
4. Do not add public read policies. CareerForge uploads through the server-side Storage client using `SUPABASE_SERVICE_ROLE_KEY`; that key bypasses RLS and must remain server-only.

Production resume uploads use object paths of the form `users/<user_id>/resumes/<uuid>.<extension>`. The object path, original sanitized filename, MIME type, and byte size are stored in the user’s existing `resume` record in PostgreSQL. Documents are parsed from memory; the application does not write production uploads to `uploads/` or another local directory.

## Connection strings

Copy connection strings from the Supabase project’s **Connect** dialog. Never commit or paste them into source files.

- Render is a persistent service. Use a Supabase direct or session-pooler PostgreSQL connection compatible with the Render network; the application requires SSL and uses a bounded SQLAlchemy pool.
- Vercel is serverless. Set `DATABASE_URL` to the Supabase transaction-pooler connection (port 6543). The application uses `NullPool`, a connection timeout, and disables psycopg prepared statements for this pool mode.

Both variables must target the same Supabase project. The app normalizes `postgres://`, `postgresql://`, and `postgresql+psycopg://` URLs and adds `sslmode=require` when absent.

## Required backend environment variables

Set these in the Render service and Vercel project settings as appropriate:

- `DATABASE_URL` for Render
- `DATABASE_URL` for Vercel (the same variable name used by Render)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET` (normally `resumes`)
- `FLASK_SECRET_KEY`
- `GEMINI_API_KEY` (optional; deterministic AI fallbacks remain available)

Do not define the service-role key in browser variables, `public/`, GitHub, or client JavaScript. `.env` remains local-only and ignored by Git.

## Safe local schema check

Run `python scripts/check_local_schema.py`. It creates a temporary SQLite database under the operating system’s temp directory, verifies the existing three-table schema bootstrap, and removes that temporary directory on exit. It does not connect to or alter Supabase.
