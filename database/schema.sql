-- SQL Server Database Schema for SQL Security HUD

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SqlSecurityHUD')
BEGIN
    CREATE DATABASE SqlSecurityHUD;
END
GO

USE SqlSecurityHUD;
GO


-- Create RegisteredHosts table
CREATE TABLE RegisteredHosts (
    HostID INT PRIMARY KEY IDENTITY(1,1),
    HostName NVARCHAR(100) UNIQUE NOT NULL,
    IPAddress NVARCHAR(45) NOT NULL,
    IsWhitelisted BIT DEFAULT 1,
    AddedDate DATETIME DEFAULT GETDATE(),
    LastSeen DATETIME,
    Notes NVARCHAR(MAX)
);

-- Create Users table
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(50) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    Email NVARCHAR(100),
    HostID INT,
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE(),
    LastLogin DATETIME,
    FOREIGN KEY (HostID) REFERENCES RegisteredHosts(HostID)
);

-- Create SessionMonitor table
CREATE TABLE SessionMonitor (
    SessionID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT NOT NULL,
    HostID INT NOT NULL,
    LoginTime DATETIME DEFAULT GETDATE(),
    LogoutTime DATETIME,
    IPAddress NVARCHAR(45),
    SessionStatus NVARCHAR(20) DEFAULT 'ACTIVE',
    DurationSeconds INT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (HostID) REFERENCES RegisteredHosts(HostID)
);

-- Create PendingHosts table
CREATE TABLE PendingHosts (
    PendingHostID INT PRIMARY KEY IDENTITY(1,1),
    HostName NVARCHAR(100),
    IPAddress NVARCHAR(45),
    UserAttempted NVARCHAR(100),
    FirstAttempt DATETIME DEFAULT GETDATE(),
    LastAttempt DATETIME DEFAULT GETDATE(),
    AttemptCount INT DEFAULT 1,
    Status NVARCHAR(20) DEFAULT 'PENDING'
);

-- Create AuditLog table
CREATE TABLE AuditLog (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    Action NVARCHAR(50) NOT NULL,
    Details NVARCHAR(MAX),
    Timestamp DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON Users(Username);
CREATE INDEX idx_sessions_userid ON SessionMonitor(UserID);
CREATE INDEX idx_sessions_status ON SessionMonitor(SessionStatus);
CREATE INDEX idx_pending_status ON PendingHosts(Status);
CREATE INDEX idx_audit_timestamp ON AuditLog(Timestamp);

-- Insert sample data
INSERT INTO RegisteredHosts (HostName, IPAddress, IsWhitelisted, LastSeen)
VALUES
    ('ADMIN-WORKSTATION', '192.168.1.10', 1, GETDATE()),
    ('SERVER-APP-01', '192.168.1.20', 1, GETDATE()),
    ('SERVER-APP-02', '192.168.1.21', 1, GETDATE()),
    ('HR-FRONTEND', '192.168.1.30', 1, GETDATE()),
    ('BACKUP-NODE', '192.168.1.40', 1, GETDATE());

-- Insert sample users (change passwords in production!)
INSERT INTO Users (Username, PasswordHash, Email, HostID, IsActive)
VALUES
    ('admin', 'admin123', 'admin@company.com', 1, 1),
    ('dbadmin', 'password123', 'dbadmin@company.com', 2, 1),
    ('operator', 'operator123', 'operator@company.com', 3, 1);

-- Insert sample session
INSERT INTO SessionMonitor (UserID, HostID, LoginTime, IPAddress, SessionStatus)
VALUES
    (1, 1, GETDATE(), '192.168.1.10', 'ACTIVE'),
    (2, 2, GETDATE(), '192.168.1.20', 'ACTIVE');

-- Insert sample audit logs
INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
VALUES
    (1, 'LOGIN', 'Admin logged in', GETDATE()),
    (1, 'SCAN_COMPLETED', 'System scan completed - 142 active hosts registered', DATEADD(MINUTE, -30, GETDATE()));
