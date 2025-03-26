import openai
import os

# Use environment variable for API key instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # Fallback for compatibility


def ai_agent(user_input):
    """A more secure AI agent with prompt injection mitigation."""
    # Basic input validation
    if not isinstance(user_input, str):
        user_input = str(user_input)
    
    # Limit input length to prevent excessive usage
    user_input = user_input[:1000]
    
    # Using structured messages format instead of string interpolation
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