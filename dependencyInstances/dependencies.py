import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse
import ipaddress
import re
import os  # Added for environment variable access

app = flask.Flask(__name__)

# SSRF Protection Configuration
ALLOWED_SCHEMES = ['http', 'https']
REQUEST_TIMEOUT = 10  # seconds

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
    """Protected from SQL Injection"""
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
    """Protected from XSS"""
    user_input = flask.request.args.get("name", "")
    return f"<h1>Welcome, {flask.escape(user_input)}!</h1>"  # Sanitized to prevent script injection


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Loads configuration from YAML file"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.SafeLoader)  # Using safe loader to prevent code execution
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected from XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against credential leakage in redirects"""
    url = flask.request.args.get("url")
    
    if not url:
        return "Error: Missing URL parameter", 400
    
    # Validate URL before making request
    if not is_safe_url(url):
        return "Invalid or potentially unsafe URL", 400
    
    try:
        # Set a timeout to prevent hanging requests
        response = requests.get(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500

def is_safe_url(url):
    """Check if a URL is safe to make requests to."""
    try:
        # Normalize the URL to prevent bypasses through encoding
        url = urllib.parse.unquote(url)
        
        parsed = urllib.parse.urlparse(url)
        
        # Validate scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False
        
        # Validate hostname
        hostname = parsed.netloc.lower()
        if ':' in hostname:  # Remove port if present
            hostname = hostname.split(':')[0]
        
        # Reject if hostname is empty
        if not hostname:
            return False
        
        # Check for localhost/internal references in various formats
        localhost_patterns = [
            r'^localhost',
            r'^127\.',
            r'^::1',
            r'^0\.0\.0\.0',
            r'\.localhost',
            r'^0'  # Short for 0.0.0.0
        ]
        
        for pattern in localhost_patterns:
            if re.match(pattern, hostname, re.IGNORECASE):
                return False
            
        # Check if it's an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private/internal IP ranges
            if (ip.is_private or ip.is_loopback or ip.is_link_local or 
                ip.is_multicast or ip.is_reserved or ip.is_unspecified):
                return False
        except ValueError:
            # Not an IP address, it's a hostname
            # Check for common internal domain patterns
            internal_patterns = [
                r'\.local',
                r'\.internal',
                r'\.intranet',
                r'\.lan',
                r'\.corp',
                r'\.private'
            ]
            
            for pattern in internal_patterns:
                if re.search(pattern, hostname, re.IGNORECASE):
                    return False
                
        return True
    except Exception:
        # Any parsing error means the URL is invalid
        return False


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to an SSH server with proper host key verification"""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load keys from system's known_hosts file
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())  # Reject unknown host keys
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH connection error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)