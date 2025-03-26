from flask import Flask, request
import html

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    escaped_input = html.escape(user_input)
    response = f"<h1>Welcome, {escaped_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run(debug=True)