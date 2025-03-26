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
    """Fetches content from a URL with validation to prevent security issues"""
    url = flask.request.args.get("url")
    
    # Validate URL is provided
    if not url:
        return "No URL provided", 400
    
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        
        # Validate URL has proper structure
        if not parsed_url.scheme or not parsed_url.netloc:
            return "Invalid URL format", 400
        
        # Validate protocol (only allow http/https)
        if parsed_url.scheme not in ['http', 'https']:
            return "Only HTTP and HTTPS URLs are allowed", 403
        
        # Prevent access to internal networks/localhost
        hostname = parsed_url.netloc.split(':')[0].lower()
        if hostname == 'localhost' or hostname.startswith('127.'):
            return "Access to internal networks is not allowed", 403
            
        # Check for other private IP ranges
        if hostname.startswith('10.') or hostname.startswith('192.168.'):
            return "Access to internal networks is not allowed", 403
            
        # Check for 172.16.0.0 to 172.31.255.255 range
        if hostname.startswith('172.'):
            try:
                parts = hostname.split('.')
                if len(parts) > 1 and 16 <= int(parts[1]) <= 31:
                    return "Access to internal networks is not allowed", 403
            except (ValueError, IndexError):
                # Not a valid IP in this format, continue
                pass
        
        # Make the request with safety measures
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    
    except Exception as e:
        return f"Error processing URL: {str(e)}", 500


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