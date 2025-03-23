import openai
import os

# Use environment variable for API key with fallback for backward compatibility
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """An AI agent with protection against prompt injection."""
    # Basic input validation
    if not user_input or len(user_input) > 1000:  # Simple length check
        return "I'm sorry, I cannot process empty requests or requests that are too long."
    
    # Use proper message structure to separate system instructions from user input
    # This mitigates prompt injection by keeping system instructions separate from user content
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))