# SQL Security HUD - Setup Guide

## Overview

This is a complete SQL Server login authentication system with session monitoring, host whitelist management, and real-time audit logging. The system prevents unauthorized database access through host-based access control.

---

## 📋 Prerequisites

- **SQL Server 2016+** (SQL Server Express or higher)
- **Python 3.8+**
- **ODBC Driver 17 for SQL Server** (Download: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **pip** (Python package manager)

---

## 🚀 Installation Steps

### 1. Install ODBC Driver (Windows)

Download and install ODBC Driver 17 for SQL Server from:
```
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### 2. Create Database

Open SQL Server Management Studio and run the schema script:

```bash
sqlcmd -S localhost -U sa -P YourPassword123 -i database\schema.sql
```

Or execute the contents of `database/schema.sql` directly in SQL Server Management Studio.

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and update with your SQL Server credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
SQL_SERVER=localhost
SQL_DATABASE=master
SQL_USER=sa
SQL_PASSWORD=YourPassword123
SECRET_KEY=your-secure-secret-key-here
```

---

## 📁 Project Structure

```
qlmoni/
├── backend/
│   ├── app.py                 # Flask application & API routes
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── .env                  # Environment variables (create from .env.example)
│
├── frontend/
│   ├── login.html            # Login page with cyberpunk styling
│   ├── ql.html              # Dashboard (existing monitoring HUD)
│   └── static/              # Static assets (CSS, JS, images)
│
├── database/
│   └── schema.sql           # SQL Server database schema
│
├── SETUP.md                 # This file
└── README.md                # Project documentation
```

---

## 🔑 Database Schema

### Users Table
Stores application users and their credentials.

```sql
UserID (PK)
Username (UNIQUE)
PasswordHash
Email
HostID (FK) - Link to RegisteredHosts
IsActive (BIT)
CreatedDate
LastLogin
```

### RegisteredHosts Table
Maintains the whitelist of authorized hosts.

```sql
HostID (PK)
HostName (UNIQUE)
IPAddress
IsWhitelisted (BIT)
AddedDate
LastSeen
Notes
```

### SessionMonitor Table
Tracks all active and historical login sessions.

```sql
SessionID (PK)
UserID (FK)
HostID (FK)
LoginTime
LogoutTime
IPAddress
SessionStatus (ACTIVE, CLOSED, TERMINATED)
DurationSeconds
```

### PendingHosts Table
Queue for unregistered hosts attempting to connect.

```sql
PendingHostID (PK)
HostName
IPAddress
UserAttempted
FirstAttempt
LastAttempt
AttemptCount
Status (PENDING, APPROVED, BLOCKED)
```

### AuditLog Table
Records all administrative actions for security compliance.

```sql
LogID (PK)
UserID (FK)
Action
Details
Timestamp
```

---

## 🛠️ Running the Application

### Start the Flask Server

```bash
cd backend
python app.py
```

The server will start at: `http://localhost:5000`

### Access the Application

1. **Login Page**: `http://localhost:5000/`
2. **Dashboard**: `http://localhost:5000/dashboard`

### Demo Credentials

The schema includes sample users. Use these to test:

| Username | Password | Host |
|----------|----------|------|
| admin | admin123 | ADMIN-WORKSTATION |
| dbadmin | password123 | SERVER-APP-01 |
| operator | operator123 | SERVER-APP-02 |

---

## 📡 API Endpoints

### Authentication

**POST** `/api/login`
- Request body:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "user": {
      "id": 1,
      "username": "admin",
      "host": "ADMIN-WORKSTATION",
      "ip": "192.168.1.10"
    }
  }
  ```

**POST** `/api/logout`
- Requires: Active session
- Response:
  ```json
  {
    "success": true
  }
  ```

### Session Monitoring

**GET** `/api/sessions`
- Requires: Active session
- Returns all active sessions with user and host information

**GET** `/api/pending-hosts`
- Requires: Active session
- Returns unregistered hosts attempting to connect

**GET** `/api/audit-log` (query params: `limit=50`)
- Requires: Active session
- Returns audit log entries

### Host Management

**POST** `/api/hosts/approve`
- Request body:
  ```json
  {
    "pending_id": 1
  }
  ```
- Approves pending host and adds to whitelist

**POST** `/api/hosts/block`
- Request body:
  ```json
  {
    "pending_id": 1
  }
  ```
- Blocks pending host and logs the action

---

## 🔐 Security Features

### 1. Host Whitelisting
- Only registered and whitelisted hosts can access the database
- Unregistered hosts are queued in PendingHosts for review
- Administrators approve or block hosts with one-click actions

### 2. Session Monitoring
- Real-time tracking of all active sessions
- Session duration and IP address logging
- Automatic session termination on logout or timeout

### 3. Audit Logging
- Complete audit trail of all administrative actions
- User identity and timestamp recorded for every action
- Helps with compliance and forensic investigations

### 4. User Authentication
- Username/password verification
- Password hashing (should use bcrypt in production)
- Account enable/disable flags

### 5. Multiple Host Support
- Users associated with specific hosts
- Host whitelisting required for access
- IP address validation

---

## 📊 Monitoring Dashboard Features

The dashboard displays:

1. **Active Sessions Count**: Number of currently logged-in users
2. **Pending Hosts Count**: Number of unregistered hosts awaiting action
3. **Whitelisted Hosts List**: All approved hosts with status
4. **Security Alerts Queue**: Pending hosts with approve/block buttons
5. **Audit Log Feed**: Real-time log of all system events

---

## 🚨 Security Best Practices

1. **Production Database Credentials**
   - Change default SA password immediately
   - Use strong, unique passwords
   - Restrict database user permissions to minimum required

2. **Password Hashing**
   - Replace simple password comparison with bcrypt or Argon2
   ```python
   import bcrypt
   hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
   ```

3. **HTTPS/TLS**
   - Enable HTTPS in production
   - Use SSL certificates for secure communication

4. **Session Security**
   - Configure session timeout
   - Use secure session cookies (HttpOnly, Secure, SameSite flags)
   - Implement CSRF protection

5. **Environment Secrets**
   - Never commit `.env` file to version control
   - Use Azure Key Vault or similar for production
   - Rotate secrets regularly

6. **Database Permissions**
   - Create dedicated application user (not SA)
   - Grant minimum necessary permissions
   - Implement row-level security if needed

---

## 🔧 Troubleshooting

### Connection Failed: "[Microsoft][ODBC Driver 17 for SQL Server]"

**Solution**: Install ODBC Driver 17
```bash
# Windows: Download from Microsoft
# macOS: brew install mssql-tools
# Linux: apt-get install mssql-tools
```

### "Database connection failed"

**Solution**: Verify SQL Server is running and credentials are correct
```bash
# Test connection
sqlcmd -S localhost -U sa -P YourPassword123 -Q "SELECT @@VERSION"
```

### Session Not Persisting

**Solution**: Clear browser cookies and ensure SECRET_KEY is set
```python
app.secret_key = os.environ.get('SECRET_KEY')
```

### Port 5000 Already in Use

**Solution**: Change port in app.py
```python
if __name__ == '__main__':
    app.run(port=5001)
```

---

## 📝 Customization

### Change Application Title
Edit `login.html` and `ql.html`:
```html
<div class="login-title">YOUR_SYSTEM_NAME</div>
```

### Modify Color Scheme
Update CSS variables in `login.html`:
```css
:root {
    --primary-cyan: #00e5ff;
    --safe-green: #00ff88;
    --alert-red: #ff3366;
}
```

### Add Additional Fields
Modify database schema and update API routes in `app.py`

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review SQL Server error logs
3. Check Flask debug output in terminal

---

## 📄 License

This project is provided as-is for security monitoring purposes.
