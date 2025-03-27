import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import re
from urllib.parse import urlparse

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


# Helper function to validate URLs
def is_safe_url(url):
    """
    Validate if a URL is safe to request.
    
    Checks:
    1. URL format is valid
    2. URL doesn't point to internal network resources
    3. URL uses an allowed scheme (http, https)
    
    Returns:
        bool: True if the URL is safe, False otherwise
    """
    if not url:
        return False
    
    # Check URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
    except:
        return False
    
    # Check URL scheme
    if parsed.scheme not in ['http', 'https']:
        return False
    
    # Check for internal network resources
    hostname = parsed.netloc.split(':')[0]  # Remove port if present
    
    # Check for localhost variations
    if hostname == 'localhost' or hostname == '127.0.0.1' or hostname.startswith('::1'):
        return False
    
    # Check for private IP ranges
    private_ip_patterns = [
        r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$',  # 10.0.0.0/8
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$',  # 172.16.0.0/12
        r'^192\.168\.\d{1,3}\.\d{1,3}$',  # 192.168.0.0/16
        r'^169\.254\.\d{1,3}\.\d{1,3}$',  # 169.254.0.0/16 (link-local)
    ]
    
    for pattern in private_ip_patterns:
        if re.match(pattern, hostname):
            return False
    
    return True


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Previously vulnerable to credential leakage in redirects"""
    url = flask.request.args.get("url")
    
    # Validate the URL before making the request
    if not url or not is_safe_url(url):
        return "Error: Invalid or unsafe URL provided", 400
    
    response = requests.get(url, allow_redirects=True)
    return response.text


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