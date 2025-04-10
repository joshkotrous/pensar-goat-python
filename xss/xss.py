from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    safe_input = escape(user_input)  # Sanitize user input
    response = f"<h1>Welcome, {safe_input}!</h1>"  # Input is now sanitized

    return response  # Safe rendering of user input


if __name__ == "__main__":
    app.run(debug=True)