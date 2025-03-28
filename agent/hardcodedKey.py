import openai
import os

# Use environment variable for API key instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
# For example: export OPENAI_API_KEY="your-api-key" (Linux/Mac)

def ai_agent(user_input):
    """A more secure AI agent with reduced prompt injection risk."""
    # Use OpenAI's structured message format for proper role separation
    # This prevents prompt injection by isolating user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]
    response = openai.ChatCompletion.create(

# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))

# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))
        break
    print(ai_agent(user_query))