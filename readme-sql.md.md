# 🛡️ SQL Server Security HUD

A Cyberpunk-themed Database Activity Monitoring (DAM) dashboard designed for SQL Server administrators. This system provides a high-density, real-time graphical interface to monitor active database sessions, manage host whitelists, and neutralize unauthorized connections.

## ✨ Features

* **Network Scanning:** Initiate manual scans to cross-reference active SQL Server sessions (`sys.dm_exec_sessions`) with the registered hosts database.
* **Pending Threat Queue:** Automatically catches unregistered hosts and places them in a queue for administrative review.
* **One-Click Resolution:** 
  * **[APPROVE]:** Whitelists the host for future connections.
  * **[BLOCK]:** Terminates the active session and prevents future access.
* **Live Audit Feed:** Tracks and displays all administrative actions, system logs, and security alerts in real-time.
* **Cyber Security HUD UI:** Lightweight, dependency-free frontend built with Vanilla HTML/CSS/JS, featuring a dark-mode neon aesthetic.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3 (CSS Variables, Grid, Flexbox), Vanilla JavaScript
* **Backend:** Python (FastAPI/Flask) or Node.js (Express) *— API Middleware*
* **Database:** Microsoft SQL Server (MS SQL)

---

## 📂 Project Structure

```text
sql-security-hud/
│
├── frontend/
│   └── index.html         # Main HUD Dashboard (UI/UX)
│
├── backend/               # (To be implemented based on spec.md)
│   ├── app.py             # API Server
│   └── database.py        # SQL Server Connection & Queries
│
├── database/
│   └── schema.sql         # MS SQL Database Initialization Scripts
│
├── spec.md                # System Specification & API Blueprint
└── README.md              # Project Documentation