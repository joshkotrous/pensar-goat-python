import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
from flask import escape  # Import for HTML escaping
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse  # Added for URL validation
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
    """Protected against SQL Injection"""
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
    """Fixed XSS vulnerability with proper escaping"""
    user_input = flask.request.args.get("name", "")
    # Sanitize user input using Flask's escape function
    safe_input = escape(user_input)
    return f"<h1>Welcome, {safe_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Fixed: Safe YAML loading"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load to prevent code execution
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
    """Fixed to prevent open redirects and SSRF"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent open redirects and SSRF
    allowed_domains = ["example.com", "api.example.com"]  # Define your trusted domains
    
    # Basic validation - check if URL is properly formed
    if not url or not url.startswith(('http://', 'https://')):
        return "Invalid URL format", 400
    
    # Parse URL to extract domain
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check if domain is in allowed list
        if domain not in allowed_domains:
            return f"Access to domain '{domain}' is not allowed", 403
            
        # Make request without following redirects
        response = requests.get(url, allow_redirects=False)
        
        # Check if the response is a redirect
        if response.is_redirect:
            return "Request resulted in a redirect, which is not allowed", 403
            
        return response.text
        
    except Exception as e:
        return f"Error processing URL: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to SSH server with proper host key validation"""
    ssh = paramiko.SSHClient()
    
    # Load known hosts from the default location (~/.ssh/known_hosts)
    ssh.load_system_host_keys()
    
    # Use RejectPolicy to reject connections to unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.ssh_exception.SSHException as e:
        # Handle host key verification failures and other SSH exceptions
        return f"SSH connection failed: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)