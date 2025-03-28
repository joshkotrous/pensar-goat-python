import openai
import os

# More secure API key handling using environment variables if available
# But keeping backward compatibility with existing code
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

def sanitize_input(user_input):
    """Basic input sanitization to help mitigate prompt injection risks."""
    # Remove any attempt to escape or create new sections
    if not isinstance(user_input, str):
        return str(user_input)
    
    sanitized = user_input.replace("\n", " ")
    return sanitized

def ai_agent(user_input):
    """A more secure AI agent with reduced prompt injection risk."""
    # Sanitize the user input
    sanitized_input = sanitize_input(user_input)
    
    # Use OpenAI's chat format correctly with separate messages for system and user
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant. Answer the following user query:"
        },
        {
            "role": "user", 
            "content": sanitized_input
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))
            api_key=OPENAI_API_KEY,
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating response: {str(e)}"


# Example usage
if __name__ == "__main__":
    print("AI Assistant (type 'exit' or 'quit' to end)")
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))