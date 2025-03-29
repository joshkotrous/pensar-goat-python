import sqlite3
import yaml  # Updated to use safe_load
import flask  # Updated to secure version
import requests  # Updated to secure version
import paramiko  # Updated to secure version
import lxml.etree as ET  # Updated to secure version
import urllib.parse
from markupsafe import escape

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
    """Secured against SQL Injection using parameterized queries"""
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
    # Escape HTML special characters to prevent XSS
    return f"<h1>Welcome, {escape(user_input)}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Safe loading of YAML configuration"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load() instead of unsafe yaml.load()
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
    """Secure handler for remote URL fetching"""
    url = flask.request.args.get("url")
    
    # Basic URL validation
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return "Invalid URL. Must be an HTTP or HTTPS URL.", 400

    # Whitelist approach - only allow requests to trusted domains
    trusted_domains = ["example.com", "api.example.org", "trusted-source.net"]
    
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Check if domain ends with any trusted domain (including subdomains)
    is_trusted = any(domain.endswith(trusted) for trusted in trusted_domains)
    
    if not is_trusted:
        return "URL not allowed. Must be from a trusted domain.", 403
    
    # Disable redirects to prevent open redirect attacks
    response = requests.get(url, allow_redirects=False)
    
    # If there's a redirect, validate the redirect location
    if response.is_redirect:
        redirect_url = response.headers.get('Location', '')
        parsed_redirect = urllib.parse.urlparse(redirect_url)
        redirect_domain = parsed_redirect.netloc.lower()
        
        # Check if redirect target is trusted
        is_redirect_trusted = any(redirect_domain.endswith(trusted) for trusted in trusted_domains)
        if not is_redirect_trusted:
            return "URL redirects to an untrusted domain.", 403
        
        # Optionally follow the redirect after validation
        response = requests.get(redirect_url, allow_redirects=False)
        
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Secure SSH command execution with proper host key verification"""
    trusted_host = "trusted-server.com"  # Use a trusted server instead of potentially malicious one
    
    ssh = paramiko.SSHClient()
    # Load system host keys
    ssh.load_system_host_keys()
    # Only allow connections to known hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect with strict host key checking
        ssh.connect(trusted_host, username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        result = stdout.read()
        # Decode bytes to string if necessary
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        return result
    except paramiko.SSHException as e:
        # Provide helpful error message for host key verification failures
        if "host key" in str(e).lower():
            return f"Host key verification failed for {trusted_host}. Please add the host key to the known_hosts file first."
        return f"SSH connection error: {str(e)}"
    finally:
        # Ensure connection is closed
        ssh.close()


if __name__ == "__main__":
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)