import openai
import os

# Secure API key handling using environment variables
# Users should set OPENAI_API_KEY in their environment
# For example: export OPENAI_API_KEY="your-api-key" (Unix/Linux/MacOS)
# or set OPENAI_API_KEY=your-api-key (Windows)

def ai_agent(user_input):
    """An AI agent that uses environment variables for API keys."""
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable is not set. Please set it before using this function."
    
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