import openai
import os

# Secure API key handling using environment variables
# The API key should be set in the environment as OPENAI_API_KEY
# For example, in Unix-like systems: export OPENAI_API_KEY=sk-your-key-here
# In Windows: set OPENAI_API_KEY=sk-your-key-here


def ai_agent(user_input):
    """An AI agent that securely handles API keys."""
    # Get API key from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable not set. Please set it and try again."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=api_key,  # Secure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))