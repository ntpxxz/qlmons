# 🚀 SQL Security HUD - Start Here (No Login Required)

## 3-Step Setup

### Step 1: Create Database

```bash
sqlcmd -S 192.168.101.219 -U DATALYZER -P NMB54321 -i database\schema.sql
```

### Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Configure & Run

```bash
copy .env.example .env
# Edit .env with your SQL Server credentials, then:
python app.py
```

---

## Access the App

**Open in browser**: `http://localhost:5090`

✅ Dashboard loads **immediately** - no login required  
✅ Start monitoring SQL Server sessions  
✅ Approve/block hosts with one click  

---

## What You Get

🔍 **Real-time Session Monitoring**

- See all active database connections
- Track IP addresses and login times
- Monitor session duration

⚠️ **Security Alerts Queue**

- Detect unregistered hosts
- Approve to whitelist
- Block suspicious connections

📋 **Audit Log Feed**

- Complete action history
- All approvals/blocks logged
- Compliance-ready tracking

---

## Demo Data

The database includes sample hosts and data:

- 5 whitelisted hosts
- Sample pending alerts
- Historical audit logs

---

## Requirements

- SQL Server (Express or higher)
- Python 3.8+
- ODBC Driver 17

---

## Troubleshooting

**"ODBC Driver not found"**
→ Download from: <https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server>

**"Connection refused"**
→ Check: `sqlcmd -S localhost -U sa -P YourPassword123 -Q "SELECT 1"`

**"Port 5000 in use"**
→ Edit `app.py` line 105: change `port=5000` to `port=5001`

---

**That's it! You're ready to monitor.** 🎉
