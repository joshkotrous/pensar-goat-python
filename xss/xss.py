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
</affected_code>
    # To run in debug mode, set FLASK_DEBUG=1 in your environment
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    
    app.run(debug=debug_mode)