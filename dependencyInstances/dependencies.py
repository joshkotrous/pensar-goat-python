import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import ipaddress
from urllib.parse import urlparse
import os  # For environment variables

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
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {flask.escape(user_input)}!</h1>"  # User input now properly escaped
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load to prevent code execution
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Secure against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
def is_safe_url(url):
    """Validate URL to prevent SSRF"""
    try:
        # Check if URL is provided
        if not url:
            return False
            
        # Parse the URL
        parsed = urlparse(url)
        
        # Validate scheme - only allow http and https
        if parsed.scheme not in ['http', 'https']:
            return False
            
        # Extract hostname
        hostname = parsed.netloc.split(':')[0]
        
        # Check for IP addresses
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private, loopback, link-local networks
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                return False
        except ValueError:
            # Not an IP address, check for localhost and common internal domains
            if hostname == 'localhost' or hostname.startswith('127.') or \
               hostname.endswith('.internal') or hostname.endswith('.local'):
                return False
                
        return True
    except Exception:
        # If any error occurs during validation, reject the URL
        return False

@app.route("/fetch")
def fetch():
    """Protected against SSRF"""
    url = flask.request.args.get("url")
    
    if not is_safe_url(url):
        return "Invalid or disallowed URL", 400
    
    # Set a timeout and disable redirects for security
    response = requests.get(url, timeout=10, allow_redirects=False)
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Using secure host key verification"""
    ssh = paramiko.SSHClient()
    # Load known hosts file for host key verification
    ssh.load_system_host_keys()
    # Use RejectPolicy instead of AutoAddPolicy to reject unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    ssh.connect("trusted-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)