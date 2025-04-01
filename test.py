import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse  # Added for URL parsing in SSRF protection

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
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {flask.escape(user_input)}!</h1>"  # Sanitized using flask.escape()
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Fixed Arbitrary Code Execution vulnerability"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load() instead of load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Secure against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Secure handling of URL redirects"""
    url = flask.request.args.get("url")
    
    # Validate the URL before making the request
    if not url or not is_safe_url(url):
        return "Invalid or untrusted URL", 400
    
    # Make the request with redirects allowed, but only to trusted domains
    response = requests.get(url, allow_redirects=True)
    return response.text


def is_safe_url(url):
    """Validate that a URL is safe and from a trusted domain."""
    try:
        parsed_url = urllib.parse.urlparse(url)
        
        # Define trusted domains/schemes
        trusted_domains = {'example.com', 'api.yourdomain.com', 'data.yourdomain.com'}
        allowed_schemes = {'http', 'https'}
        
        return (
            parsed_url.scheme in allowed_schemes and
            (parsed_url.netloc in trusted_domains or
             parsed_url.netloc.endswith('.yourdomain.com'))
        )
    except Exception:
        return False


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """SSH command execution with proper host key verification"""
    ssh = paramiko.SSHClient()
    
    # Load known hosts if the file exists
    ssh.load_system_host_keys()
    
    # Instead of auto-adding, use RejectPolicy to require key verification
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect to the server - will fail if key is unknown
        ssh.connect("trusted-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        # Handle SSH exceptions appropriately
        return f"SSH connection error: {str(e)}"


if __name__ == "__main__":
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)