import sqlite3

conn = sqlite3.connect("medical_data.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cur.fetchall())

cur.execute("PRAGMA table_info(users)")
print("Users:", cur.fetchall())

conn.close()