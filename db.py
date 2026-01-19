import sqlite3

DB_NAME = "attendance.db"

def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    db = connect()
    cur = db.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS admins (
        telegram_id INTEGER PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS parents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE
    );

    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        group_id INTEGER,
        parent_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        date TEXT,
        lesson_number INTEGER,
        started_at TEXT
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id INTEGER,
        student_id INTEGER,
        status TEXT,
        check_in_time TEXT
    );
    """)

    db.commit()
    db.close()
