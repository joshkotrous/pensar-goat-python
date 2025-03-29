import os  # Import os to access environment variables
import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse  # Added for URL parsing
from markupsafe import escape  # Import for XSS protection

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
    """Fixed SQL Injection Vulnerability"""
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
    return f"<h1>Welcome, {escape(user_input)}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.SafeLoader)  # Using safer yaml.SafeLoader
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
    """Secure handling of external requests"""
    url = flask.request.args.get("url")
    
    if not url:
        return "No URL provided", 400
    
    try:
        parsed_url = urlparse(url)
        
        # Validate protocol
        if parsed_url.scheme not in ['http', 'https']:
            return "Only HTTP and HTTPS protocols are allowed", 403
        
        # Validate domain against whitelist
        allowed_domains = ['example.com', 'api.example.org', 'trusted-source.net']
        domain = parsed_url.netloc.lower()
        
        if not any(domain == d or domain.endswith('.' + d) for d in allowed_domains):
            return f"Access to domain '{domain}' is not allowed", 403
        
        # Proceed with the request
        response = requests.get(url, allow_redirects=True)
        return response.text
        
    except Exception as e:
        return f"Error processing URL: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command(server, username, password, command, known_hosts_file=None):
    """Securely execute SSH command with proper host key verification"""
    # Input validation
    if not server or not username or not password or not command:
        raise ValueError("Missing required SSH connection parameters")
        
    # Create SSH client
    ssh = paramiko.SSHClient()
    
    # Use system's known_hosts file or a provided one
    if known_hosts_file:
        ssh.load_host_keys(known_hosts_file)
    else:
        ssh.load_system_host_keys()
    
    # Use RejectPolicy to ensure we only connect to known hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect to the server using provided credentials
        ssh.connect(server, username=username, password=password)
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    finally:
        # Ensure the connection is closed
        ssh.close()


if __name__ == "__main__":
    # Get debug mode from environment variable, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)