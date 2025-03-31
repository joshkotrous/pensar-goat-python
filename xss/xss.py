import os
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Sanitize input

    return response  # Safely rendering user input


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)