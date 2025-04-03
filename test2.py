import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import os  # Added to access environment variables
from urllib.parse import urlparse  # Added for URL validation

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
    """Vulnerable to SQL Injection"""
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
    """Previously vulnerable to XSS - Fixed with input sanitization"""
    user_input = flask.request.args.get("name", "")
    # Sanitize user input to prevent XSS
    sanitized_input = flask.escape(user_input)
    return f"<h1>Welcome, {sanitized_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fetch content from validated external URLs"""
    url = flask.request.args.get("url")
    
    # Basic URL validation
    if not url or not url.startswith(("http://", "https://")):
        return "Invalid URL. Only HTTP/HTTPS protocols are allowed.", 400
    
    # Simple checks to prevent access to internal resources
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc.split(":", 1)[0]  # Remove port if present
    
    # Block localhost and common internal patterns
    if (hostname == "localhost" or 
        hostname == "127.0.0.1" or 
        hostname.startswith("192.168.") or
        hostname.startswith("10.") or
        hostname.startswith("172.16.") or
        hostname.endswith((".local", ".internal"))):
        return "Access to internal resources is not allowed.", 403
    
    try:
        # Disable redirects to prevent redirect-based attacks
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        # If it's a redirect, inform the user
        if response.is_redirect:
            return "The requested URL redirects to another location. Redirects are not allowed.", 403
            
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Secure SSH connection with proper host key verification"""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load system host keys
    # Reject unknown host keys instead of automatically accepting them
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        ssh.connect("server.example.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH connection error: {str(e)}"


if __name__ == "__main__":
    # Use environment variable to control debug mode
    # Defaults to False for security in production
    debug_mode = os.environ.get("FLASK_DEBUG", "").lower() == "true"
    app.run(debug=debug_mode)