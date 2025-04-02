from flask import Flask, request
import html  # Added for HTML escaping

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {html.escape(user_input)}!</h1>"  # Added HTML escaping

    return response  # Now safely rendering user input


if __name__ == "__main__":
    app.run(debug=True)