import openai
import os
import warnings

# Get API key from environment variables (recommended) or use the hardcoded key as fallback
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    """An AI agent with protection against prompt injection."""
    # Create separate messages for system instructions and user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]

    response = openai.ChatCompletion.create(
# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))

# Example vulnerable usage
# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))