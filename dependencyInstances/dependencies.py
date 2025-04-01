import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
from flask import escape  # Added for XSS protection
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse  # Added for URL parsing
import os  # Added for environment variable access

app = flask.Flask(__name__)

# Allowlist of permitted domains for external requests
ALLOWED_DOMAINS = {
    'api.example.com',
    'data.example.org',
    'public-api.example.net'
}

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
    """Fixed SQL Injection vulnerability"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    # Use parameterized query instead of string interpolation
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Secured against XSS"""
    user_input = flask.request.args.get("name", "")
    user_input = escape(user_input)  # Escape user input to prevent XSS
    return (
        f"<h1>Welcome, {user_input}!</h1>"
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """No longer vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe yaml.safe_load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    try:
        tree = ET.fromstring(xml_data, parser)
        return ET.tostring(tree)
    except ET.XMLSyntaxError:
        return "Invalid XML", 400


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fetch content from a URL with proper validation"""
    url = flask.request.args.get("url")
    
    # Validate the URL
    if not url or not isinstance(url, str):
        return "Invalid URL", 400
        
    # Parse the URL to extract components
    parsed_url = urlparse(url)
    
    # Check for allowed schemes
    if parsed_url.scheme not in ('http', 'https'):
        return "Error: Only HTTP/HTTPS URLs are allowed", 403
    
    # Extract hostname
    hostname = parsed_url.netloc.split(':')[0]
    
    # Check if the hostname is in the allowlist
    if hostname not in ALLOWED_DOMAINS:
        return f"Error: Domain not in allowlist", 403
    
    try:
        # Make the request with redirects disabled
        response = requests.get(url, allow_redirects=False)
        
        # If there was a redirect, return an error
        if response.is_redirect:
            return "Redirects are not allowed", 403
        
        return response.text
    except Exception as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Connect to SSH server with proper host key verification"""
    ssh = paramiko.SSHClient()
    # Load system host keys
    ssh.load_system_host_keys()
    # Use RejectPolicy instead of AutoAddPolicy for better security
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        # Handle SSH exceptions properly
        return f"SSH connection error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    # Get debug mode from environment variable, defaulting to False for security
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)