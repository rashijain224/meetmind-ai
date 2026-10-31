import sqlite3
db_name = "meetmind.db"

def get_connection():
    return sqlite3.connect(db_name)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY AUTOINCREMENT,decision TEXT NOT NULL,speaker TEXT,
    meeting_title TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    conn.commit()
    conn.close()

def save_decision(decision, speaker, meeting_title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO decisions (decision, speaker, meeting_title)VALUES (?, ?, ?)""", (decision, speaker, meeting_title))

    conn.commit()
    conn.close()

def get_previous_decisions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT decision, speaker, meeting_title FROM decisions ORDER BY id DESC"
    )

    decisions = cursor.fetchall()
    conn.close()

    return decisions