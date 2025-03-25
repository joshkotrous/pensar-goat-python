import openai
import os

# Secure API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


def ai_agent(user_input):
    """A more secure AI agent with prompt injection protection."""
    # Basic input validation
    if not user_input.strip():
        return "Error: Input cannot be empty."
    
    # Use the messages array structure instead of a raw prompt string
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found in environment variables."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with AI service: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))