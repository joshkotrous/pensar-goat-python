import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse
import ipaddress
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
    """Previously vulnerable to XSS, now sanitized"""
    user_input = flask.request.args.get("name", "")
    return flask.render_template_string("<h1>Welcome, {{ user_input }}!</h1>", user_input=user_input)


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


def is_safe_url(url):
    """
    Check if a URL is safe to make requests to.
    Prevents access to private networks, localhost, etc.
    """
    if not url:
        return False

    try:
        parsed_url = urlparse(url)
        
        # Validate scheme
        if parsed_url.scheme not in ('http', 'https'):
            return False
        
        # Validate the URL has a hostname
        hostname = parsed_url.netloc.split(':')[0]  # Remove port if present
        if not hostname:
            return False
        
        # Check for localhost or similar
        hostname_lower = hostname.lower()
        if (hostname_lower == 'localhost' or 
            hostname_lower.startswith('127.') or 
            hostname_lower == '::1' or
            hostname_lower.endswith('.local')):
            return False
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block requests to private IPs
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast:
                return False
        except ValueError:
            # Not an IP address, hostname will be resolved by requests
            pass
            
        return True
    except Exception:
        # If any error occurs during validation, consider it unsafe
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fetch content from a URL after validating it's safe"""
    url = flask.request.args.get("url")
    if not url:
        return "No URL provided", 400

    if not is_safe_url(url):
        return "Invalid or unsafe URL", 403

    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except Exception as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command(hostname="example.com", username="user", password="pass", command="ls"):
    """Securely connect to an SSH server and run a command"""
    ssh = paramiko.SSHClient()
    
    # Load system host keys
    ssh.load_system_host_keys()
    
    # Use RejectPolicy to reject unknown hosts (most secure)
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    finally:
        ssh.close()


if __name__ == "__main__":
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't'])