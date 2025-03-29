import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A more secure AI agent with mitigated prompt injection risk."""
    # Using the OpenAI message structure properly to separate system instructions from user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}  # User input isolated in its own message
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,  # Using structured messages instead of string interpolation
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))