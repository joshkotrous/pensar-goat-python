import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A more secure AI agent with prompt injection risk mitigated."""
    # Basic input validation
    if not user_input or len(user_input.strip()) == 0:
        return "Empty queries are not allowed."
    
    if len(user_input) > 1000:
        return "Query is too long. Please keep your questions concise."
    
    # Use the proper message structure to separate system instructions from user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,  # Insecure key handling remains unchanged
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))