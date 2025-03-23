# Text to Mermaid Graph Converter

This tool converts code-base into graph TD (Top-Down) format using the Google Gemini API.

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
python app.py
```

## Usage

1. Enter your text in the input field
2. Click on "Generate Graph"
3. View the generated Mermaid graph

The tool processes converts code-base into structured graph diagrams, making it useful for visualizing workflows, processes, and relationships between components.

## Example

Input:

```
User enters a public repository link,analyses
```

Output:

```
graph TD
    A[User Login] --> B[Check Email]
    B --> C[User Logout]
```

## Hosted Link

http://cdb-archtool.onrender.com
