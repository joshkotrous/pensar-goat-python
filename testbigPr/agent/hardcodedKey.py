import openai
import os  # Added for environment variable access


def ai_agent(user_input):
    """An AI agent with potential prompt injection risk."""
    # Check if API key is available in environment
    api_key = os.environ.get('OPENAI_API_KEY')
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
            api_key=api_key,  # Using environment variable instead of hardcoded key
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))
