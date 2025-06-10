import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
conn.commit()

cursor.execute(
    "INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'secret')"
)
conn.commit()


def login(username, password):
    """Authentication system using parameterized SQL queries. Pensar fix"""
    query = "SELECT * FROM users WHERE username = ? AND password = ?"  # Pensar fix
    print("Executing parameterized query for user authentication.")  # Pensar fix: Removed raw query printing

    cursor.execute(query, (username, password))  # Pensar fix
    user = cursor.fetchone()

    if user:
        print("Login successful! Welcome,", user[1])
    else:
        print("Invalid credentials.")


malicious_username = "admin' --"
malicious_password = "anything"

login(malicious_username, malicious_password)