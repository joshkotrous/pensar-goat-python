import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse

app = flask.Flask(__name__)

# Define a whitelist of allowed domains for the fetch function
ALLOWED_DOMAINS = ["trusted-domain.com", "api.example.org", "data.gov"]

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
    """Safely fetches content from a whitelisted URL"""
    url = flask.request.args.get("url")
    
    # Input validation
    if not url:
        return "Error: No URL provided", 400
    
    # Validate URL format and extract domain
    try:
        parsed_url = urlparse(url)
        
        # Check for valid scheme
        if parsed_url.scheme not in ["http", "https"]:
            return "Error: Only HTTP and HTTPS protocols are allowed", 400
        
        domain = parsed_url.netloc
        
        # Check against whitelist
        if domain not in ALLOWED_DOMAINS:
            return f"Error: Domain '{domain}' is not in the whitelist", 403
        
        # Make the request with safety measures
        response = requests.get(
            url, 
            allow_redirects=False,  # Disable automatic redirects
            timeout=10,  # Set timeout for request
            headers={"User-Agent": "SecureApp/1.0"}  # Use a consistent user agent
        )
        
        # Handle redirects manually if needed
        if response.status_code in [301, 302, 303, 307, 308]:  # Redirect status codes
            redirect_url = response.headers.get('Location')
            # Handle relative URLs
            if redirect_url.startswith('/'):
                redirect_url = f"{parsed_url.scheme}://{parsed_url.netloc}{redirect_url}"
            
            redirect_parsed = urlparse(redirect_url)
            redirect_domain = redirect_parsed.netloc
            
            # Only follow redirects to allowed domains
            if redirect_domain in ALLOWED_DOMAINS:
                response = requests.get(
                    redirect_url,
                    allow_redirects=False,
                    timeout=10,
                    headers={"User-Agent": "SecureApp/1.0"}
                )
            else:
                return f"Error: Redirect to non-whitelisted domain '{redirect_domain}' blocked", 403
        
        return response.text
    
    except requests.exceptions.RequestException as e:
        return f"Error making request: {str(e)}", 500
    except Exception as e:
        return f"Error processing URL: {str(e)}", 400


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