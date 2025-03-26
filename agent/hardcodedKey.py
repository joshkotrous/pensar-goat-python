import openai
import os

# Load API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check if API key is available at startup
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Please set this environment variable before running the script.")
    print("Example: export OPENAI_API_KEY='your-api-key'")


def ai_agent(user_input):
    """An AI agent that processes user queries using OpenAI's API."""
    # Check if API key is available before making API call
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."
    
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