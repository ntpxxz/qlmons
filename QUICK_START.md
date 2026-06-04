# SQL Server Security HUD - Quick Start (5 Minutes)

## Prerequisites Checklist

- [ ] SQL Server installed (Express, Standard, or Enterprise)
- [ ] Python 3.8+ installed
- [ ] ODBC Driver 17 for SQL Server installed

---

## Step 1: Install ODBC Driver (2 minutes)

### Windows
1. Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Run the installer
3. Restart your computer

### macOS
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install mssql-tools17
```

### Linux
```bash
sudo apt-get update
sudo apt-get install msodbcsql17
```

---

## Step 2: Create Database (1 minute)

### Option A: SQL Server Management Studio (GUI)
1. Open SQL Server Management Studio
2. Connect to your SQL Server instance
3. Open the file: `database/schema.sql`
4. Click **Execute** (F5)

### Option B: Command Line
```bash
sqlcmd -S localhost -U sa -P YourPassword123 -i database\schema.sql
```

---

## Step 3: Install Python Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

---

## Step 4: Configure Environment (30 seconds)

```bash
# Copy template
cp .env.example .env

# Edit .env file with your SQL Server credentials
# Update these lines:
# SQL_SERVER=localhost
# SQL_USER=sa
# SQL_PASSWORD=YourPassword123
```

---

## Step 5: Start the Application (30 seconds)

```bash
cd backend
python app.py
```

You should see:
```
WARNING in werkzeug: This is a development server. Do not use it in production.
 * Running on http://127.0.0.1:5000
```

---

## Step 6: Login

1. Open browser: **http://localhost:5000**
2. Use demo credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

3. You should see the cyberpunk dashboard! 🎉

---

## What You Can Do Now

✅ **View Active Sessions** - See all logged-in users and hosts  
✅ **Review Pending Hosts** - Check unregistered hosts attempting connection  
✅ **Approve/Block Hosts** - One-click whitelist management  
✅ **Check Audit Log** - See complete action history  

---

## Demo Data

The database comes with sample data:

**Users:**
| Username | Password | Host |
|----------|----------|------|
| admin | admin123 | ADMIN-WORKSTATION |
| dbadmin | password123 | SERVER-APP-01 |
| operator | operator123 | SERVER-APP-02 |

**Hosts:**
- ADMIN-WORKSTATION (192.168.1.10)
- SERVER-APP-01 (192.168.1.20)
- SERVER-APP-02 (192.168.1.21)
- HR-FRONTEND (192.168.1.30)
- BACKUP-NODE (192.168.1.40)

---

## Common Issues

### "ODBC Driver 17 not found"
→ Download and install ODBC Driver 17 from Microsoft

### "Login failed for user 'sa'"
→ Check SQL Server is running and credentials are correct:
```bash
sqlcmd -S localhost -U sa -P YourPassword123 -Q "SELECT 1"
```

### "Port 5000 already in use"
→ Edit `backend/app.py` line 142, change port to 5001:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### "Module 'flask' not found"
→ Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Next Steps

1. **Read Full Documentation**: See `SETUP.md` for detailed configuration
2. **Change Passwords**: Update default credentials for production
3. **Configure HTTPS**: Enable SSL/TLS for secure communication
4. **Add Users**: Run SQL INSERT statements to add more users
5. **Customize UI**: Modify colors/styling in HTML files

---

## Production Deployment

Before going live:

1. ✅ Change all default passwords
2. ✅ Implement HTTPS with valid certificates
3. ✅ Enable SQL Server audit logging
4. ✅ Set up automated backups
5. ✅ Implement password hashing (bcrypt/Argon2)
6. ✅ Configure firewall rules
7. ✅ Set up monitoring and alerting
8. ✅ Document operational procedures

See `SETUP.md` for complete production checklist.

---

## File Structure

```
qlmoni/
├── backend/
│   ├── app.py              ← Main Flask server
│   ├── requirements.txt    ← Install with pip
│   └── .env               ← Your configuration
├── frontend/
│   ├── login.html         ← Login page
│   └── dashboard.html     ← Main dashboard
├── database/
│   └── schema.sql         ← Run in SQL Server
├── QUICK_START.md         ← This file
└── SETUP.md               ← Detailed guide
```

---

## Need Help?

1. Check logs in terminal window where you ran `python app.py`
2. Verify SQL Server connection:
   ```bash
   sqlcmd -S localhost -U sa -P YourPassword123 -Q "SELECT @@VERSION"
   ```
3. Check firewall isn't blocking port 5000
4. Review `SETUP.md` for detailed troubleshooting

---

**You're all set! 🚀 Happy monitoring!**

Last Updated: 2024-01-15
