import sqlite3
from datetime import datetime
from typing import List, Dict

class DatabaseHandler:
    def __init__(self, db_path: str = "messages.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    message_text TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            # Settings table with chat_id support
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    chat_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (chat_id, key)
                )
            ''')
            conn.commit()

    def store_message(self, chat_id: int, user_id: int, username: str, message_text: str, timestamp: datetime):
        """Store a new message in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (chat_id, user_id, username, message_text, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (chat_id, user_id, username, message_text, timestamp))
            conn.commit()

    def get_recent_messages(self, chat_id: int, limit: int = 10) -> List[Dict]:
        """Retrieve recent messages for a specific chat"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages
                WHERE chat_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (chat_id, limit))

            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'chat_id': row['chat_id'],
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'message_text': row['message_text'],
                    'timestamp': row['timestamp']
                })

            return messages

    def get_setting(self, chat_id: int, key: str, default: str = None) -> str:
        """Get a setting value by chat_id and key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE chat_id = ? AND key = ?', (chat_id, key))
            result = cursor.fetchone()
            return result[0] if result else default

    def set_setting(self, chat_id: int, key: str, value: str):
        """Set a setting value for a specific chat"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO settings (chat_id, key, value) VALUES (?, ?, ?)',
                          (chat_id, key, value))
            conn.commit()
