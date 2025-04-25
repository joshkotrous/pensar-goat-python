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
    """Secure authentication system using parameterized SQL queries."""
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    print(f"Executing Query: {query} with parameters ({username!r}, {password!r})")

    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        print("Login successful! Welcome,", user[1])
    else:
        print("Invalid credentials.")


malicious_username = "admin' --"
malicious_password = "anything"

login(malicious_username, malicious_password)
