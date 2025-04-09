import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse  # For URL parsing
import os  # Added for environment variable access

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

    # Using parameterized query instead of string interpolation
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Previously vulnerable to XSS, now fixed"""
    user_input = flask.request.args.get("name", "")
    return f"<h1>Welcome, {flask.escape(user_input)}!</h1>"  # Sanitized user input


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
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
    """Safe handling of URL fetching with domain validation"""
    url = flask.request.args.get("url")
    
    # Check if URL is provided
    if not url:
        return "Error: URL parameter is required", 400
    
    # Validate URL against a whitelist of trusted domains
    try:
        parsed_url = urllib.parse.urlparse(url)
        
        # Check scheme is http or https
        if parsed_url.scheme not in ["http", "https"]:
            return "Error: Only HTTP and HTTPS protocols are allowed", 403
        
        # Check domain against whitelist
        allowed_domains = ["trusted-domain.com", "api.example.org"]
        if not parsed_url.netloc or parsed_url.netloc not in allowed_domains:
            return "Error: Only requests to trusted domains are allowed", 403
    except Exception:
        return "Error: Invalid URL", 400
    
    # Disable redirects for security
    response = requests.get(url, allow_redirects=False)
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connects to an SSH server and runs a command"""
    ssh = paramiko.SSHClient()
    
    # Load known host keys from file (default location: ~/.ssh/known_hosts)
    ssh.load_system_host_keys()
    
    # Set policy to reject unknown host keys by default
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect to the server
        ssh.connect("malicious-server.com", username="user", password="pass")
        
        # Execute command and get output
        stdin, stdout, stderr = ssh.exec_command("ls")
        result = stdout.read()
        return result
    except paramiko.ssh_exception.SSHException as e:
        # Handle SSH exceptions, like unknown host keys
        print(f"SSH Error: {e}")
        return None
    finally:
        # Always close the connection
        ssh.close()


if __name__ == "__main__":
    # Get debug mode from environment variable, default to False
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)