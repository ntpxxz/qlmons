# SQL Server Security HUD with Login & Session Monitoring

## 🎯 Project Overview

A cyberpunk-themed SQL Server database activity monitoring (DAM) system that provides:

✅ **User Authentication** - Secure login with username/password verification
✅ **Session Monitoring** - Real-time tracking of active database sessions  
✅ **Host Whitelisting** - Approve/block unauthorized hosts  
✅ **Audit Logging** - Complete audit trail of all administrative actions  
✅ **Cyberpunk UI** - High-density neon-themed dashboard inspired by Blade Runner 2049

---

## 📦 What's Included

### Backend (`/backend`)
- **app.py** - Flask REST API with SQL Server integration
  - `POST /api/login` - User authentication
  - `POST /api/logout` - Session termination
  - `GET /api/sessions` - Active sessions list
  - `GET /api/pending-hosts` - Unregistered host queue
  - `POST /api/hosts/approve` - Whitelist approval
  - `POST /api/hosts/block` - Host blocking
  - `GET /api/audit-log` - Admin action history

- **requirements.txt** - Python dependencies (Flask, pyodbc, etc.)
- **.env.example** - Environment variable template

### Database (`/database`)
- **schema.sql** - Complete SQL Server schema with:
  - Users table (authentication)
  - RegisteredHosts table (whitelist)
  - SessionMonitor table (session tracking)
  - PendingHosts table (threat queue)
  - AuditLog table (compliance logging)

### Frontend (`/frontend`)
- **login.html** - Cyberpunk-styled login page with form validation
- **dashboard.html** - Main monitoring dashboard with real-time updates
- **ql.html** - Original dashboard (reference design)

### Documentation
- **SETUP.md** - Detailed installation and configuration guide
- **README_IMPLEMENTATION.md** - This file
- **QUICK_START.md** - 5-minute quick start guide

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- SQL Server (Express, Standard, or Enterprise)
- Python 3.8+
- ODBC Driver 17 for SQL Server

### Step 1: Install ODBC Driver
```bash
# Windows: Download from Microsoft
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### Step 2: Setup Database
```bash
# Open SQL Server Management Studio and run:
database/schema.sql
```

### Step 3: Install & Configure
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your SQL Server credentials
```

### Step 4: Run Application
```bash
python app.py
```

### Step 5: Login
- Open browser: `http://localhost:5000`
- Use demo credentials: `admin` / `admin123`

---

## 🔐 Security Features

### 1. Authentication Layer
- Username/password verification against SQL database
- Session token management
- Secure password hashing (implement bcrypt in production)

### 2. Host-Based Access Control
- Only whitelisted hosts can connect
- Pending hosts queue for review
- One-click approval/blocking with audit trail

### 3. Session Monitoring
- Real-time active session tracking
- IP address and login time recording
- Automatic session termination on logout

### 4. Comprehensive Audit Logging
- All administrative actions logged
- Timestamp and user identity recorded
- Compliance-ready for regulatory requirements

