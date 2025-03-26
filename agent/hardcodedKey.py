import openai
import os

# Secure API key handling (using environment variables instead of hardcoding)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Get API key from environment variable


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,  # Using environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))