import openai
import os

# Get API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable not set. "
        "Please set this variable to your OpenAI API key before running the script."
    )


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    # Using the official message structure prevents many prompt injection attacks
    # by clearly separating system instructions from user input
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant. Answer the following user query helpfully and safely."
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


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))