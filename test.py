import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse  # Added for URL parsing

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
    """Fixed SQL Injection vulnerability using parameterized queries"""
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
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerability fixed by using safe_load"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe yaml.safe_load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Secured against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========

# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fetches content from whitelisted URLs"""
    url = flask.request.args.get("url")
    
    # Whitelist of allowed domains and schemes
    allowed_domains = ['api.example.com', 'public-api.org', 'data.gov']
    allowed_schemes = ['https']
    
    try:
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Check if scheme and domain are in the whitelist
        if parsed_url.scheme not in allowed_schemes:
            return "Only HTTPS URLs are allowed", 403
            
        if parsed_url.netloc not in allowed_domains:
            return "This domain is not in the allowed list", 403
            
        # Make the request with a reasonable timeout
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except Exception as e:
        return f"Error processing URL: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Automatically accepting any key
    ssh.connect("malicious-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()

    return stdout.read()


if __name__ == "__main__":
    app.run(debug=True)