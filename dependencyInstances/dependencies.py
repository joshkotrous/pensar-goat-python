import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import os  # Added for environment variable access
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

    # Using parameterized queries instead of string formatting
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
    # Escape user input to prevent XSS
    escaped_input = flask.escape(user_input)
    return f"<h1>Welcome, {escaped_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load for security
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
    """URL fetching with proper validation to prevent SSRF"""
    url = flask.request.args.get("url")
    
    # Ensure URL is provided
    if not url:
        return "Error: URL parameter is required", 400
    
    # Validate the URL
    try:
        parsed_url = urlparse(url)
        
        # Check scheme
        if parsed_url.scheme not in ['http', 'https']:
            return "Error: Only HTTP/HTTPS URLs are allowed", 403
        
        # Extract hostname
        hostname = parsed_url.netloc.lower()
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        
        # Block access to localhost and common private domains
        if hostname == 'localhost' or hostname == '127.0.0.1' or hostname == '::1' or \
           hostname.endswith('.local') or hostname.endswith('.internal') or \
           hostname.endswith('.intranet'):
            return "Error: Access to internal resources is restricted", 403
        
        # Simple check for private IP ranges
        ip_parts = hostname.split('.')
        if len(ip_parts) == 4 and all(part.isdigit() for part in ip_parts):
            # Check for private IP ranges
            if ip_parts[0] == '10' or \
               (ip_parts[0] == '192' and ip_parts[1] == '168') or \
               (ip_parts[0] == '172' and 16 <= int(ip_parts[1]) <= 31):
                return "Error: Access to private IP ranges is restricted", 403
        
        # Proceed with the request
        response = requests.get(url, allow_redirects=True)
        return response.text
    except Exception as e:
        return f"Error: Invalid URL - {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to SSH server with proper host key verification"""
    ssh = paramiko.SSHClient()
    
    # Load system host keys
    ssh.load_system_host_keys()
    
    # Use RejectPolicy instead of AutoAddPolicy
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("server.example.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH Error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    # Get debug mode from environment variable, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)