import os
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {user_input}!</h1>"  # No input sanitization

    return response  # Directly rendering user input


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true")
    app.run(debug=debug_mode)