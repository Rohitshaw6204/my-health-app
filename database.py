import sqlite3

def init_db():
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    # Pipes hata di hain aur lines sahi kar di hain
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS records (username TEXT, date TEXT, sugar REAL, med_status TEXT)''')
    conn.commit()
    conn.close()

def add_record(username, date, sugar, med_status):
    conn = sqlite3.connect('medical_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO records VALUES (?, ?, ?, ?)", (username, date, sugar, med_status))
    conn.commit()
    conn.close()