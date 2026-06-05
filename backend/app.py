from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import pyodbc
import os
import logging

TZ_OFFSET = timezone(timedelta(hours=7))  # Asia/Bangkok UTC+7

load_dotenv()

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL Server Configuration
SQL_SERVER = os.environ.get('SQL_SERVER', 'localhost')
SQL_DATABASE = os.environ.get('SQL_DATABASE', 'master')
SQL_USER = os.environ.get('SQL_USER', 'sa')
SQL_PASSWORD = os.environ.get('SQL_PASSWORD', 'YourPassword123')

def get_db_connection():
    """Create SQL Server connection"""
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USER};PWD={SQL_PASSWORD}'
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# No authentication required - direct access to monitoring

# ==================== SESSION MONITORING ====================

@app.route('/api/sessions', methods=['GET'])
def get_active_sessions():
    """Get all active SQL Server sessions from sys.dm_exec_sessions"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                s.session_id,
                s.login_name,
                s.host_name,
                c.client_net_address,
                s.program_name,
                s.login_time,
                s.last_request_start_time,
                CASE WHEN r.HostID IS NOT NULL THEN 1 ELSE 0 END as is_whitelisted
            FROM sys.dm_exec_sessions s
            LEFT JOIN sys.dm_exec_connections c ON s.session_id = c.session_id
            LEFT JOIN RegisteredHosts r ON s.host_name = r.HostName AND r.IsWhitelisted = 1
            WHERE s.session_id > 50
            ORDER BY s.login_time DESC
        ''')

        sessions = []
        for row in cursor.fetchall():
            session_id, login_name, host_name, ip_address, app_name, login_time, last_request, is_whitelisted = row
            sessions.append({
                'session_id': session_id,
                'login_name': login_name or 'N/A',
                'host_name': host_name or 'N/A',
                'ip_address': ip_address or 'N/A',
                'application': app_name or '.Net SqlClient Data Provider',
                'login_time': login_time.isoformat() if login_time else None,
                'last_request': last_request.isoformat() if last_request else None,
                'is_whitelisted': bool(is_whitelisted)
            })

        return jsonify({
            'success': True,
            'count': len(sessions),
            'sessions': sessions
        }), 200

    except Exception as e:
        logger.error(f"Session query error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()

@app.route('/api/pending-hosts', methods=['GET'])
def get_pending_hosts():
    """Get unregistered hosts attempting to connect"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                PendingHostID,
                HostName,
                IPAddress,
                UserAttempted,
                FirstAttempt,
                LastAttempt,
                AttemptCount,
                Status
            FROM PendingHosts
            WHERE Status = 'PENDING'
            ORDER BY LastAttempt DESC
        ''')

        pending = []
        for row in cursor.fetchall():
            pending.append({
                'pending_id': row[0],
                'host_name': row[1],
                'ip_address': row[2],
                'user_attempted': row[3],
                'first_attempt': row[4].isoformat() if row[4] else None,
                'last_attempt': row[5].isoformat() if row[5] else None,
                'attempt_count': row[6],
                'status': row[7]
            })

        return jsonify({
            'success': True,
            'count': len(pending),
            'pending_hosts': pending
        }), 200

    except Exception as e:
        logger.error(f"Pending hosts query error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()

# ==================== HOST MANAGEMENT ====================

@app.route('/api/hosts/approve', methods=['POST'])
def approve_host():
    """Approve a pending host and add to whitelist"""
    data = request.get_json()
    pending_id = data.get('pending_id')

    if not pending_id:
        return jsonify({'error': 'pending_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Get pending host details
        cursor.execute('''
            SELECT HostName, IPAddress FROM PendingHosts WHERE PendingHostID = ?
        ''', (pending_id,))

        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Pending host not found'}), 404

        host_name, ip_address = host_data

        # Add to RegisteredHosts
        cursor.execute('''
            INSERT INTO RegisteredHosts (HostName, IPAddress, IsWhitelisted, AddedDate)
            VALUES (?, ?, 1, GETDATE())
        ''', (host_name, ip_address))

        # Update pending status
        cursor.execute('''
            UPDATE PendingHosts SET Status = 'APPROVED' WHERE PendingHostID = ?
        ''', (pending_id,))

        # Log the action
        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'HOST_APPROVED', f'Host {host_name} ({ip_address}) approved and whitelisted'))

        conn.commit()

        logger.info(f"Host approved: {host_name}")

        return jsonify({
            'success': True,
            'message': f'Host {host_name} approved'
        }), 200

    except Exception as e:
        logger.error(f"Host approval error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()

@app.route('/api/hosts/block', methods=['POST'])
def block_host():
    """Block a pending host and terminate sessions"""
    data = request.get_json()
    pending_id = data.get('pending_id')

    if not pending_id:
        return jsonify({'error': 'pending_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Get pending host details
        cursor.execute('''
            SELECT HostName, IPAddress FROM PendingHosts WHERE PendingHostID = ?
        ''', (pending_id,))

        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Pending host not found'}), 404

        host_name, ip_address = host_data

        # Update pending status
        cursor.execute('''
            UPDATE PendingHosts SET Status = 'BLOCKED' WHERE PendingHostID = ?
        ''', (pending_id,))

        # Log the action
        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'HOST_BLOCKED', f'Host {host_name} ({ip_address}) blocked'))

        conn.commit()

        logger.info(f"Host blocked: {host_name}")

        return jsonify({
            'success': True,
            'message': f'Host {host_name} blocked'
        }), 200

    except Exception as e:
        logger.error(f"Host block error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()

@app.route('/api/hosts/cancel', methods=['POST'])
def cancel_host():
    """Cancel/dismiss a pending host from the queue"""
    data = request.get_json()
    pending_id = data.get('pending_id')

    if not pending_id:
        return jsonify({'error': 'pending_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT HostName, IPAddress FROM PendingHosts WHERE PendingHostID = ?
        ''', (pending_id,))
        
        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Pending host not found'}), 404
            
        host_name, ip_address = host_data

        cursor.execute('''
            UPDATE PendingHosts SET Status = 'CANCELED' WHERE PendingHostID = ?
        ''', (pending_id,))

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'HOST_CANCELED', f'Host {host_name} ({ip_address}) flagging canceled'))

        conn.commit()
        
        logger.info(f"Host canceled: {host_name}")
        return jsonify({'success': True, 'message': f'Host {host_name} canceled'}), 200

    except Exception as e:
        logger.error(f"Host cancel error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()

@app.route('/api/hosts/unblock', methods=['POST'])
def unblock_host():
    """Unblock a blacklisted host (moves it back to pending or canceled)"""
    data = request.get_json()
    pending_id = data.get('pending_id')

    if not pending_id:
        return jsonify({'error': 'pending_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT HostName, IPAddress FROM PendingHosts WHERE PendingHostID = ?
        ''', (pending_id,))
        
        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Pending host not found'}), 404
            
        host_name, ip_address = host_data

        # Set status back to CANCELED instead of BLOCKED
        cursor.execute('''
            UPDATE PendingHosts SET Status = 'CANCELED' WHERE PendingHostID = ?
        ''', (pending_id,))

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'HOST_UNBLOCKED', f'Host {host_name} ({ip_address}) was unblocked'))

        conn.commit()
        
        logger.info(f"Host unblocked: {host_name}")
        return jsonify({'success': True, 'message': f'Host {host_name} unblocked'}), 200

    except Exception as e:
        logger.error(f"Host unblock error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()

@app.route('/api/audit-log', methods=['GET'])
def get_audit_log():
    """Get audit log of all administrative actions"""
    limit = request.args.get('limit', 50, type=int)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT TOP (?) LogID, UserID, Action, Details, Timestamp
            FROM AuditLog
            ORDER BY Timestamp DESC
        ''', (limit,))

        logs = []
        for row in cursor.fetchall():
            logs.append({
                'log_id': row[0],
                'user_id': row[1],
                'action': row[2],
                'details': row[3],
                'timestamp': row[4].isoformat() if row[4] else None
            })

        return jsonify({
            'success': True,
            'count': len(logs),
            'logs': logs
        }), 200

    except Exception as e:
        logger.error(f"Audit log query error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()

@app.route('/api/sessions/kill', methods=['POST'])
def kill_session():
    """Kill a specific SQL Server session"""
    data = request.get_json()
    try:
        session_id = int(data.get('session_id', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid session_id'}), 400

    if session_id <= 50:
        return jsonify({'error': 'Cannot kill system session'}), 403

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(f'KILL {session_id}')   # session_id validated as int above

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'SESSION_KILLED', f'Session {session_id} forcibly terminated'))
        conn.commit()

        logger.info(f"Session killed: {session_id}")
        return jsonify({'success': True, 'message': f'Session {session_id} killed'}), 200

    except Exception as e:
        logger.error(f"Kill session error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/sessions/flag', methods=['POST'])
def flag_session_host():
    """Flag a host from an active session into the pending-hosts queue"""
    data = request.get_json()
    host_name  = data.get('host_name')
    ip_address = data.get('ip_address', 'N/A')
    login_name = data.get('login_name', 'N/A')

    if not host_name:
        return jsonify({'error': 'host_name required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Check if already whitelisted
        cursor.execute('''
            SELECT HostID FROM RegisteredHosts WHERE HostName = ? AND IsWhitelisted = 1
        ''', (host_name,))
        if cursor.fetchone():
            return jsonify({'error': f'{host_name} is already whitelisted and safe'}), 400

        cursor.execute('''
            SELECT PendingHostID FROM PendingHosts WHERE HostName = ? AND Status = 'PENDING'
        ''', (host_name,))
        if cursor.fetchone():
            return jsonify({'error': f'{host_name} already in pending queue'}), 409

        cursor.execute('''
            INSERT INTO PendingHosts (HostName, IPAddress, UserAttempted, FirstAttempt, LastAttempt, AttemptCount, Status)
            VALUES (?, ?, ?, GETDATE(), GETDATE(), 1, 'PENDING')
        ''', (host_name, ip_address, login_name))

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'HOST_FLAGGED', f'Host {host_name} ({ip_address}) flagged for review'))

        conn.commit()

        logger.info(f"Host flagged: {host_name}")
        return jsonify({'success': True, 'message': f'Host {host_name} flagged for review'}), 200

    except Exception as e:
        logger.error(f"Flag host error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/whitelist', methods=['GET'])
def get_whitelist():
    """Get all whitelisted/registered hosts"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT HostID, HostName, IPAddress, IsWhitelisted, AddedDate
            FROM RegisteredHosts
            WHERE IsWhitelisted = 1
            ORDER BY AddedDate DESC
        ''')
        hosts = []
        for row in cursor.fetchall():
            hosts.append({
                'host_id': row[0],
                'host_name': row[1] or 'N/A',
                'ip_address': row[2] or 'N/A',
                'is_whitelisted': bool(row[3]),
                'added_date': row[4].isoformat() if row[4] else None
            })
        return jsonify({'success': True, 'count': len(hosts), 'whitelist': hosts}), 200
    except Exception as e:
        logger.error(f"Whitelist query error: {e}")
        return jsonify({'error': 'Server error', 'detail': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/blacklist', methods=['GET'])
def get_blacklist():
    """Get all blocked/blacklisted hosts"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT PendingHostID, HostName, IPAddress, UserAttempted,
                   FirstAttempt, LastAttempt, AttemptCount, Status
            FROM PendingHosts
            WHERE Status = 'BLOCKED'
            ORDER BY LastAttempt DESC
        ''')
        hosts = []
        for row in cursor.fetchall():
            hosts.append({
                'pending_id': row[0],
                'host_name': row[1] or 'N/A',
                'ip_address': row[2] or 'N/A',
                'user_attempted': row[3] or 'N/A',
                'first_attempt': row[4].isoformat() if row[4] else None,
                'last_attempt': row[5].isoformat() if row[5] else None,
                'attempt_count': row[6],
                'status': row[7]
            })
        return jsonify({'success': True, 'count': len(hosts), 'blacklist': hosts}), 200
    except Exception as e:
        logger.error(f"Blacklist query error: {e}")
        return jsonify({'error': 'Server error', 'detail': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/whitelist/update', methods=['POST'])
def update_whitelist_host():
    """Update whitelist host status and notes"""
    data = request.get_json()
    registered_id = data.get('registered_id')
    status = data.get('status', 'active')
    notes = data.get('notes', '')

    if not registered_id:
        return jsonify({'error': 'registered_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT HostName, IPAddress FROM RegisteredHosts WHERE RegisteredHostID = ?
        ''', (registered_id,))

        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Host not found'}), 404

        host_name, ip_address = host_data

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'WHITELIST_UPDATED', f'Host {host_name} ({ip_address}) status updated to {status}. Notes: {notes}'))

        conn.commit()

        logger.info(f"Whitelist host updated: {host_name}")

        return jsonify({
            'success': True,
            'message': f'Host {host_name} updated'
        }), 200

    except Exception as e:
        logger.error(f"Update whitelist error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()


@app.route('/api/blacklist/update', methods=['POST'])
def update_blacklist_host():
    """Update blacklist host status and notes"""
    data = request.get_json()
    pending_id = data.get('pending_id')
    status = data.get('status', 'active')
    notes = data.get('notes', '')

    if not pending_id:
        return jsonify({'error': 'pending_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT HostName, IPAddress FROM PendingHosts WHERE PendingHostID = ?
        ''', (pending_id,))

        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Host not found'}), 404

        host_name, ip_address = host_data

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'BLACKLIST_UPDATED', f'Host {host_name} ({ip_address}) status updated to {status}. Notes: {notes}'))

        conn.commit()

        logger.info(f"Blacklist host updated: {host_name}")

        return jsonify({
            'success': True,
            'message': f'Host {host_name} updated'
        }), 200

    except Exception as e:
        logger.error(f"Update blacklist error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()


@app.route('/api/whitelist/remove', methods=['POST'])
def remove_from_whitelist():
    """Remove a host from whitelist"""
    data = request.get_json()
    registered_id = data.get('registered_id')

    if not registered_id:
        return jsonify({'error': 'registered_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT HostName, IPAddress FROM RegisteredHosts WHERE RegisteredHostID = ?
        ''', (registered_id,))

        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Host not found'}), 404

        host_name, ip_address = host_data

        cursor.execute('''
            DELETE FROM RegisteredHosts WHERE RegisteredHostID = ?
        ''', (registered_id,))

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'WHITELIST_REMOVED', f'Host {host_name} ({ip_address}) removed from whitelist'))

        conn.commit()

        logger.info(f"Host removed from whitelist: {host_name}")

        return jsonify({
            'success': True,
            'message': f'Host {host_name} removed from whitelist'
        }), 200

    except Exception as e:
        logger.error(f"Remove from whitelist error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()


@app.route('/api/blacklist/remove', methods=['POST'])
def remove_from_blacklist():
    """Remove a host from blacklist"""
    data = request.get_json()
    pending_id = data.get('pending_id')

    if not pending_id:
        return jsonify({'error': 'pending_id required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT HostName, IPAddress FROM PendingHosts WHERE PendingHostID = ?
        ''', (pending_id,))

        host_data = cursor.fetchone()
        if not host_data:
            return jsonify({'error': 'Host not found'}), 404

        host_name, ip_address = host_data

        cursor.execute('''
            DELETE FROM PendingHosts WHERE PendingHostID = ?
        ''', (pending_id,))

        cursor.execute('''
            INSERT INTO AuditLog (UserID, Action, Details, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ''', (None, 'BLACKLIST_REMOVED', f'Host {host_name} ({ip_address}) removed from blacklist'))

        conn.commit()

        logger.info(f"Host removed from blacklist: {host_name}")

        return jsonify({
            'success': True,
            'message': f'Host {host_name} removed from blacklist'
        }), 200

    except Exception as e:
        logger.error(f"Remove from blacklist error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()


@app.route('/api/databases', methods=['GET'])
def get_all_databases():
    """Get list of all databases in SQL Server instance"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                name,
                database_id,
                state_desc,
                recovery_model_desc,
                create_date
            FROM sys.databases
            WHERE database_id > 4
            ORDER BY name
        ''')

        databases = []
        for row in cursor.fetchall():
            databases.append({
                'name': row[0],
                'database_id': row[1],
                'state': row[2],
                'recovery_model': row[3],
                'create_date': row[4].isoformat() if row[4] else None
            })

        return jsonify({
            'success': True,
            'count': len(databases),
            'databases': databases
        }), 200

    except Exception as e:
        logger.error(f"Get databases error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()


@app.route('/api/sessions/all-databases', methods=['GET'])
def get_sessions_all_databases():
    """Get active sessions from ALL databases in SQL Server"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                s.session_id,
                s.login_name,
                s.host_name,
                c.client_net_address,
                s.program_name,
                s.login_time,
                s.last_request_start_time,
                db_name(s.database_id) as database_name,
                s.database_id,
                s.status,
                CASE WHEN r.HostID IS NOT NULL THEN 1 ELSE 0 END as is_whitelisted
            FROM sys.dm_exec_sessions s
            LEFT JOIN sys.dm_exec_connections c ON s.session_id = c.session_id
            LEFT JOIN RegisteredHosts r ON s.host_name = r.HostName AND r.IsWhitelisted = 1
            WHERE s.session_id > 50
            ORDER BY db_name(s.database_id), s.login_time DESC
        ''')

        sessions = []
        for row in cursor.fetchall():
            session_id, login_name, host_name, ip_address, app_name, login_time, last_request, db_name, db_id, status, is_whitelisted = row
            sessions.append({
                'session_id': session_id,
                'login_name': login_name or 'N/A',
                'host_name': host_name or 'N/A',
                'ip_address': ip_address or 'N/A',
                'application': app_name or '.Net SqlClient Data Provider',
                'login_time': login_time.isoformat() if login_time else None,
                'last_request': last_request.isoformat() if last_request else None,
                'database_name': db_name or 'N/A',
                'database_id': db_id,
                'status': status,
                'is_whitelisted': bool(is_whitelisted)
            })

        return jsonify({
            'success': True,
            'count': len(sessions),
            'sessions': sessions
        }), 200

    except Exception as e:
        logger.error(f"Get sessions all databases error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()


@app.route('/api/metrics/by-database', methods=['GET'])
def get_metrics_by_database():
    """Get session metrics grouped by database"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Get sessions per database
        cursor.execute('''
            SELECT
                db_name(s.database_id) as database_name,
                COUNT(*) as session_count,
                COUNT(DISTINCT s.login_name) as unique_users,
                COUNT(DISTINCT s.host_name) as unique_hosts,
                MIN(s.login_time) as oldest_session,
                MAX(s.login_time) as newest_session
            FROM sys.dm_exec_sessions s
            WHERE s.session_id > 50
            GROUP BY s.database_id
            ORDER BY session_count DESC
        ''')

        metrics = []
        for row in cursor.fetchall():
            db_name, session_count, unique_users, unique_hosts, oldest, newest = row
            metrics.append({
                'database_name': db_name or 'Unknown',
                'session_count': session_count,
                'unique_users': unique_users,
                'unique_hosts': unique_hosts,
                'oldest_session': oldest.isoformat() if oldest else None,
                'newest_session': newest.isoformat() if newest else None
            })

        # Get total stats
        cursor.execute('''
            SELECT
                COUNT(*) as total_sessions,
                COUNT(DISTINCT s.login_name) as total_users,
                COUNT(DISTINCT s.host_name) as total_hosts,
                COUNT(DISTINCT s.database_id) as total_databases
            FROM sys.dm_exec_sessions s
            WHERE s.session_id > 50
        ''')

        total_row = cursor.fetchone()
        total_stats = {
            'total_sessions': total_row[0],
            'total_users': total_row[1],
            'total_hosts': total_row[2],
            'total_databases': total_row[3]
        }

        return jsonify({
            'success': True,
            'by_database': metrics,
            'totals': total_stats
        }), 200

    except Exception as e:
        logger.error(f"Get metrics by database error: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        conn.close()


@app.route('/api/server-time', methods=['GET'])
def get_server_time():
    """Return current server time in Thai timezone (UTC+7)"""
    now_thai = datetime.now(TZ_OFFSET)
    return jsonify({
        'success': True,
        'iso': now_thai.isoformat(),
        'display': now_thai.strftime('%H:%M:%S'),
        'date': now_thai.strftime('%Y-%m-%d'),
        'timezone': 'Asia/Bangkok (UTC+7)'
    }), 200


@app.route('/')
def index():
    """Serve dashboard directly"""
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5090))
    app.run(debug=True, host='0.0.0.0', port=port)
