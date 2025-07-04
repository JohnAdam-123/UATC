import sqlite3
import hashlib
import os
import json

DB_NAME = "data/students.db"
SESSION_FILE = "session.json"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create students table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            course TEXT,
            ca REAL,
            se REAL,
            total REAL,
            grade TEXT,
            status TEXT
        )
    """)

    # Create users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            role TEXT
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16).hex()
    hash_obj = hashlib.sha256((password + salt).encode())
    return hash_obj.hexdigest(), salt


def verify_password(stored_hash, stored_salt, input_password):
    input_hash, _ = hash_password(input_password, stored_salt)
    return stored_hash == input_hash


def save_session(user_id, username, role):
    session = {"id": user_id, "username": username, "role": role}
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)


def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None


def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
