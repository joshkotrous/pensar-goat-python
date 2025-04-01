from flask import Flask, request
import html
import os  # Import os module for environment variables

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {html.escape(user_input)}!</h1>"  # Input properly sanitized

    return response  # Rendering sanitized user input


if __name__ == "__main__":
    # Use environment variable to control debug mode
    # Set FLASK_DEBUG=1 to enable debug mode during development
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)