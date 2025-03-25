import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from markupsafe import escape  # Import for XSS prevention

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
    """Fixed SQL Injection vulnerability with parameterized queries"""
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
    """Previously vulnerable to XSS, now fixed with escaping"""
    user_input = flask.request.args.get("name", "")
    # Escape user input to prevent XSS
    safe_input = escape(user_input)
    return f"<h1>Welcome, {safe_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Previously vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe yaml.safe_load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected from XXE"""
    xml_data = flask.request.data
    # Disable external entity resolution to prevent XXE attacks
    parser = ET.XMLParser(resolve_entities=False)
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Secured against credential leakage in redirects"""
    from urllib.parse import urlparse, urljoin
    
    url = flask.request.args.get("url")
    
    # Check if URL is provided
    if not url:
        return "Error: No URL provided", 400
    
    # Validate URL format and domain
    try:
        # Whitelist of allowed domains
        allowed_domains = ["example.com", "api.example.org", "data.example.net"]
        
        # Parse and validate URL
        parsed_url = urlparse(url)
        
        # Ensure URL has scheme and netloc
        if not parsed_url.scheme or not parsed_url.netloc:
            return "Error: Invalid URL format", 400
            
        # Check against whitelist
        if not any(parsed_url.netloc.endswith(domain) for domain in allowed_domains):
            return f"Error: Domain not allowed. Allowed domains: {', '.join(allowed_domains)}", 403
        
        # Make the request with redirects disabled to prevent leaking to untrusted domains
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        # Check if redirect occurred and notify user instead of following automatically
        if 300 <= response.status_code < 400 and 'Location' in response.headers:
            return f"Redirect detected to: {response.headers['Location']}. Redirects are disabled for security.", 200
            
        return response.text
        
    except requests.RequestException as e:
        return f"Error making request: {str(e)}", 500
    except Exception as e:
        return f"Error processing request: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to SSH server with host key verification"""
    ssh = paramiko.SSHClient()
    # Load system host keys
    ssh.load_system_host_keys()
    # Use RejectPolicy to reject unknown hosts by default
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.ssh_exception.SSHException as e:
        return f"SSH connection error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)