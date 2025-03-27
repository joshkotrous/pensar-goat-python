import openai
import os
import re

# Get API key from environment variable
try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set your OpenAI API key as an environment variable.")
    exit(1)


def sanitize_user_input(user_input):
    """
    Basic input validation and sanitization.
    """
    # Ensure input is a string
    if not isinstance(user_input, str):
        return ""
    
    # Limit length
    if len(user_input) > 1000:
        user_input = user_input[:1000]
    
    # Remove control characters that might interfere with processing
    user_input = re.sub(r'[\x00-\x1F\x7F]', '', user_input)
    
    return user_input.strip()


def ai_agent(user_input):
    """A more secure AI agent with prompt injection mitigation."""
    # Sanitize the user input
    sanitized_input = sanitize_user_input(user_input)
    
    if not sanitized_input:
        return "Invalid input. Please provide a valid text query."
    
    # Use OpenAI's recommended message structure
    # This separates system instructions from user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Respond to the user's query helpfully and safely."},
        {"role": "user", "content": sanitized_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            # API key is automatically used from openai.api_key
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage
if __name__ == "__main__":
    print("AI Assistant (type 'exit' or 'quit' to end)")
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))