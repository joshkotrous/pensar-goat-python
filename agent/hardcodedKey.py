import openai
import os

# Use environment variables for API key security
# Set this in your environment: OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


def ai_agent(user_input):
    """A secure AI agent that mitigates prompt injection risk."""
    # Properly separate system instructions from user input using the messages structure
    messages = [
        {"role": "system", "content": "You are an AI assistant."},
        {"role": "user", "content": user_input}
    ]

    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: API key not found in environment variables."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=api_key,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))