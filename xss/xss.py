from flask import Flask, request, escape
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Added sanitization

    return response  # Now rendering sanitized user input


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "").lower() == "true"
    app.run(debug=debug_mode)