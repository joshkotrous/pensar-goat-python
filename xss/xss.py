from flask import Flask, request, escape

app = Flask(__name__)


@app.route("/")
def home():
    """No longer vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Input sanitized

    return response


if __name__ == "__main__":
    app.run(debug=True)