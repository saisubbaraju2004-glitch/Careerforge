# CareerForge AI

CareerForge AI is a Flask-based career planning and placement preparation application.

## Requirements

- Python 3.10 or later
- Environment variables configured from `.env.example`

Create a `.env` file from `.env.example`, set `FLASK_SECRET_KEY` to a unique,
high-entropy value, and add AI provider keys if AI-backed features are needed.
The application uses deterministic local fallbacks when an AI provider is not
configured or unavailable.

## Local development

Install the dependencies and run the Flask application:

```powershell
python -m pip install -r requirements.txt
python app.py
```

The development entry point binds to `127.0.0.1:5000` unless `HOST` and `PORT`
are set. Keep `FLASK_DEBUG=False` except during local debugging.

## Production

Use Waitress rather than Flask's development server:

```powershell
python -m pip install -r requirements.txt
python wsgi.py
```

The WSGI entry point uses Waitress and reads `HOST` and `PORT` from the
environment (defaults: `0.0.0.0:8000`). Keep `FLASK_DEBUG=False`. The application
serves its health check at `/api/health`.

Resume uploads are temporarily stored in `uploads/` while parsed and should not
be shared between application users or retained as durable user data.

Do not expose the application to the public internet until authentication,
request rate limiting, and durable per-user data storage are provided by the
application or a trusted deployment boundary.
