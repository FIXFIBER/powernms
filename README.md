# PowerNMS

FiberOne Rectifier NOC dashboard (FastAPI + PostgreSQL).

## What it does
- Login-protected NOC dashboard for POP/rectifier monitoring
- PostgreSQL-backed data model (SQLAlchemy) with seed data fallback
- Excel export (`/export/excel`)
- Routes: `/`, `/login`, `/logout`, `/dashboard`, `/export/excel`

## Requirements
- Python 3.12+
- PostgreSQL 16+
- Packages: `fastapi uvicorn sqlalchemy psycopg2-binary pandas openpyxl python-multipart jinja2` (install what your app needs in your venv)

## Configuration
Set `DATABASE_URL` via environment (recommended) or a `.env` file loaded by your process manager:

```bash
cp .env.example .env
# edit .env with real credentials
```

Example:
`DATABASE_URL=postgresql+psycopg2://fiberone:YOUR_PASSWORD@127.0.0.1:5432/fiberone_noc`

**Never commit `.env` or real credentials.**

## Run locally (dev)
```bash
uvicorn main:app --host 127.0.0.1 --port 8080
```

## Production deployment (reference)
- `deploy/fiberone-noc.service` — systemd unit (runs uvicorn on `127.0.0.1:8080`)
- `deploy/nginx-fiberone-noc.conf` — nginx HTTP→HTTPS redirect + TLS reverse proxy

Typical steps on Ubuntu:
1. Create DB/user in PostgreSQL and set `DATABASE_URL`.
2. Install deps in a venv.
3. Install the systemd unit, `daemon-reload`, `enable --now`.
4. Install nginx site config + TLS cert, test (`nginx -t`), reload.
5. Open firewall ports `22,80,443` (e.g., `ufw`).

## Security notes
- App login credentials are defined in application code/config — change them before production exposure.
- Use HTTPS with a valid certificate (self-signed is only for testing).
- Keep DB bound to localhost or restrict access; use strong passwords.
