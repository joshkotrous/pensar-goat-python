import sqlite3
import hashlib

def hash_password(password):
    """Returns a SHA-256 hash of the password as a hex string."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
conn.commit()

# Insert default user admin with hashed password
username = 'admin'
plain_password = 'secret'
hashed_password = hash_password(plain_password)
cursor.execute(
    "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, hashed_password)
)
conn.commit()


def login(username, password):
    """Authentication system using hashed passwords."""
    hashed_input_password = hash_password(password)
    query = (
        "SELECT * FROM users WHERE username = ? AND password = ?"
    )
    print(f"Executing Query: {query} with parameters ({username!r}, <hashed>)")

    cursor.execute(query, (username, hashed_input_password))
    user = cursor.fetchone()

    if user:
        print("Login successful! Welcome,", user[1])
    else:
        print("Invalid credentials.")


malicious_username = "admin' --"
malicious_password = "anything"

login(malicious_username, malicious_password)
