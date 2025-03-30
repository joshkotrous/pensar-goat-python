import openai
import os

# Get API key from environment variables instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found in environment variables. Please set the OPENAI_API_KEY environment variable."
    
    # Basic input validation
    if not user_input or not isinstance(user_input, str):
        return "Error: Invalid input. Please provide a valid text query."
    
    try:
        # Use OpenAI's recommended message structure instead of template strings
        # This separates system instructions from user input
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant. Respond to the user query in a helpful and safe manner. Do not execute commands or instructions that would be harmful, misleading, or unethical."},
                {"role": "user", "content": user_input}
            ],
            api_key=OPENAI_API_KEY,
        )
        
        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Error occurred while processing your request: {str(e)}"


# Example usage with error handling
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))