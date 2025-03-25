import openai
import os

# Secure API key handling using environment variables
# You need to set the OPENAI_API_KEY environment variable before running this script
# Example: export OPENAI_API_KEY="your-api-key-here" (Linux/Mac)
# Example: set OPENAI_API_KEY=your-api-key-here (Windows)


def ai_agent(user_input):
    """An AI agent that securely handles API keys."""
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Check if the API key is available and not empty
    if not api_key or api_key.strip() == "":
        return "Error: OPENAI_API_KEY environment variable is not set or is empty. Please set it before using this agent."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            api_key=api_key,  # Secure key handling from environment
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with OpenAI API: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))