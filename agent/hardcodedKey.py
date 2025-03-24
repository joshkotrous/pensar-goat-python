import openai
import os

# Use environment variable for API key
# Requires setting OPENAI_API_KEY environment variable
# e.g., export OPENAI_API_KEY="your-api-key"


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Input validation
    if not user_input or user_input.strip() == "":
        return "Please provide a valid query."
    
    # Using the OpenAI message structure instead of string concatenation
    # This properly separates system instructions from user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]

    try:
        # Get API key from environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OpenAI API key not found in environment variables."
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=api_key,
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