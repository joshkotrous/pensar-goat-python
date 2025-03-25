import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A more secure AI agent with protection against prompt injection."""
    # Using separate messages for system instructions and user input
    # This properly isolates the system instructions from user input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system", 
                "content": "You are an AI assistant. Answer the following user query."
            },
            {
                "role": "user", 
                "content": user_input
            }
        ],
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))