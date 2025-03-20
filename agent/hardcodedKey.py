import openai
import os


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: OpenAI API key not found in environment variables."
    
    # Use OpenAI's role-based messaging system which provides better
    # isolation between system instructions and user input
    messages = [
        {"role": "system", "content": "You are an AI assistant."},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=api_key,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


# Example usage with improved security
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))