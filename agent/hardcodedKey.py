import openai
import os

# Securely retrieve API key from environment variables
# You must set the OPENAI_API_KEY environment variable before running this script
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Verify the API key is available
if not OPENAI_API_KEY:
    raise ValueError("The OPENAI_API_KEY environment variable is not set. Please set it before running this script.")


def ai_agent(user_input):
    """An AI agent with secure credential handling."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,  # Securely using environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))