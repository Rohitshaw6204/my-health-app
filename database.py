import sqlite3

def create_database():

    conn = sqlite3.connect("medical_data.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        record_date TEXT,
        blood_sugar REAL,
        activity TEXT
    )
    """)
    cur.execute("""
     CREATE TABLE IF NOT EXISTS user_profile(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER UNIQUE,
          name TEXT,
          age INTEGER,
          weight REAL,
          diabetes_type TEXT,
          email TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_user_history(user_id):

    conn = sqlite3.connect("medical_data.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT
        record_date,
        blood_sugar,
        activity
    FROM health_records
    WHERE user_id = ?
    ORDER BY id DESC
    """, (user_id,))

    records = cur.fetchall()

    conn.close()

    return records 
def save_profile(user_id, name, age, weight, diabetes_type, email):

    conn = sqlite3.connect("medical_data.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO user_profile
    (user_id, name, age, weight, diabetes_type, email)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, name, age, weight, diabetes_type, email))

    conn.commit()
    conn.close()


def get_profile(user_id):

    conn = sqlite3.connect("medical_data.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT name, age, weight, diabetes_type, email
    FROM user_profile
    WHERE user_id = ?
    """, (user_id,))

    profile = cur.fetchone()

    conn.close()

    return profile
