# Code 2 Architecture

This tool converts code-base into a flow diagram using gemini,mermaid js and lizard parser.

## Hosted link
http://cdb-archtool.onrender.com

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

