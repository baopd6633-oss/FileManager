import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="server.db"):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        # Đảm bảo thư mục chứa file database tồn tại
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    status TEXT,
                    last_heartbeat TEXT,
                    ip_address TEXT,
                    port INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT,
                    event_type TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    timestamp TEXT,
                    received_at TEXT
                )
            """)
            conn.commit()

    def update_client_status(self, client_id, status, ip_address=None, port=None):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ip_address, port FROM clients WHERE client_id = ?", (client_id,))
            row = cursor.fetchone()
            if row:
                final_ip = ip_address if ip_address is not None else row[0]
                final_port = port if port is not None else row[1]
                cursor.execute("""
                    UPDATE clients 
                    SET status = ?, last_heartbeat = ?, ip_address = ?, port = ?
                    WHERE client_id = ?
                """, (status, now_str, final_ip, final_port, client_id))
            else:
                cursor.execute("""
                    INSERT INTO clients (client_id, status, last_heartbeat, ip_address, port)
                    VALUES (?, ?, ?, ?, ?)
                """, (client_id, status, now_str, ip_address, port))
            conn.commit()

    def update_client_heartbeat(self, client_id):
        self.update_client_status(client_id, "ONLINE")

    def save_event(self, client_id, event_type, file_name, file_path, timestamp):
        received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (client_id, event_type, file_name, file_path, timestamp, received_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (client_id, event_type, file_name, file_path, timestamp, received_at))
            conn.commit()
