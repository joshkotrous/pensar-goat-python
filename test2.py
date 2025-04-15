import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from markupsafe import escape  # Added for XSS protection

app = flask.Flask(__name__)

# ======== 1. SQL Injection Vulnerability ========
# ======== 1. SQL Injection Vulnerability ========
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")


@app.route("/login")
def login():
    """Fixed SQL Injection vulnerability by using parameterized query"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    # Use parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    # Sanitize user input to prevent XSS
    user_input = escape(user_input)
    return (
        f"<h1>Welcome, {user_input}!</h1>"
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Loads configuration safely"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe YAML loading
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Vulnerable to credential leakage in redirects"""
    url = flask.request.args.get("url")
    response = requests.get(url, allow_redirects=True)
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Connects to an SSH server with proper host key verification."""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load system host keys
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())  # Reject unknown servers
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
    return stdout.read()
    return stdout.read()


if __name__ == "__main__":
    app.run(debug=True)
    app.run(debug=debug_mode)
if __name__ == "__main__":
    app.run(debug=True)