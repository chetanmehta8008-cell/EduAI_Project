import sqlite3
import json
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "education_ai.db")

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE,
            content TEXT,
            flashcards TEXT,
            image_paths TEXT,
            difficulty TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    for migration in [
        "ALTER TABLE notes ADD COLUMN flashcards TEXT",
        "ALTER TABLE notes ADD COLUMN image_paths TEXT",
        "ALTER TABLE notes ADD COLUMN difficulty TEXT",
    ]:
        try:
            cursor.execute(migration)
        except Exception:
            pass
    conn.commit()
    conn.close()

def save_note(topic, content, flashcards=None, image_paths=None, difficulty=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO notes (topic, content, flashcards, image_paths, difficulty)
        VALUES (?, ?, ?, ?, ?)
    """, (
        topic,
        content,
        json.dumps(flashcards) if flashcards else None,
        json.dumps(image_paths) if image_paths else None,
        difficulty
    ))
    conn.commit()
    conn.close()

def get_note(topic):
    conn = get_connection()
    cursor = conn.cursor()
    create_table()
    cursor.execute("SELECT content, flashcards, image_paths, difficulty FROM notes WHERE topic = ?", (topic,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], json.loads(row[1]) if row[1] else [], json.loads(row[2]) if row[2] else [], row[3]
    return None, [], [], None

def get_all_topics():
    create_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT topic, difficulty, created_at FROM notes ORDER BY created_at DESC")
    except Exception:
        cursor.execute("SELECT topic, created_at FROM notes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [(row[0], None, row[1]) for row in rows]
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_topic(topic):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE topic = ?", (topic,))
    conn.commit()
    conn.close()