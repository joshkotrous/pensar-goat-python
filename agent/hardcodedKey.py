import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Create separate messages for system instructions and user input
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant. Answer the user's query helpfully and accurately."
        },
        {
            "role": "user", 
            "content": user_input
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,  # Use proper message structure
        api_key=OPENAI_API_KEY,  # Insecure key handling (not the focus of this fix)
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))