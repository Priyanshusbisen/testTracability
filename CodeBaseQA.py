import openai
from CodeHelp import generate_answer

# Initialize OpenAI and Qdrant API keys and clients if not done elsewhere in your program
openai.api_key = "your-openai-api-key"  # replace with your OpenAI API key

# Function for terminal-based Q&A
def terminal_qa():
    print("Welcome to the Codebase Q&A!")
    print("Type 'exit' to quit.\n")

    while True:
        # Get user input for the question and optional team
        query = input("Ask a question about the codebase: ")
        if query.lower() == 'exit':
            print("Goodbye!")
            break

        team = input("Specify team (or press Enter to search all teams): ")
        if team.strip() == "":
            team = None  # No team specified means search all teams

        # Call the generate_answer function with the query and team
        try:
            answer = generate_answer(query, team=team)
            print("\nAnswer:\n", answer, "\n")
        except Exception as e:
            print(f"Error: {e}")

# Main function to start Q&A session
if __name__ == "__main__":
    terminal_qa()
