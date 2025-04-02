import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
from markupsafe import escape  # For HTML escaping
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse  # Added for URL parsing
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
    """Fixed SQL Injection vulnerability using parameterized queries"""
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
    """Fixed XSS vulnerability by escaping user input"""
    user_input = flask.request.args.get("name", "")
    # Escape user input to prevent XSS
    safe_input = escape(user_input)
    return f"<h1>Welcome, {safe_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Loads configuration from YAML file safely"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load to prevent code execution
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False, no_network=True)  # XXE protection enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Security-enhanced request handling"""
    url = flask.request.args.get("url")
    
    # Basic URL validation
    if not url or not url.startswith(('http://', 'https://')):
        return "Invalid URL format", 400
    
    # Whitelist of allowed domains
    allowed_domains = ['example.com', 'api.example.com', 'trusted-site.org']
    
    # Parse the domain from the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Check if domain is in the whitelist
    if domain not in allowed_domains:
        return f"Access to domain '{domain}' is not allowed", 403
    
    # Make the request with redirects disabled to prevent open redirects
    response = requests.get(url, allow_redirects=False)
    
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command(server, username, password, command="ls", known_hosts_file=None):
    """Execute a command on an SSH server with proper host key validation
    
    Args:
        server (str): The SSH server address
        username (str): SSH username
        password (str): SSH password
        command (str): Command to execute (default: "ls")
        known_hosts_file (str): Path to known hosts file (default: system default)
        
    Returns:
        The command output or error message
    """
    ssh = paramiko.SSHClient()
    
    # Load system host keys
    ssh.load_system_host_keys()
    
    # If a specific known_hosts file is provided, load it too
    if known_hosts_file:
        try:
            ssh.load_host_keys(known_hosts_file)
        except (IOError, paramiko.SSHException) as e:
            return f"Error loading known hosts file: {str(e)}"
    
    # Set the policy to reject unknown host keys by default
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect(server, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read()
        error = stderr.read()
        ssh.close()
        
        if error:
            return f"Error executing command: {error.decode('utf-8')}"
        return output
    except paramiko.SSHException as e:
        return f"SSH error: {str(e)}"
    except Exception as e:
        return f"Connection error: {str(e)}"


if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)