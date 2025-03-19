import openai
import os

# Secure API key handling using environment variables
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    if not OPENAI_API_KEY:
        raise KeyError("OPENAI_API_KEY environment variable is empty")
except KeyError:
    raise RuntimeError("OPENAI_API_KEY environment variable not set. Set this variable with your OpenAI API key before running.")


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
        api_key=OPENAI_API_KEY,  # Now using the environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))