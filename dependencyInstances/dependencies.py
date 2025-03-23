import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse
import re

app = flask.Flask(__name__)

# Allowlist configuration for SSRF protection
ALLOWED_DOMAINS = ["example.com", "api.example.com", "trusted-site.com"]
ALLOWED_SCHEMES = ["https"]  # Only allow HTTPS for security

def is_url_safe(url):
    """
    Validate URL against allowlist and prevent SSRF attacks.
    Returns True if URL is safe, False otherwise.
    """
    if not url:
        return False
        
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False
            
        # Check domain against allowlist
        if parsed.netloc not in ALLOWED_DOMAINS:
            return False
            
        # Prevent accessing internal networks
        if not parsed.netloc or is_internal_ip(parsed.netloc):
            return False
            
        return True
    except Exception:
        return False

def is_internal_ip(host):
    """Check if hostname/IP refers to internal network."""
    if not host:
        return True
        
    # Remove port number if present
    if ":" in host:
        host = host.split(":")[0]
        
    # Check for localhost
    if host == "localhost" or host == "127.0.0.1" or host == "::1":
        return True
        
    # Check for private IPv4 ranges
    private_ip_pattern = re.compile(
        r'^(10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.|169\.254\.|127\.)'
    )
    if private_ip_pattern.match(host):
        return True
        
    return False

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

    query = (
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    cursor.execute(query)
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
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF with URL validation"""
    url = flask.request.args.get("url")
    
    if not url:
        return "Error: Missing URL parameter", 400
        
    if not is_url_safe(url):
        return "Error: URL not allowed for security reasons", 403
        
    try:
        # Disable redirects to prevent bypass techniques
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        # Check if it's a redirect
        if response.status_code >= 300 and response.status_code < 400:
            return "Error: Redirects are not allowed", 403
            
        return response.text
    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Vulnerable to RCE if connecting to an untrusted SSH server"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Automatically accepting any key
    ssh.connect("malicious-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()


if __name__ == "__main__":
    app.run(debug=True)