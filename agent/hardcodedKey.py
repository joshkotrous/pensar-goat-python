import openai
import os

# Use environment variables for API keys instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def ai_agent(user_input):
    """A secured AI agent resistant to prompt injection."""
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found in environment variables."
    
    try:
        # Use the OpenAI recommended approach with separate messages
        # This helps prevent prompt injection by clearly defining roles
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
                {"role": "user", "content": user_input}
            ],
            api_key=OPENAI_API_KEY,
        )
        return response["choices"][0]["message"]["content"]
    except Exception:
        return "An error occurred while processing your request."


# Example usage
while True:
    try:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))
    except KeyboardInterrupt:
        print("\nExiting...")
        break