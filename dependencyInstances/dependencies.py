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
def is_url_allowed(url):
    """Validate a URL against an allowlist of allowed domains and protocols."""
    try:
        parsed_url = urllib.parse.urlparse(url)
        
        # Check for allowed schemes (protocols)
        allowed_schemes = ['http', 'https']
        if parsed_url.scheme not in allowed_schemes:
            return False
        
        # Check for allowed domains
        allowed_domains = ['example.com', 'trusted-domain.com', 'api.trusted-service.org']
        if parsed_url.netloc not in allowed_domains:
            return False
        
        return True
    except Exception:
        return False

@app.route("/fetch")
def fetch():
    """Fetch content from an allowed URL."""
    url = flask.request.args.get("url")
    
    if not url:
        return "No URL provided", 400
    
    if not is_url_allowed(url):
        return "URL not allowed for security reasons", 403
    
    try:
        # Set timeout to prevent hanging connections
        # Disable redirects to prevent redirect-based attacks
        response = requests.get(
            url, 
            allow_redirects=False, 
            timeout=10
        )
        
        # Check if the response contains sensitive information
        # This is a basic check and may need to be enhanced
        if 'password' in response.text.lower() or 'token' in response.text.lower():
            return "Response contains potentially sensitive data", 403
        
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