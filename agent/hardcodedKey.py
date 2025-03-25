import openai
import os

# Secure API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def ai_agent(user_input):
    """An AI agent that uses environment variables for API keys."""
    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    
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