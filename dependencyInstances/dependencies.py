import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse  # For URL parsing and validation

app = flask.Flask(__name__)

# Define allowed schemes and hosts for URL validation
ALLOWED_SCHEMES = {'http', 'https'}
ALLOWED_HOSTS = {'api.example.com', 'data.example.org'}  # Replace with actual allowed hosts

def is_url_allowed(url):
    """Validate URL against allowlist of schemes and hosts"""
    try:
        parsed_url = urllib.parse.urlparse(url)
        return (parsed_url.scheme in ALLOWED_SCHEMES and 
                parsed_url.netloc in ALLOWED_HOSTS)
    except Exception:
        return False

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
    """Protected against SSRF"""
    url = flask.request.args.get("url")
    
    # Validate URL against allowlist
    if not url or not is_url_allowed(url):
        return "Invalid or disallowed URL", 400
    
    try:
        # Add timeout to prevent hanging
        response = requests.get(
            url,
            allow_redirects=False,  # Prevent redirects to malicious URLs
            timeout=10,
            headers={'User-Agent': 'SecureApp/1.0'}  # Don't leak default user agent
        )
        
        # Return a limited subset of the response data
        return f"Request completed with status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500


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