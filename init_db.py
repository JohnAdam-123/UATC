import sqlite3

conn = sqlite3.connect("data/students.db")
cursor = conn.cursor()

# Create levels table
cursor.execute("""
CREATE TABLE IF NOT EXISTS levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

# Create academic_years table
cursor.execute("""
CREATE TABLE IF NOT EXISTS academic_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year TEXT UNIQUE NOT NULL
)
""")

# Create semesters table
cursor.execute("""
CREATE TABLE IF NOT EXISTS semesters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

# Modify students table to support foreign keys
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    ca REAL,
    se REAL,
    total REAL,
    grade TEXT,
    status TEXT,
    level_id INTEGER,
    year_id INTEGER,
    semester_id INTEGER,
    FOREIGN KEY (level_id) REFERENCES levels(id),
    FOREIGN KEY (year_id) REFERENCES academic_years(id),
    FOREIGN KEY (semester_id) REFERENCES semesters(id)
)
""")

conn.commit()
conn.close()

print("✅ Database schema initialized.")
