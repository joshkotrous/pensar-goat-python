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

# SECURITY NOTICE: This code is for educational purposes to demonstrate SQL injection
# For a real application, NEVER store sensitive credentials in code and ALWAYS use parameterized queries

# Get demo credentials from environment variables or use defaults for demonstration
demo_username = os.environ.get("DEMO_USERNAME", "demo_user")
demo_password = os.environ.get("DEMO_PASSWORD", "demo_pass")

# Insert a test user using parameterized query (safer)
cursor.execute(
    "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
    (demo_username, demo_password)
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
malicious_username = f"{demo_username}' --"
malicious_password = "anything"

# Attempt login with SQL injection
login(malicious_username, malicious_password)