import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A more secure AI agent implementation."""
    
    # Input validation
    if not user_input or not isinstance(user_input, str):
        return "Please provide a valid input."
    
    if len(user_input) > 4000:  # Reasonable length limit
        return "Input exceeds maximum allowed length."
    
    # Use proper message structure with separate system and user messages
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,  # Insecure key handling
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error processing request: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))