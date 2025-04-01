import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
from flask import escape  # Added import for escape function
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse  # Added for URL parsing
import os  # Added for environment variable access

app = flask.Flask(__name__)

# ======== 1. SQL Injection Vulnerability ========
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
conn.commit()


@app.route("/login")
def login():
    """Fixed SQL Injection vulnerability by using parameterized queries"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {escape(user_input)}!</h1>"  # User input is now escaped to prevent XSS
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Safe YAML loading"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safer yaml.safe_load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF attacks"""
    url = flask.request.args.get("url")
    
    # Validate URL
    if not url:
        return "Error: No URL provided", 400
    
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Validate scheme
    if parsed_url.scheme not in ['http', 'https']:
        return "Error: Only HTTP/HTTPS URLs are allowed", 400
    
    # Create a list of allowed domains
    allowed_domains = ['example.com', 'api.example.com', 'trusted-domain.com']
    
    # Check if domain is in allowed list
    if parsed_url.netloc not in allowed_domains:
        return f"Error: Domain {parsed_url.netloc} is not allowed", 403
    
    # If all checks pass, proceed with the request
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """SSH connection with proper host key verification"""
    ssh = paramiko.SSHClient()
    # Load system host keys for verification
    ssh.load_system_host_keys()
    # Use RejectPolicy to reject connections to unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("example-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        # Handle SSH exceptions including unknown host keys
        return f"SSH Connection Error: {str(e)}"


if __name__ == "__main__":
    # Use environment variable to control debug mode
    # Default to False for production safety
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)