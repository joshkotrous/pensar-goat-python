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
    """Protected from SSRF by URL validation"""
    url = flask.request.args.get("url")
    
    # Validate URL before making request
    if not url:
        return "Error: No URL provided", 400
    
    try:
        # Parse the URL to validate components
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        
        # Ensure the URL has a scheme and netloc
        if not parsed_url.scheme or not parsed_url.netloc:
            return "Error: Invalid URL format", 400
        
        # Block requests to private IP ranges, localhost, etc.
        hostname = parsed_url.netloc.split(':')[0].lower()
        
        # Check for obvious localhost/internal requests
        if hostname in ["localhost", "127.0.0.1", "0.0.0.0", "::1"] or \
           hostname.startswith("192.168.") or hostname.startswith("10.") or \
           (hostname.startswith("172.") and 
            len(hostname.split('.')) > 1 and 
            hostname.split('.')[1].isdigit() and 
            16 <= int(hostname.split('.')[1]) <= 31) or \
           hostname.startswith("169.254."):
            return "Error: Access to internal resources is prohibited", 403
        
        # Proceed with the request only if validation passes
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}", 500


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