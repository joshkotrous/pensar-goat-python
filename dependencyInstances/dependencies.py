import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse  # For URL validation

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
    """Protected against Open Redirect vulnerabilities"""
    url = flask.request.args.get("url")
    
    # Basic URL validation
    if not url:
        return "Error: No URL provided", 400
    
    try:
        parsed_url = urlparse(url)
        
        # Ensure scheme is http or https
        if parsed_url.scheme not in ('http', 'https'):
            return "Error: URL must use http or https scheme", 400
            
        # Ensure hostname is not empty
        if not parsed_url.netloc:
            return "Error: Invalid URL format", 400
            
        # Block localhost and internal hostnames
        hostname = parsed_url.netloc.split(':')[0].lower()  # Extract hostname without port
        
        # Check for localhost and loopback addresses
        if (hostname == 'localhost' or hostname.startswith('127.') or 
            hostname == '::1' or hostname == '[::1]'):
            return "Error: Access to localhost is not allowed", 403
            
        # Block common private network IP ranges
        private_patterns = [
            '10.', '192.168.', 
            # 172.16.0.0 to 172.31.255.255
            '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.'
        ]
        
        if any(hostname.startswith(pattern) for pattern in private_patterns):
            return "Error: Access to internal networks is not allowed", 403
            
        # Now it's safe to make the request
        response = requests.get(url, allow_redirects=True)
        return response.text
        
    except Exception as e:
        return f"Error: Invalid URL - {str(e)}", 400


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