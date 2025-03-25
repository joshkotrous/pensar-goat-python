from flask import Flask, request, escape

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Input sanitization added

    return response  # Now safely rendering user input


if __name__ == "__main__":
    app.run(debug=True)