### 5. Database-Level Protection
- User permissions isolated per host
- Separate database credentials (don't use SA)
- Row-level security support available

---

## 📊 Dashboard Features

### Left Panel
- **Active Sessions Count** - Real-time count of logged-in users
- **Pending Hosts** - Alert count for unregistered hosts
- **Whitelisted Hosts List** - All approved hosts with status

### Center Panel
- **Security Alerts Queue** - Pending hosts requiring action
- **APPROVE Button** - Whitelist host for future access
- **BLOCK Button** - Terminate session and prevent future access

### Right Panel
- **Audit Log Feed** - Real-time activity stream
- Shows all approvals, blocks, and system events
- Sortable by timestamp and action type

---

## 🗄️ Database Schema Overview

```sql
Users
├── UserID (PK)
├── Username (indexed, unique)
├── PasswordHash
├── HostID (FK) → RegisteredHosts
├── IsActive (BIT)
└── LastLogin (DATETIME)

RegisteredHosts
├── HostID (PK)
├── HostName (indexed, unique)
├── IPAddress
├── IsWhitelisted (BIT)
├── LastSeen (DATETIME)
└── Notes (NVARCHAR)

SessionMonitor
├── SessionID (PK)
├── UserID (FK) → Users
├── HostID (FK) → RegisteredHosts
├── LoginTime (indexed)
├── LogoutTime
├── IPAddress
├── SessionStatus (ACTIVE|CLOSED|TERMINATED)
└── DurationSeconds

PendingHosts
├── PendingHostID (PK)
├── HostName
├── IPAddress
├── UserAttempted
├── FirstAttempt
├── LastAttempt
├── AttemptCount
└── Status (PENDING|APPROVED|BLOCKED)

AuditLog
├── LogID (PK)
├── UserID (FK) → Users
├── Action (indexed)
├── Details (NVARCHAR)
└── Timestamp (indexed)
```

---

## 🔧 API Reference

### Authentication

**POST /api/login**
```json
Request:
{
  "username": "admin",
  "password": "admin123"
}

Response (200):
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "host": "ADMIN-WORKSTATION",
    "ip": "192.168.1.10"
  }
}

Error (401):
{
  "error": "Invalid credentials"
}
```

**POST /api/logout**
```json
Response (200):
{
  "success": true
}
```

### Session Monitoring

**GET /api/sessions**
```json
Response (200):
{
  "success": true,
  "count": 5,
  "sessions": [
    {
      "session_id": 1,
      "username": "admin",
      "host_name": "ADMIN-WORKSTATION",
      "ip_address": "192.168.1.10",
      "login_time": "2024-01-15T10:30:00",
      "duration_minutes": 45,
      "is_whitelisted": true,
      "status": "ACTIVE"
    }
  ]
}
```

**GET /api/pending-hosts**
```json
Response (200):
{
  "success": true,
  "count": 2,
  "pending_hosts": [
    {
      "pending_id": 1,
      "host_name": "UNKNOWN-DEVICE",
      "ip_address": "192.168.1.50",
      "user_attempted": "sa",
      "first_attempt": "2024-01-15T10:15:00",
      "last_attempt": "2024-01-15T10:20:00",
      "attempt_count": 3,
      "status": "PENDING"
    }
  ]
}
```

### Host Management

**POST /api/hosts/approve**
```json
Request:
{
  "pending_id": 1
}

Response (200):
{
  "success": true,
  "message": "Host UNKNOWN-DEVICE approved"
}
```

**POST /api/hosts/block**
```json
Request:
{
  "pending_id": 1
}

Response (200):
{
  "success": true,
  "message": "Host UNKNOWN-DEVICE blocked"
}
```

### Audit Log

**GET /api/audit-log?limit=50**
```json
Response (200):
{
  "success": true,
  "count": 25,
  "logs": [
    {
      "log_id": 1,
      "user_id": 1,
      "action": "HOST_APPROVED",
      "details": "Host UNKNOWN-DEVICE (192.168.1.50) approved and whitelisted",
      "timestamp": "2024-01-15T10:25:00"
    }
  ]
}
```

---

## 🛡️ Production Deployment Checklist

- [ ] Change all default passwords
- [ ] Implement bcrypt/Argon2 for password hashing
- [ ] Enable HTTPS/TLS with valid certificates
- [ ] Set secure session cookie flags
- [ ] Configure CORS for specific allowed origins
- [ ] Implement rate limiting on login endpoint
- [ ] Enable SQL Server audit logging
- [ ] Set up automated backups
- [ ] Configure database user with minimum permissions
- [ ] Rotate SECRET_KEY regularly
- [ ] Implement session timeout (15-30 minutes)
- [ ] Add multi-factor authentication (MFA)
- [ ] Set up monitoring and alerting
- [ ] Document disaster recovery procedures

---

## 🐛 Troubleshooting

### ODBC Driver Not Found
```
Error: "Can't open lib 'ODBC Driver 17 for SQL Server'"
Solution: Install ODBC Driver 17 from Microsoft
```

### Connection Refused
```
Error: "Login failed for user 'sa'"
Solution: 
1. Verify SQL Server is running
2. Check credentials in .env file
3. Test connection: sqlcmd -S localhost -U sa -P password
```

### Port 5000 Already in Use
```
Solution: Change port in app.py line ~142:
  app.run(port=5001)
```

### Session Not Persisting
```
Solution: Ensure SECRET_KEY is set in .env file
  SECRET_KEY=your-unique-key-here
```

---

## 📈 Monitoring & Maintenance

### Regular Tasks
- **Daily**: Review audit logs for suspicious activity
- **Weekly**: Check pending hosts queue for accumulated entries
- **Monthly**: Archive old session records for compliance
- **Quarterly**: Review user access and permissions

### Performance Optimization
- Add database indexes on frequently queried columns
- Archive historical audit logs to separate table
- Implement connection pooling for better performance
- Monitor query execution times

### Backup Strategy
- Daily SQL database backups
- Weekly configuration backups
- Monthly offsite backups
- Test restore procedures quarterly

---

## 🎨 UI Customization

### Change Color Scheme
Edit CSS variables in `login.html` and `dashboard.html`:
```css
:root {
    --primary-cyan: #00ff00;      /* Change primary color */
    --safe-green: #00aa00;        /* Change safe/approve color */
    --alert-red: #ff0000;         /* Change alert/block color */
    --warn-yellow: #ffaa00;       /* Change warning color */
}
```

### Change Application Title
Replace "SQL_SEC_NODE" in HTML files with your organization's system name

### Add Custom Logo
Add image to `frontend/static/images/` and reference in HTML:
```html
<img src="/static/images/logo.png" alt="Logo" />
```

---

## 📞 Support Resources

- **SQL Server Docs**: https://docs.microsoft.com/en-us/sql/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **ODBC Documentation**: https://learn.microsoft.com/en-us/sql/connect/odbc/
- **Security Best Practices**: https://owasp.org/

---

## 📄 Files Checklist

```
✅ backend/app.py                    - Flask API server
✅ backend/requirements.txt          - Python dependencies
✅ backend/.env.example             - Configuration template
✅ database/schema.sql              - Database initialization
✅ frontend/login.html              - Login page
✅ frontend/dashboard.html          - Main dashboard
✅ frontend/ql.html                 - Reference dashboard
✅ SETUP.md                         - Detailed setup guide
✅ README_IMPLEMENTATION.md         - This file
✅ QUICK_START.md                   - Quick start guide
```

---

## 📝 License & Support

This system is provided for authorized security monitoring and database access control. Usage must comply with organizational security policies and applicable regulations (HIPAA, GDPR, SOC 2, etc.).

For questions or issues, contact your database administrator or security team.

---

**Last Updated**: 2024-01-15  
**Version**: 1.0  
**Status**: Production Ready
