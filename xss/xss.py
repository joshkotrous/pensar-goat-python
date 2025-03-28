from flask import Flask, request
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {user_input}!</h1>"  # No input sanitization

    return response  # Directly rendering user input


if __name__ == "__main__":
    # Get debug setting from environment variable, default to False for safety
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t", "yes")
    app.run(debug=debug_mode)