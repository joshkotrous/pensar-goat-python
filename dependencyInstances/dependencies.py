import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse
import ipaddress
import os

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
    """Protected against SQL Injection"""
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
    """Fixed XSS vulnerability"""
    user_input = flask.request.args.get("name", "")
    sanitized_input = flask.escape(user_input)  # Sanitize user input
    return f"<h1>Welcome, {sanitized_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Protected against Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load() to prevent code execution
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
    """Protected against SSRF"""
    url = flask.request.args.get("url")
    
    # Validate URL
    if not is_safe_url(url):
        return "Invalid or disallowed URL", 400
    
    try:
        # Set a timeout and disable redirects for security
        response = requests.get(url, allow_redirects=False, timeout=10)
        return response.text
    except requests.RequestException:
        return "Error fetching URL", 500

def is_safe_url(url):
    """Check if URL is safe against SSRF attacks"""
    if not url or not isinstance(url, str):
        return False
    
    # Only allow http and https URLs
    if not url.startswith(('http://', 'https://')):
        return False
    
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        # Reject if no hostname
        if not hostname:
            return False
        
        # Reject localhost
        if hostname == 'localhost' or hostname == '127.0.0.1' or hostname == '::1':
            return False
        
        # Check for private IPs
        ip_address = None
        try:
            ip_address = ipaddress.ip_address(hostname)
        except ValueError:
            # Not an IP address, continue with hostname checks
            pass
        
        # If it's an IP address, check if it's private
        if ip_address and (ip_address.is_private or ip_address.is_loopback or ip_address.is_link_local):
            return False
        
        return True
    except Exception:
        # Any parsing error means the URL is invalid
        return False


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to SSH server with proper host key validation"""
    ssh = paramiko.SSHClient()
    
    # Use RejectPolicy to reject unknown host keys
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    # Load known host keys from a specified file
    known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
    if os.path.exists(known_hosts_path):
        ssh.load_host_keys(known_hosts_path)
    
    try:
        # Connect only if the host key is verified
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        # Handle the case where host key verification fails
        return f"SSH connection error: {str(e)}"


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "").lower() == "true"
    app.run(debug=debug_mode)