import openai
import os

# Get API key from environment variables (more secure)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Fallback for backward compatibility during transition
    OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    print("Warning: Using hardcoded API key. Set OPENAI_API_KEY environment variable instead.")


def ai_agent(user_input):
    """A more secure AI agent with protection against prompt injection."""
    # Using the proper message structure of the OpenAI API to separate
    # system instructions from user input, reducing prompt injection risk
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            # System message defines the AI's behavior and constraints
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
            # User message contains only the user's input
            {"role": "user", "content": user_input}
        ],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))