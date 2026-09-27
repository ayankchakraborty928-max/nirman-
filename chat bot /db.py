import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(__file__), "nirman.db")

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    # Table for Organization/Entity details
    conn.execute("""CREATE TABLE IF NOT EXISTS entities(
        entity_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        entity_type TEXT,
        sector TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    # Table for checklist progress
    conn.execute("""CREATE TABLE IF NOT EXISTS sessions(
        session_id TEXT PRIMARY KEY,
        answers TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    # Table for required documents
    conn.execute("""CREATE TABLE IF NOT EXISTS documents(
        session_id TEXT,
        approval_id TEXT,
        approval_name TEXT,
        status TEXT DEFAULT 'need'
    )""")
    conn.commit()
    conn.close()

def save_entity(entity_id, data):
    conn = get_conn()
    conn.execute(
        "INSERT INTO entities(entity_id, name, email, entity_type, sector) VALUES (?, ?, ?, ?, ?)",
        (entity_id, data['name'], data['email'], data['entity_type'], data['sector'])
    )
    conn.commit()
    conn.close()

def save_session(session_id, answers):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO sessions(session_id, answers) VALUES (?, ?)",
                 (session_id, json.dumps(answers)))
    conn.commit()
    conn.close()

def save_documents(session_id, required):
    conn = get_conn()
    conn.execute("DELETE FROM documents WHERE session_id = ?", (session_id,))
    for item in required:
        conn.execute("INSERT INTO documents(session_id, approval_id, approval_name) VALUES (?, ?, ?)",
                     (session_id, item["id"], item["approval"]))
    conn.commit()
    conn.close()