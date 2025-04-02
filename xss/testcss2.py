from flask import Flask, request
import html

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    safe_input = html.escape(user_input)  # Sanitize input by escaping HTML special characters
    response = f"<h1>Welcome, {safe_input}!</h1>"

    return response  # Rendering sanitized input


if __name__ == "__main__":
    app.run(debug=True)