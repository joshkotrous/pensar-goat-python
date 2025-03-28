import openai
import os

# Secure API key handling using environment variables
# Users need to set the OPENAI_API_KEY environment variable before running this script
# For example: export OPENAI_API_KEY="your-api-key-here" (Unix/Linux/MacOS)
# or: set OPENAI_API_KEY=your-api-key-here (Windows)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,  # Using environment variable instead of hardcoded key
    )

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))