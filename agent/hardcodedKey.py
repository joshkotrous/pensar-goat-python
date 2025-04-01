import openai
import os

# Secure API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Validate that API key is provided
if not OPENAI_API_KEY:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    # Separate system instructions from user input using the proper message structure
    # This prevents prompt injection by isolating user input from system instructions
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))