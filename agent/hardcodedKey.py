import openai
import os

# Secure API key handling using environment variables
# Set your API key as an environment variable: export OPENAI_API_KEY="your-api-key"
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")


def ai_agent(user_input):
    """An AI agent that answers user queries."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))