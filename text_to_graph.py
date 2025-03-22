import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in your .env file")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def convert_to_graph_td(text):
    """
    Convert input text to Mermaid graph TD format using Gemini API.
    
    Args:
        text (str): Input text describing relationships or processes
        
    Returns:
        str: Mermaid graph TD formatted string
    """
    prompt = f"""
    Convert the following text into a Mermaid graph TD format. 
    The output should only contain the graph TD code without any additional text.
    Focus on representing key relationships and processes.
    Input text: {text}
    
    Example format:
    graph TD
        A[Step 1] --> B[Step 2]
        B --> C[Step 3]
    """
    
    try:
        response = model.generate_content(prompt)
        # Extract just the graph TD code
        graph_code = response.text.strip()
        if not graph_code.startswith('graph TD'):
            graph_code = 'graph TD\n' + graph_code
        return graph_code
    except Exception as e:
        return f"Error generating graph: {str(e)}"

def main():
    print("Enter text to convert to Mermaid graph TD format (Ctrl+C to exit):")
    print("Example: 'User logs in, then checks email, then logs out'")
    
    try:
        while True:
            text = input("\nEnter your text: ")
            if text.strip():
                result = convert_to_graph_td(text)
                print("\nMermaid Graph TD Format:")
                print(result)
                print("\n---")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
