from flask import Flask, render_template, request, jsonify
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

app = Flask(__name__)

def clean_mermaid_code(code):
    """Clean and format Mermaid graph code."""
    # Remove any markdown code blocks
    code = code.replace('```mermaid', '').replace('```', '')
    
    # Split into lines and remove empty lines
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    
    # Remove duplicate 'graph TD' statements
    graph_td_count = sum(1 for line in lines if line.lower().startswith('graph td'))
    if graph_td_count > 1:
        lines = [line for line in lines if not line.lower().startswith('graph td')]
        lines.insert(0, 'graph TD')
    elif graph_td_count == 0:
        lines.insert(0, 'graph TD')
    
    # Format the lines with proper indentation
    formatted_lines = []
    for i, line in enumerate(lines):
        if i == 0:  # First line (graph TD)
            formatted_lines.append(line)
        else:  # Other lines should be indented
            # Remove any existing indentation first
            line = line.lstrip()
            formatted_lines.append('    ' + line)
    
    return '\n'.join(formatted_lines)

def convert_to_graph_td(text):
    """Convert input text to Mermaid graph TD format using Gemini API."""
    prompt = f"""
    Convert the following text into a Mermaid flowchart using graph TD format.
    Rules:
    1. Use descriptive node labels in square brackets
    2. Use proper arrows (-->)
    3. Return only the flowchart code
    4. Each node should have a unique identifier
    5. Do not repeat 'graph TD' multiple times
    
    Input text: {text}
    
    Example format:
    graph TD
        A[First Step] --> B[Second Step]
        B --> C[Final Step]
        B --> D[Alternative Step]
    """
    
    try:
        response = model.generate_content(prompt)
        graph_code = clean_mermaid_code(response.text)
        return graph_code
    except Exception as e:
        return f"Error generating graph: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text = request.json.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    graph_code = convert_to_graph_td(text)
    return jsonify({'graph_code': graph_code})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
