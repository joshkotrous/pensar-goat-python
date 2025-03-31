import openai
import os

# Secure API key handling from environment variables
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running this script.")


def ai_agent(user_input):
    """A secure AI agent with prompt injection protection."""
    # Use the ChatGPT message structure properly to prevent prompt injection
    # This isolates user input within its own message, preventing it from modifying instructions
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,  # Key now securely obtained from environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))