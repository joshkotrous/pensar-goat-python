import openai
import os

# Get API key from environment variables instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def validate_input(user_input):
    """Basic input validation."""
    if not user_input or not user_input.strip():
        raise ValueError("Input cannot be empty")
    
    if len(user_input) > 1000:  # Set a reasonable limit
        raise ValueError("Input exceeds maximum allowed length")
    
    return user_input.strip()


def ai_agent(user_input):
    """An AI agent with protection against prompt injection."""
    try:
        # Validate API key
        if not OPENAI_API_KEY:
            raise ValueError("API key is missing. Set the OPENAI_API_KEY environment variable.")
        
        # Validate user input
        validated_input = validate_input(user_input)
        
        # Use OpenAI's structured message format instead of f-strings
        # This approach separates system instructions from user input
        messages = [
            {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
            {"role": "user", "content": validated_input}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,
        )
        
        return response["choices"][0]["message"]["content"]
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        # Log the error in a production environment
        return f"An error occurred while processing your request: {str(e)}"


# Example usage
if __name__ == "__main__":
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))