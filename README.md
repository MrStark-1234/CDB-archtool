# Text to Mermaid Graph Converter

This tool converts natural language text into Mermaid's graph TD (Top-Down) format using the Google Gemini API.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Run the script:
```bash
python text_to_graph.py
```

## Usage

1. Enter your text description when prompted
2. The script will convert it to Mermaid graph TD format
3. Use Ctrl+C to exit

The output can be used in any Mermaid-compatible markdown viewer or editor.

## Example

Input:
```
User logs in, then checks email, then logs out
```

Output:
```
graph TD
    A[User Login] --> B[Check Email]
    B --> C[User Logout]
```
