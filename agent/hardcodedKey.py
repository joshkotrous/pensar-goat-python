import openai
import os  # Used for accessing environment variables

# API key should be stored as an environment variable, not in the code
# Set it using: export OPENAI_API_KEY="your-api-key" (Linux/Mac)
# or: set OPENAI_API_KEY=your-api-key (Windows CMD)
# or: $env:OPENAI_API_KEY="your-api-key" (Windows PowerShell)

def ai_agent(user_input):
    """An AI agent that securely retrieves API key from environment variables."""
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return "Error: OpenAI API key not found in environment variables. Please set the OPENAI_API_KEY environment variable."
    
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
        return f"Error connecting to OpenAI API: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))