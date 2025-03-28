import openai
import os

# Secure API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    """An AI agent protected against prompt injection."""
    
    # Properly structured messages with separation of system and user content
    messages = [
        {"role": "system", "content": "You are an AI assistant."},
        {"role": "user", "content": user_input}
    ]
        {
            "role": "user", 
            "content": user_input
        messages=messages,
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,  # Insecure key handling
# Example usage

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))