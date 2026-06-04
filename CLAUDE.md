# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SQL Server Security HUD — a cyberpunk-themed Database Activity Monitoring (DAM) dashboard. It reads live session data from SQL Server system views (`sys.dm_exec_sessions`) and manages a custom host whitelist/audit system stored in a separate `SqlSecurityHUD` database.

## Running the Backend

```powershell
cd backend
pip install -r requirements.txt
# Copy and configure .env (see .env.example for keys)
python app.py
```

Default port is **5090** (set via `FLASK_PORT` env var). The app serves `frontend/dashboard.html` directly at `/` — there is no login gate in the current implementation.

## Database Setup

Run `database/schema.sql` against SQL Server (via SSMS or `sqlcmd`) to create the `SqlSecurityHUD` database and all tables. Requires **ODBC Driver 17 for SQL Server** installed on the host machine.

The `.env` file (not `.env.example`) holds live credentials pointing to `192.168.101.219`. Do not overwrite it without backing up the current values.

## Architecture

```
backend/app.py  (Flask API + template server)
    │
    ├── serves frontend/dashboard.html at GET /
    ├── connects to SQL Server via pyodbc using .env credentials
    │
    ├── GET  /api/sessions        — queries sys.dm_exec_sessions (session_id > 50)
    ├── GET  /api/pending-hosts   — reads PendingHosts table (Status='PENDING')
    ├── POST /api/hosts/approve   — inserts to RegisteredHosts, updates PendingHosts, writes AuditLog
    ├── POST /api/hosts/block     — updates PendingHosts status, writes AuditLog
    └── GET  /api/audit-log       — reads AuditLog table, limit param via query string
```

**Two separate concerns share one SQL Server connection:**

1. **Live session data** — read from SQL Server system DMVs (`sys.dm_exec_sessions`, `sys.dm_exec_connections`). Requires a login with `VIEW SERVER STATE` permission.
2. **Custom management tables** — `PendingHosts`, `RegisteredHosts`, `AuditLog`, `Users`, `SessionMonitor` in the `SqlSecurityHUD` database.

**Frontend** (`frontend/dashboard.html`) is a single-file vanilla JS app. It polls the API every 30 seconds via `fetch()` and updates the DOM directly. No build step, no JS framework.

Flask is configured with `template_folder='../frontend'` and `static_folder='../frontend/static'` — templates are resolved relative to the `backend/` directory.

## Known Issues to Be Aware Of

- `GET /api/audit-log` interpolates the `limit` query parameter directly into SQL (`f'SELECT TOP {limit} ...'`) — this is a SQL injection risk if `limit` is not sanitized beyond the `type=int` cast on line 252.
- Passwords in `database/schema.sql` sample data are stored in plaintext. The `Users` table `PasswordHash` column holds raw strings in the seed data.
- No authentication middleware is active; `dashboard.html` is accessible without login.
