import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def sanitize_user_input(input_str):
    """Basic sanitization of user input to prevent prompt injection attempts."""
    # Define a list of suspicious patterns
    suspicious_patterns = [
        "ignore previous instructions",
        "disregard",
        "forget",
        "system prompt",
        "instructions:",
        "act as",
        "new role"
    ]
    
    input_lower = input_str.lower()
    for pattern in suspicious_patterns:
        if pattern in input_lower:
            return "I detect potential prompt injection in your query. Please rephrase your question."
    
    # Limit the length of input to prevent exploitation
    max_length = 500
    if len(input_str) > max_length:
        return input_str[:max_length] + "... (input truncated for security)"
    
    return input_str


def ai_agent(user_input):
    """An AI agent with improved security against prompt injection."""
    # Sanitize user input
    sanitized_input = sanitize_user_input(user_input)
    
    # If the sanitization function detected prompt injection, return the warning
    if "detect potential prompt injection" in sanitized_input:
        return sanitized_input
    
    # Use OpenAI's message structure to separate system instructions from user content
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
            {"role": "user", "content": sanitized_input}
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