from flask import Flask, request
import html

app = Flask(__name__)


@app.route("/")
def home():
    """Previously vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {html.escape(user_input)}!</h1>"  # Input sanitized with html.escape()

    return response


if __name__ == "__main__":
    app.run(debug=True)