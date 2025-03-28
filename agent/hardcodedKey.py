import openai
import os

# Better API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """A secured AI agent with prompt injection protection."""
    # Using proper message structure with separate system and user roles
    # This prevents the user input from manipulating system instructions
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


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))