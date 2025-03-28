import openai
import os

# Use environment variables for API key
# Set your key using: export OPENAI_API_KEY="your-key-here"
# or in your environment configuration

    """A secured AI agent with protection against prompt injection."""
    # Basic input validation
    if not user_input or len(user_input) > 1000:  # Limit input length
        return "Invalid input. Please provide a reasonable query (less than 1000 characters)."

    # Use proper role-based message structure with OpenAI API
    # This prevents prompt injection by clearly separating system instructions from user input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
            {"role": "user", "content": user_input}
        ],
        api_key=OPENAI_API_KEY,
    )
        response = openai.ChatCompletion.create(
    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))
# Example usage
if __name__ == "__main__":
    print("AI Assistant (type 'exit' or 'quit' to end)")
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))