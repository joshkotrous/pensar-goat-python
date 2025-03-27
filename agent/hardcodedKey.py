import openai
import os

# Secure API key handling using environment variables
# Set your OPENAI_API_KEY as an environment variable before running this script


def ai_agent(user_input):
    """An AI agent that securely handles API keys."""
    # Check if the API key is set in the environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable not set."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=api_key,  # Using environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))