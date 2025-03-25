import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse

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
# Allowlist of permitted schemes and domains
ALLOWED_SCHEMES = {'http', 'https'}
ALLOWED_DOMAINS = {'example.com', 'trusted-domain.com', 'api.public-service.org'}

def is_valid_url(url):
    """Validate if a URL is allowed based on scheme and domain allowlists"""
    try:
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Check scheme
        if parsed_url.scheme.lower() not in ALLOWED_SCHEMES:
            return False
            
        # Extract domain
        domain = parsed_url.netloc.lower()
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
            
        # Check if domain is in allowlist
        if domain not in ALLOWED_DOMAINS:
            return False
            
        # URL is valid
        return True
    except Exception:
        return False

@app.route("/fetch")
def fetch():
    """Fixed to prevent SSRF attacks"""
    url = flask.request.args.get("url")
    
    # Validate URL against allowlist
    if not is_valid_url(url):
        return "Invalid or unauthorized URL", 403
    
    # Make request with security measures
    response = requests.get(
        url, 
        allow_redirects=False,  # Prevent redirect-based attacks
        timeout=10  # Set timeout to prevent denial-of-service
    )
    
    return response.text


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