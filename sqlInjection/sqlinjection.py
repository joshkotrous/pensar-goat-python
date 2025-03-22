import sqlite3

# Insecure database connection (no ORM, raw queries)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create a users table (for testing)
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
conn.commit()

# Insert a test user (username: admin, password: secret)
cursor.execute(
    "INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'secret')"
)
conn.commit()


def login(username, password):
    """Secure authentication system using parameterized SQL queries."""
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    
    # Using parameterized query instead of string interpolation
    # Not revealing the actual query for security reasons
    print("Executing authentication query")
    
    cursor.execute(query, (username, password))
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