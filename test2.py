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
    """Protected against XSS"""
    user_input = flask.request.args.get("name", "")
    escaped_input = flask.escape(user_input)  # Escape HTML special characters
    return f"<h1>Welcome, {escaped_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load to prevent arbitrary code execution
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# Function to validate URLs to prevent SSRF
def is_safe_url(url):
    """
    Validate a URL to prevent SSRF attacks by checking:
    1. URL has a valid format with http/https scheme
    2. URL doesn't point to localhost or internal networks
    3. URL doesn't use tricks to bypass validation
    """
    if not url or not isinstance(url, str):
        return False
        
    # Check URL format
    try:
        parsed = urlparse(url)
        
        # Only allow http and https schemes
        if parsed.scheme not in ('http', 'https'):
            return False
            
        # Extract hostname
        hostname = parsed.netloc.split(':')[0].lower()
        if not hostname:
            return False
            
        # Block localhost variations
        if hostname in ('localhost', '127.0.0.1', '::1', '[::1]'):
            return False
            
        # Block URLs with @ character (potential credential embedding)
        if '@' in parsed.netloc:
            return False
            
        # Block URLs with backslashes (potential path traversal)
        if '\\' in url:
            return False
            
        # Check for IP address
        try:
            ip = ipaddress.ip_address(hostname.strip('[]'))  # Handle IPv6 addresses in brackets
            
            # Block private, loopback, multicast, link-local, and reserved IPs
            if (ip.is_private or ip.is_loopback or 
                ip.is_multicast or ip.is_reserved or 
                ip.is_link_local):
                return False
                
        except ValueError:
            # Not an IP address, continue with domain validation
            pass
            
        return True
        
    except Exception:
        # Any parsing exception means the URL is invalid
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fetch content from a URL with SSRF protection"""
    url = flask.request.args.get("url")
    
    if not is_safe_url(url):
        return "Invalid or unsafe URL", 400
    
    try:
        # Add timeout to prevent hanging
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except Exception as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Secure SSH connection with proper host key verification"""
    ssh = paramiko.SSHClient()
    
    # Load known host keys from system's known_hosts file
    ssh.load_system_host_keys()
    
    # Set RejectPolicy to reject connections to unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.ssh_exception.SSHException as e:
        # Handle the case where host key verification fails
        return f"SSH connection failed: {str(e)}"


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)