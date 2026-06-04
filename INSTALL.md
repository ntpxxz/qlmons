# Installation & Setup Guide

## 📋 Prerequisites

- **Python 3.8+** - Download from <https://www.python.org/>
- **SQL Server** - Already running on `192.168.101.219`
- **ODBC Driver 17** - For SQL Server connection

---

## 🚀 Installation Steps

### Step 1: Download ODBC Driver (if not installed)

**Windows:**
Download from: <https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server>

Test connection:

```bash
sqlcmd -S 192.168.101.219 -U DATALYZER -P NMB54321 -Q "SELECT 1"
```

---

### Step 2: Create Database & Tables

```bash
sqlcmd -S 192.168.101.219 -U DATALYZER -P NMB54321 -i database\schema.sql
```

✅ This will create:

- Users table
- RegisteredHosts table
- SessionMonitor table
- PendingHosts table
- AuditLog table
- Sample data

---

### Step 3: Install Python Dependencies

Navigate to the backend folder:

```bash
cd backend
```

Install all requirements:

```bash
pip install -r requirements.txt
```

**What gets installed:**

- Flask 2.3.3 - Web framework
- Flask-CORS 4.0.0 - Cross-origin support
- pyodbc 4.0.39 - SQL Server driver
- python-dotenv 1.0.0 - Environment variables

---

### Step 4: Configure Environment Variables

Create `.env` file from the template:

**Windows (PowerShell):**

```powershell
copy .env.example .env
```

**Windows (CMD):**

```cmd
copy .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

**Edit `.env` file** and verify:

```
SQL_SERVER=192.168.101.219
SQL_DATABASE=SqlSecurityHUD
SQL_USER=DATALYZER
SQL_PASSWORD=NMB54321
FLASK_PORT=5090
```

---

### Step 5: Start the Application

From the `backend` folder:

```bash
python app.py
```

**Expected output:**

```
 * Running on http://127.0.0.1:5090
```

---

## 🌐 Access the Application

Open in your browser:

```
http://localhost:5090
```

Or:

```
http://192.168.101.219:5090
```

---

## 📍 Available Pages

| URL | Purpose |
|-----|---------|
| `http://localhost:5090/` | Main Dashboard |
| `http://localhost:5090/test-scan.html` | Test/Debug Scan |
| `http://localhost:5090/debug.html` | API Debug Page |

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] ODBC Driver 17 installed
- [ ] SQL Server accessible (test with sqlcmd)
- [ ] Database created (schema.sql executed)
- [ ] .env file configured
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] Application running (python app.py)
- [ ] Dashboard accessible (<http://localhost:5090>)

---

## 🔧 Troubleshooting

### "ODBC Driver 17 not found"

```
Solution: Install ODBC Driver 17 from Microsoft
```

### "Login failed for user 'DATALYZER'"

```
Verify:
1. SQL Server is running on 192.168.101.219
2. Username/password in .env are correct
3. User has database access permission
```

Test connection:

```bash
sqlcmd -S 192.168.101.219 -U DATALYZER -P NMB54321 -Q "SELECT @@VERSION"
```

### "Port 5090 already in use"

Change port in `.env`:

```
FLASK_PORT=5091
```

### "Module not found: Flask"

Reinstall dependencies:

```bash
pip install --upgrade -r requirements.txt
```

---

## 📦 Dependencies Details

### requirements.txt

```
Flask==2.3.3          # Web framework
Flask-CORS==4.0.0     # Enable CORS
pyodbc==4.0.39        # SQL Server connection
python-dotenv==1.0.0  # Load .env variables
```

---

## 🚀 Next Steps

1. ✅ Open dashboard: <http://localhost:5090>
2. 🔍 Run test scan: <http://localhost:5090/test-scan.html>
3. 📊 Monitor SQL Server sessions in real-time
4. ⚠️ Manage host whitelist (approve/block)
5. 📋 Review audit logs

---

**Status:** ✅ Ready to use!

For questions or issues, check the troubleshooting section or test with the debug pages.
