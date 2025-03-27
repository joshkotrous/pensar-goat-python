import openai
import re

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def is_potential_prompt_injection(user_input):
    """
    Check if the user input might contain a prompt injection attempt.
    
    This function checks for common patterns used in prompt injection attacks.
    """
    suspicious_patterns = [
        r"ignore previous instructions",
        r"disregard previous",
        r"forget your instructions",
        r"ignore your programming",
        r"new instructions:",
        r"you are now",
        r"act as ",
        r"system: ",
        r"developer mode",
        r"admin mode",
        r"user:",
        r"ignore everything above",
        r"\[\[\[",  # Triple brackets often used to try to escape context
        r"```system",  # Attempting to inject system messages
    ]
    
    # Check if any suspicious pattern is in the input
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input.lower()):
            return True
    
    return False


def ai_agent(user_input):
    """A secured AI agent with prompt injection protection."""
    # Validate user input
    if not user_input.strip():
        return "I cannot process empty queries. Please provide a valid question."
        
    if is_potential_prompt_injection(user_input):
        return "I've detected potentially unsafe instructions in your query. Please rephrase your question."
    
    # Use the OpenAI recommended message structure instead of embedding in a string
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))