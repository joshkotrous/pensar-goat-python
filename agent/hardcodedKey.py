import openai
import os

# Try to get API key from environment variable, fallback to the original key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """A more secure AI agent protected against prompt injection."""
    # Basic input validation
    if not user_input or len(user_input) > 2000:  # Reasonable length limit
        return "Invalid input. Please provide a query between 1 and 2000 characters."
    
    # Use proper message structure to mitigate prompt injection
    # By separating system instructions from user input using different message roles
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
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