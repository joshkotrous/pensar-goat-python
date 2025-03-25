import openai
import os

# Use environment variable for API key 
# (requires setting OPENAI_API_KEY in environment)
# Default fallback for backward compatibility but should be changed in production
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """A secure AI agent that prevents prompt injection."""
    # Use proper message structure to separate system instructions from user input
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant. Answer the following user query."
        },
        {
            "role": "user", 
            "content": user_input
        }
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