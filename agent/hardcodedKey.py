import openai
import os

# Use environment variables instead of hardcoded API keys
# To set: export OPENAI_API_KEY="your-key-here" (on Unix/Mac)
# To set: set OPENAI_API_KEY=your-key-here (on Windows)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def ai_agent(user_input):
    """A safer AI agent with improved prompt handling."""
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found in environment variables."
        
    # Use the messages array structure with proper role separation
    # instead of vulnerable string interpolation
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))