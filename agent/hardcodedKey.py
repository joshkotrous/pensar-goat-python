import openai
import os
import re

# Get API key from environment variable instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it with your API key.")


def ai_agent(user_input):
    """A more secure AI agent that prevents prompt injection."""
    # Basic input validation
    if not user_input or len(user_input.strip()) < 2:
        return "Input too short, please provide a valid query."
    
    # Check for common prompt injection patterns
    prompt_injection_patterns = [
        r"ignore previous instructions",
        r"forget your instructions",
        r"you are now",
        r"system:",
        r"new instructions:",
    ]
    
    for pattern in prompt_injection_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return "Sorry, your input contains patterns that aren't allowed."
    
    # Use a structured approach with separate system and user messages
    # This prevents user input from manipulating the system instructions
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
            {"role": "user", "content": user_input}
        ],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))