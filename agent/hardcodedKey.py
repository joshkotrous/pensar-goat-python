import openai
import os

# Secure API key handling using environment variables
# Set your API key as an environment variable: OPENAI_API_KEY


def ai_agent(user_input):
    """An AI agent that securely handles API keys."""
    # Check if API key is available in environment
    if not os.environ.get("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY environment variable is not set. Please set it before using this application."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        # API key is retrieved from environment variables
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))