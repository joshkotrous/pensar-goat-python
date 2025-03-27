from flask import Flask, request
import os  # Added to access environment variables

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {user_input}!</h1>"  # No input sanitization

    return response  # Directly rendering user input


if __name__ == "__main__":
    # Use environment variable to control debug mode, default to False for production safety
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)