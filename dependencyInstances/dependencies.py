import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse  # For URL validation
import os  # Added for environment variable access
from markupsafe import escape  # Added for XSS protection

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
    """Fixed SQL Injection vulnerability using parameterized query"""
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
        f"<h1>Welcome, {escape(user_input)}!</h1>"  # Sanitized input to prevent XSS
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Loads configuration safely"""
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


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fetches content from external URLs with security measures"""
    url = flask.request.args.get("url")
    
    # Check if URL is provided
    if not url:
        return "URL parameter is required", 400
    
    # Validate URL to prevent access to internal resources or non-HTTP schemes
    try:
        parsed_url = urllib.parse.urlparse(url)
        
        # Ensure URL uses http or https scheme
        if parsed_url.scheme not in ['http', 'https']:
            return "Only HTTP and HTTPS schemes are allowed", 403
        
        # Block requests to internal/private networks
        hostname = parsed_url.netloc.split(':')[0]  # Remove port if present
        if not hostname or hostname in ['localhost'] or any([
            hostname.startswith(prefix) for prefix in ['127.', '10.', '172.16.', '192.168.']
        ]):
            return "Access to internal resources is not allowed", 403
    except Exception:
        return "Invalid URL", 400
    
    try:
        # Make the request without following redirects and with a timeout
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        # Check if the response is a redirect
        if response.is_redirect:
            return "Redirects are not followed for security reasons", 403
        
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Connect to SSH server with proper host key validation.
    
    SECURITY NOTE: This function has been updated to use secure SSH practices:
    - Loads known hosts from system configuration
    - Rejects connections to unknown/untrusted hosts
    - Uses a neutral example hostname (replace with your actual trusted server)
    
    If you need to connect to a new server:
    1. First manually SSH to it to add its key to your known_hosts file, or
    2. If you must accept unknown hosts (not recommended), replace RejectPolicy 
       with WarningPolicy to log warnings instead of rejecting connections.
    """
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load keys from system's known_hosts
    
    # RejectPolicy will refuse connections to unknown hosts
    # This prevents man-in-the-middle attacks and connections to untrusted servers
    ssh.set_missing_host_key_policy(
        paramiko.RejectPolicy()
    )
    
    # Replace with your trusted server
    ssh.connect("example-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()


if __name__ == "__main__":
    # Use environment variable to control debug mode, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)