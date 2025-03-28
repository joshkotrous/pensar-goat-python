import openai
import os

# Get API key from environment variables, fall back to old method with warning
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
if OPENAI_API_KEY == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
    print("WARNING: Using placeholder API key. Set OPENAI_API_KEY environment variable for security.")


def ai_agent(user_input):
    """An AI agent with protection against prompt injection."""
    try:
        # Basic validation
        if not isinstance(user_input, str):
            raise ValueError("User input must be a string")
        
        if len(user_input) > 4000:  # Set a reasonable limit
            raise ValueError("User input exceeds maximum allowed length (4000 characters)")
        
        # Use OpenAI's structured message format instead of embedding input in a prompt string
        messages = [
            {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
            {"role": "user", "content": user_input}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,
        )
        )
        return response["choices"][0]["message"]["content"]
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))