import openai
import os

# Get the API key from environment variables
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Please set it using: export OPENAI_API_KEY='your-api-key' (Unix/Linux/MacOS)")
    print("or: set OPENAI_API_KEY=your-api-key (Windows CMD)")
    print("or: $env:OPENAI_API_KEY = 'your-api-key' (Windows PowerShell)")
    exit(1)


def ai_agent(user_input):
    """An AI agent that securely handles API keys."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,  # Now uses environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))