import sqlite3
import os

# Insecure database connection (no ORM, raw queries)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create a users table (for testing)
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
conn.commit()

# For testing purposes, get test credentials from environment variables
# In a production environment, use a proper authentication system
test_username = os.environ.get("TEST_USERNAME")
test_password = os.environ.get("TEST_PASSWORD")

# Only insert test user if environment variables are set
if test_username and test_password:
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        (test_username, test_password)
    )
    conn.commit()


def login(username, password):
    """Vulnerable authentication system using raw SQL queries."""
    query = (
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    print(f"Executing Query: {query}")  # Debugging purpose (reveals injection point)

    cursor.execute(query)
    user = cursor.fetchone()

    if user:
        print("Login successful! Welcome,", user[1])
    else:
        print("Invalid credentials.")


# User input (simulating a hacker's attempt)
malicious_username = "admin' --"
malicious_password = "anything"

# Attempt login with SQL injection
login(malicious_username, malicious_password)