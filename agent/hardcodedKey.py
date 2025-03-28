import openai
import os

# Get API key from environment variables instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


def ai_agent(user_input):
    """A more secure AI agent with mitigations for prompt injection risk."""
    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: API key not found. Please set the OPENAI_API_KEY environment variable."
    
    # Basic input validation and length limiting
    if not isinstance(user_input, str) or not user_input.strip():
        return "Invalid input. Please provide a valid query."
    user_input = user_input[:1000].strip()
    
    # Use separate system and user messages to prevent prompt injection
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]
while True:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))