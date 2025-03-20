import openai
import os

# Secure API key handling using environment variables
def get_api_key():
    """Retrieve API key from environment variable safely."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
    return api_key


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
        api_key=get_api_key(),  # Secure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))