import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import ipaddress
from urllib.parse import urlparse
import os  # Added for environment variable access
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
    """Protected against XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {escape(user_input)}!</h1>"
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Safe loading of YAML configuration"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected from XXE by disabling entity resolution"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# Function to validate URLs against SSRF attempts
def is_url_safe(url):
    """
    Validate a URL against SSRF attempts by checking:
    1. URL scheme (only http/https allowed)
    2. Hostname not pointing to internal/private networks
    3. Hostname matches allowed domains
    """
    if not url:
        return False

    # List of allowed schemes
    ALLOWED_SCHEMES = ['http', 'https']
    
    # List of allowed domains (add your trusted domains here)
    ALLOWED_DOMAINS = ['example.com', 'api.example.com', 'trusted-domain.com']
    
    try:
        parsed_url = urlparse(url)
        
        # Check scheme
        if parsed_url.scheme not in ALLOWED_SCHEMES:
            return False
        
        # Extract hostname
        hostname = parsed_url.netloc.split(':')[0]  # Remove port if present
        
        # Check hostname against allowed domains
        domain_allowed = False
        for domain in ALLOWED_DOMAINS:
            if hostname == domain or hostname.endswith('.' + domain):
                domain_allowed = True
                break
        
        if not domain_allowed:
            return False
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Reject if IP is private/loopback/link-local
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            # Not an IP address, continue with domain checks
            pass
        
        return True
    except:
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Secured against SSRF by validating URLs"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent SSRF
    if not url or not is_url_safe(url):
        return flask.jsonify({"error": "Invalid or disallowed URL"}), 400
    
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        
        # Return a sanitized response
        return flask.jsonify({
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type', ''),
            "content_length": len(response.content),
            "success": response.status_code == 200
        })
    except requests.RequestException as e:
        return flask.jsonify({"error": "Failed to fetch URL", "details": str(e)}), 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to an SSH server and run a command"""
    # Use environment variables for configuration, with secure defaults
    host = os.environ.get("SSH_HOST", "trusted-server.example.com")
    username = os.environ.get("SSH_USERNAME", "user")
    password = os.environ.get("SSH_PASSWORD", "pass")
    
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load system host keys
    
    # Use RejectPolicy to prevent connecting to unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect(host, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except Exception as e:
        return f"SSH connection error: {str(e)}"
    finally:
        if ssh:
            ssh.close()


if __name__ == "__main__":
    # Use environment variable with a default of False for safety
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)