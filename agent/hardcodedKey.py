import os
import openai

# Secure API key retrieval from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running this script.")


def ai_agent(user_input):
    """An AI agent with improved protection against prompt injection."""
    # Use the OpenAI API with properly structured messages
    # This correctly separates system instructions from user input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
            {"role": "user", "content": user_input}
        ],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))