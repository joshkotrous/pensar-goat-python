from flask import Flask, request, escape

app = Flask(__name__)


@app.route("/")
def home():
    """Secure against reflected XSS."""
    user_input = request.args.get("name", "")
    safe_input = escape(user_input)
    response = f"<h1>Welcome, {safe_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run(debug=True)