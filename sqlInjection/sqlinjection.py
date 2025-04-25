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
    """Vulnerable authentication system using raw SQL queries."""
    query = (
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    print(f"Executing Query: {query}")

    cursor.execute(query)
    user = cursor.fetchone()

    if user:
        print("Login successful! Welcome,", user[1])
    else:
        print("Invalid credentials.")


malicious_username = "admin' --"
malicious_password = "anything"

login(malicious_username, malicious_password)
