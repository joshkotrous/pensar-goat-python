import html
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    """Protected from reflected XSS."""
    user_input = request.args.get("name", "")
    sanitized_input = html.escape(user_input)  # Sanitize user input
    response = f"<h1>Welcome, {sanitized_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run(debug=True)