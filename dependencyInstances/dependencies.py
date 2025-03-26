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


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Prevent SSRF by validating URLs and disabling redirects"""
    url = flask.request.args.get("url")
    
    # Validate URL
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        return "Invalid URL scheme. Only HTTP and HTTPS are allowed.", 400
    
    # Block requests to internal resources
    lower_url = url.lower()
    blocked_patterns = [
        'localhost', '127.', '192.168.', '10.', 
        '172.16.', '172.17.', '172.18.', '172.19.', 
        '172.20.', '172.21.', '172.22.', '172.23.',
        '172.24.', '172.25.', '172.26.', '172.27.', 
        '172.28.', '172.29.', '172.30.', '172.31.',
        '0.0.0.0', 'internal', 'local', 'intranet',
        'file://', '169.254.', '::1', '[::1]'
    ]
    
    if any(pattern in lower_url for pattern in blocked_patterns):
        return "Access to internal or local resources is forbidden.", 403
    
    # Make request with controlled parameters
    try:
        # Disable redirects to prevent SSRF through redirection
        response = requests.get(
            url,
            allow_redirects=False,
            timeout=10
        )
        
        # Check if there's a redirect and respond accordingly
        if response.status_code in (301, 302, 303, 307, 308):
            return "Resource moved, but redirects are disabled for security reasons.", 403
            
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