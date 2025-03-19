import openai
import os

# API key should be retrieved from environment variables, not hardcoded
# OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Removed hardcoded key


def ai_agent(user_input):
    """A secured AI agent with protection against prompt injection."""
    # Get API key from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    
    # Use the OpenAI messages structure properly instead of building a prompt string
    # This separates the system instructions from user input to prevent prompt injection
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
            {"role": "user", "content": user_input}
        ],
        api_key=api_key,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))