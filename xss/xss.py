from flask import Flask, request
import html  # Added for HTML escaping

app = Flask(__name__)


@app.route("/")
def home():
    """Previously vulnerable to reflected XSS - now fixed."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {html.escape(user_input)}!</h1>"  # Added HTML escaping

    return response


if __name__ == "__main__":
    app.run(debug=True)