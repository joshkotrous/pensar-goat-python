from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {user_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run()