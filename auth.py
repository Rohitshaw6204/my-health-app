import sqlite3

DB_NAME = "medical_data.db"

def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        conn.commit()
        return True

    except:
        return False

    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect("medical_data.db")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE username=? AND password=?
        """,
        (username, password)
    )

    user = cur.fetchone()

    print("LOGIN RESULT:", user)

    conn.close()

    return user