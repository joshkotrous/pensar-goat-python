import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import ipaddress
import socket
from urllib.parse import urlparse
from markupsafe import escape
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
    """Fixed SQL Injection vulnerability"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    # Use parameterized query instead of string concatenation
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
    # Sanitize user input to prevent XSS
    sanitized_input = escape(user_input)
    return f"<h1>Welcome, {sanitized_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Previously vulnerable to Arbitrary Code Execution - now fixed"""
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
@app.route("/fetch")
def fetch():
    """Protected against SSRF with URL validation"""
    url = flask.request.args.get("url")
    
    # Ensure URL is provided
    if not url:
        return "Error: No URL provided", 400
    
    try:
        parsed_url = urlparse(url)
        
        # Check protocol
        if parsed_url.scheme not in ["http", "https"]:
            return "Error: Only HTTP and HTTPS protocols are allowed", 403
        
        # Ensure hostname is present
        if not parsed_url.netloc:
            return "Error: Invalid URL format", 400
        
        # Resolve hostname to check if it's internal
        hostname = parsed_url.netloc
        if ":" in hostname:
            hostname = hostname.split(":")[0]  # Remove port if present
        
        try:
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            
            # Check for private IP addresses
            if (ip_obj.is_private or ip_obj.is_loopback or 
                ip_obj.is_unspecified or ip_obj.is_reserved or 
                ip_obj.is_multicast):
                return "Error: Access to internal resources is forbidden", 403
            
        except socket.gaierror:
            return "Error: Cannot resolve hostname", 400
        
        # Proceed with the request
        response = requests.get(url, allow_redirects=True)
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Vulnerable to RCE if connecting to an untrusted SSH server"""
    ssh = paramiko.SSHClient()
    # SECURITY FIX: Use RejectPolicy instead of AutoAddPolicy to ensure
    # host keys are verified before establishing connections
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    ssh.connect("malicious-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)