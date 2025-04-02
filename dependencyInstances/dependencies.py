import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from markupsafe import escape  # Added for XSS protection
import urllib.parse
import socket
import ipaddress
import os  # Added for environment variable support

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
    """Protected against XSS"""
    user_input = flask.request.args.get("name", "")
    return f"<h1>Welcome, {escape(user_input)}!</h1>"  # Sanitized with escape()


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Fixed XXE vulnerability"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
def is_safe_url(url):
    """
    Validate if a URL is safe to request.
    
    Returns:
        bool: True if the URL is safe, False otherwise
    """
    try:
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Check scheme
        if parsed_url.scheme not in ['http', 'https']:
            return False
        
        # Get the hostname
        hostname = parsed_url.netloc
        
        # Disallow requests to private IP ranges and localhost
        if not hostname:
            return False
            
        # Resolve the hostname to an IP address
        try:
            ip = socket.gethostbyname(hostname)
            
            # Check if it's a private/internal IP
            ip_obj = ipaddress.ip_address(ip)
            if (
                ip_obj.is_private or
                ip_obj.is_loopback or
                ip_obj.is_reserved or
                ip_obj.is_multicast
            ):
                return False
        except socket.gaierror:
            # If hostname can't be resolved, it might be safer to block it
            return False
            
        return True
    except Exception:
        # Any parsing error should be treated as unsafe
        return False


@app.route("/fetch")
def fetch():
    """Safely fetch content from an external URL"""
    url = flask.request.args.get("url")
    
    if not url or not is_safe_url(url):
        return "Invalid or disallowed URL", 400
        
    response = requests.get(url, allow_redirects=True)
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command(server="malicious-server.com", username="user", password="pass", command="ls"):
    """Securely connect to an SSH server and run a command"""
    ssh = paramiko.SSHClient()
    
    # Load system host keys from the default location
    ssh.load_system_host_keys()
    
    # Use RejectPolicy instead of AutoAddPolicy to prevent automatic acceptance of unknown host keys
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect to the server with provided credentials
        ssh.connect(server, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read()
        ssh.close()
        return result
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)