import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks

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
    """Protected against SQL Injection using parameterized queries"""
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
    """Previously vulnerable to XSS, now fixed"""
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    return flask.render_template_string("<h1>Welcome, {{ user_input }}!</h1>", user_input=user_input)


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data
        data = yaml.safe_load(file)  # Using yaml.safe_load() to prevent code execution

# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    """Protected against XXE"""
    tree = ET.fromstring(xml_data, parser)
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
def is_safe_url(url):
    """Checks if a URL is safe to request."""
    try:
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        # Only allow http and https URLs
        if parsed.scheme not in ['http', 'https']:
            return False
    """Connects to an SSH server with proper host key verification"""
        # Extract hostname
    
    # Load system host keys for verification
    ssh.load_system_host_keys()
    
    # Secure option: Use RejectPolicy to enforce host key verification
    # This will reject connections to servers with unknown host keys
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    # Alternative option (less secure): Use WarningPolicy if you need more flexibility
    # This will log a warning but still allow connections to servers with unknown host keys
    # ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
    
    try:
        # Connect to the server
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        # Handle SSH exceptions (e.g., unknown host key)
        return f"SSH Error: {str(e)}"
    finally:
        ssh.close()  # Ensure the connection is closed


if __name__ == "__main__":
    app.run(debug=True)
    url = flask.request.args.get("url")
    
    if not url:
        return "No URL provided", 400
    
    if not is_safe_url(url):
        return "Invalid or unsafe URL", 403
    
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except requests.exceptions.RequestException:
        return "Error fetching URL", 500


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