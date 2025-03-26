import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import ipaddress
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

    query = (
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    cursor.execute(query)
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
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


def is_url_safe(url):
    """
    Check if a URL is safe to request by verifying it doesn't point to internal networks.
    Returns True if safe, False otherwise.
    """
    if not url:
        return False
    
    parsed_url = urlparse(url)
    
    # Ensure the scheme is http or https
    if parsed_url.scheme not in ('http', 'https'):
        return False
    
    # Check if the URL points to a private IP
    try:
        hostname = parsed_url.hostname
        if hostname:
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                    return False
            except ValueError:
                # Hostname is not an IP address, proceed with other checks
                pass
            
            # Prevent localhost access via hostname
            if hostname == 'localhost' or hostname.startswith('127.') or hostname.endswith('.local'):
                return False
    except Exception:
        # If any error occurs during validation, consider it unsafe
        return False
    
    return True


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Secured against SSRF by validating URLs and disabling redirects"""
    url = flask.request.args.get("url")
    
    if not is_url_safe(url):
        return "Invalid or unsafe URL", 400
    
    try:
        # Disable redirects for security, set a short timeout
        response = requests.get(url, allow_redirects=False, timeout=10)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error processing request: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Vulnerable to RCE if connecting to an untrusted SSH server"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Automatically accepting any key
    ssh.connect("malicious-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()


if __name__ == "__main__":
    app.run(debug=True)