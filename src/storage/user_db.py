import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "user_data.db")


def init_db():
    """Initialize the SQLite database and create tables with correct schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users;")  # remove old incorrect table

    cursor.execute("""
        CREATE TABLE users (
            email TEXT PRIMARY KEY,
            age INTEGER,
            sex TEXT,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


def create_user(email: str, age: int, sex: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (email, age, sex, usage_count)
        VALUES (?, ?, ?, 0)
    """, (email, age, sex))

    conn.commit()
    conn.close()


def get_user(email: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT email, age, sex, usage_count FROM users WHERE email = ?;", (email,))
    result = cursor.fetchone()

    conn.close()
    return result


def save_message(email: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (email, role, content)
        VALUES (?, ?, ?);
    """, (email, role, content))

    conn.commit()
    conn.close()


def get_messages(email: str, limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, timestamp
        FROM messages
        WHERE email = ?
        ORDER BY id DESC
        LIMIT ?;
    """, (email, limit))

    rows = cursor.fetchall()
    conn.close()

    return rows[::-1]
