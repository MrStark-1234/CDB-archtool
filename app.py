from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv
# Add these imports for code analysis
from lizard_parser import analyze_codebase
from graph_builder import build_dependency_graph
import ntpath

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

def shorten_path(path):
    """Extract just the filename from a full path."""
    return ntpath.basename(path)

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

# Add new code analysis endpoint
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    directory = data.get("directory")
    
    if not directory:
        return jsonify({"error": "Missing directory parameter"}), 400

    print(f"Analyzing directory: {directory}")
    analysis_result = analyze_codebase(directory)
    graph = build_dependency_graph(analysis_result)

    # Print graph structure to console
    print("\n=== GRAPH STRUCTURE ===")
    print(f"Total nodes: {len(graph.nodes())}")
    print(f"Total edges: {len(graph.edges())}")
    
    # Print node types
    node_types = {}
    for node, attrs in graph.nodes(data=True):
        node_type = attrs.get('type', 'unknown')
        if node_type not in node_types:
            node_types[node_type] = 0
        node_types[node_type] += 1
    
    print("\nNode types:")
    for node_type, count in node_types.items():
        print(f"  - {node_type}: {count}")
    
    # Print edge types
    edge_types = {}
    for source, target, attrs in graph.edges(data=True):
        edge_type = attrs.get('type', 'unknown')
        if edge_type not in edge_types:
            edge_types[edge_type] = 0
        edge_types[edge_type] += 1
    
    print("\nEdge types:")
    for edge_type, count in edge_types.items():
        print(f"  - {edge_type}: {count}")

    # Convert to serializable format with shortened paths
    nodes_with_attrs = []
    for node in graph.nodes:
        attrs = graph.nodes[node]
        # Shorten the ID and name if they are file paths
        node_id = node
        node_name = attrs.get('name', node)
        
        if attrs.get('type') == 'file':
            node_name = shorten_path(node_name)
        
        nodes_with_attrs.append({
            "id": node_id,
            "display_id": shorten_path(node_id) if '/' in node_id or '\\' in node_id else node_id,
            "type": attrs.get("type", "unknown"),
            "name": node_name
        })
    
    edges_with_attrs = []
    for source, target in graph.edges:
        attrs = graph.edges[(source, target)]
        edges_with_attrs.append({
            "source": source,
            "target": target,
            "type": attrs.get("type", "unknown")
        })

    graph_data = {
        "nodes": nodes_with_attrs,
        "edges": edges_with_attrs
    }
    
    # Print a sample of nodes and edges for verification
    print("\nSample nodes (first 5):")
    for node in nodes_with_attrs[:5]:
        print(f"  - {node['display_id']} ({node['type']}): {node['name']}")
    
    print("\nSample edges (first 5):")
    for edge in edges_with_attrs[:5]:
        source_name = next((n['name'] for n in nodes_with_attrs if n['id'] == edge['source']), edge['source'])
        target_name = next((n['name'] for n in nodes_with_attrs if n['id'] == edge['target']), edge['target'])
        print(f"  - {source_name} --({edge['type']})--> {target_name}")
    
    print("=====================\n")
    
    return jsonify(graph_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
