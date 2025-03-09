from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    # Escape user input to prevent XSS
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"

    return response

if __name__ == "__main__":
    app.run(debug=False)
    app.run(debug=False)
    app.run(debug=True)
