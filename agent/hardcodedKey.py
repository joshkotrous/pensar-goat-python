import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    # Sanitize and validate user input
    sanitized_input = sanitize_user_input(user_input)
    
    # Use a structured message format instead of raw string interpolation
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": sanitized_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

def sanitize_user_input(input_text):
    """Sanitize user input to prevent prompt injection."""
    # Remove any attempts to inject system prompts or role definitions
    forbidden_patterns = ["system:", "assistant:", "role:", "you are", "you're an", "<|"]
    sanitized = input_text
    for pattern in forbidden_patterns:
        sanitized = sanitized.lower().replace(pattern.lower(), "")
    return sanitized.strip()

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))
