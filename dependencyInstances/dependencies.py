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
    """Secured against SSRF and credential leakage"""
    url = flask.request.args.get("url")
    
    # Validate URL
    if not url:
        return "Missing URL parameter", 400
    
    # Ensure URL starts with http:// or https://
    if not (url.startswith('http://') or url.startswith('https://')):
        return "Invalid URL scheme. Only HTTP and HTTPS are allowed.", 400
    
    # Extract domain for whitelist checking
    try:
        # Parse domain from URL
        if '://' in url:
            domain_part = url.split('://', 1)[1]
        else:
            domain_part = url
            
        if '/' in domain_part:
            domain_part = domain_part.split('/', 1)[0]
            
        if ':' in domain_part:
            domain_part = domain_part.split(':', 1)[0]
            
        domain = domain_part.lower()
    except Exception:
        return "Invalid URL format", 400
    
    # Whitelist allowed domains - this is an example, customize as needed
    allowed_domains = ['api.example.com', 'public-api.trusted-domain.com']
    if not any(domain == allowed or domain.endswith('.' + allowed) for allowed in allowed_domains):
        return f"Domain not in whitelist: {domain}", 403
    
    # Make the request with safe settings
    try:
        # Set allow_redirects=False to prevent redirect-based attacks
        # Set timeout to prevent hanging requests
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        # If it's a redirect, inform the user
        if 300 <= response.status_code < 400:
            return "Request resulted in a redirect which was blocked for security reasons", 403
            
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error making request: {str(e)}", 500


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