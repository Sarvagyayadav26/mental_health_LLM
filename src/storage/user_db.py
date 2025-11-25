import sqlite3
import os

DB_PATH = "user_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    age INTEGER,
    sex TEXT,
    password_hash TEXT,
    usage_count INTEGER DEFAULT 0
)
""")

    conn.commit()
    conn.close()

def create_user(email, age, sex):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (email, age, sex, usage_count) VALUES (?, ?, ?, 0)",
                   (email, age, sex))
    conn.commit()
    conn.close()

def get_user(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, age, sex, password_hash, usage_count
        FROM users
        WHERE email=?
    """, (email,))
    result = cursor.fetchone()
    conn.close()
    return result


def increment_usage(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET usage_count = usage_count + 1 WHERE email=?", (email,))
    conn.commit()
    conn.close()

def get_usage(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT usage_count FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0
