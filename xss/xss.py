from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    # Escape user input to prevent XSS
    safe_input = escape(user_input)
    response = f"<h1>Welcome, {safe_input}!</h1>"

    return response  # Now rendering sanitized user input


if __name__ == "__main__":
    app.run(debug=True)