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


# ======== Helper function for URL validation ========
def is_url_allowed(url):
    """
    Validate if a URL is allowed based on scheme and host.
    Returns True if allowed, False otherwise.
    """
    try:
        # Simple URL validation without external dependencies
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Extract the host part (simplified parsing)
        if url.startswith('http://'):
            host_part = url[7:]
        else:  # https://
            host_part = url[8:]
            
        # Find the end of the host part
        path_start = host_part.find('/')
        if path_start != -1:
            host_part = host_part[:path_start]
            
        # Remove port if present
        port_start = host_part.find(':')
        if port_start != -1:
            host_part = host_part[:port_start]
            
        # Convert to lowercase for comparison
        host_part = host_part.lower()
        
        # Block localhost and common private IP patterns
        forbidden_patterns = [
            'localhost',
            '127.0.0.1',
            '169.254.169.254',  # AWS metadata
            '.internal',
            '.local',
            'intranet'
        ]
        
        for pattern in forbidden_patterns:
            if pattern in host_part:
                return False
                
        # Check for private IP ranges
        ip_parts = host_part.split('.')
        if len(ip_parts) == 4:
            try:
                # Convert all parts to integers
                ip_nums = [int(part) for part in ip_parts]
                
                # Check for private IP ranges
                if ip_nums[0] == 10:  # 10.0.0.0/8
                    return False
                if ip_nums[0] == 192 and ip_nums[1] == 168:  # 192.168.0.0/16
                    return False
                if ip_nums[0] == 172 and (16 <= ip_nums[1] <= 31):  # 172.16.0.0/12
                    return False
                    
            except ValueError:
                # Not an IP address format, continue
                pass
                
        # Allow all other URLs - uncomment for stricter validation if needed
        # allowed_hosts = ['api.example.com', 'public-service.org']
        # if host_part not in allowed_hosts:
        #     return False
            
        return True
    except Exception:
        # If any parsing error occurs, reject the URL
        return False


# ======== 5. Fixed SSRF Vulnerability ========
@app.route("/fetch")
def fetch():
    """Fetches content from validated URLs with SSRF protections"""
    url = flask.request.args.get("url")
    
    # Validate URL against allowlist
    if not url or not is_url_allowed(url):
        return "Invalid or disallowed URL", 400
    
    try:
        # Set reasonable timeouts and limit redirects
        response = requests.get(
            url, 
            allow_redirects=True,
            timeout=5,  # Timeout after 5 seconds
        )
        
        # Check if the final URL after redirects is still allowed
        if not is_url_allowed(response.url):
            return "Redirected to disallowed URL", 400
            
        # Only return successful responses
        if response.status_code != 200:
            return f"Request failed with status code: {response.status_code}", 400
            
        return response.text
    except requests.exceptions.RequestException as e:
        # Handle request exceptions safely
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