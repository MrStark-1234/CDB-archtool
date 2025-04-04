import time
import stat
from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv
# Add these imports for code analysis
from lizard_parser import analyze_codebase
from graph_builder import build_dependency_graph
import ntpath
import git
import tempfile
import shutil
import zipfile

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
        A --> B
        B --> C
        B --> D
    """
   
    try:
        response = model.generate_content(prompt)
        graph_code = clean_mermaid_code(response.text)
        return graph_code
    except Exception as e:
        return f"Error generating graph: {str(e)}"

def shorten_path(path, preserve_namespace=False):
    """Extract filename with optimal directory context."""
    if not path:
        return ""
   
    # Handle already shortened paths
    if "/" not in path and "\\" not in path:
        return path
   
    # Normalize path separators
    normalized_path = path.replace('\\', '/')
   
    # Get the filename (last part)
    parts = normalized_path.split('/')
    filename = parts[-1]
   
    if not preserve_namespace:
        return filename
   
    # Extract meaningful context - avoid full paths but keep useful structure
    context_parts = []
   
    # Identify relevant path components
    # Skip common non-meaningful directories
    skip_dirs = {'src', 'lib', 'app', 'source', 'main', 'test', 'bin', 'build', 'dist','venv', 'env', 'virtualenv', 'node_modules'}
   
    # Start from the end (nearest to filename) and collect up to 2 meaningful directory names
    i = len(parts) - 2  # Start with the directory containing the file
    context_count = 0
   
    while i >= 0 and context_count < 2:
        part = parts[i]
        # Skip generic directory names and empty parts
        if part and part.lower() not in skip_dirs:
            context_parts.insert(0, part)
            context_count += 1
        i -= 1
   
    # Assemble the shortened path
    if context_parts:
        return "/".join(context_parts) + "/" + filename
    else:
        return filename

def optimize_mermaid_for_large_graph(mermaid_code, node_count):
    """Optimize mermaid settings for large graphs."""
   
    # If we have a large graph, add configuration for better rendering
    if node_count > 20:
        # Insert configuration after graph TD
        config_line = "    %%{ init: { 'flowchart': { 'curve': 'basis', 'nodeSpacing': 50, 'rankSpacing': 70 } } }%%"
        lines = mermaid_code.split('\n')
        if lines[0].strip().startswith('graph TD'):
            lines.insert(1, config_line)
            return '\n'.join(lines)
   
    return mermaid_code

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
   
    # New filter options
    filters = {
        "node_types": data.get("node_types", []),
        "edge_types": data.get("edge_types", []),
        "search_term": data.get("search_term", ""),
        "max_nodes": data.get("max_nodes", 0)
    }
   
    if not directory:
        return jsonify({"error": "Missing directory parameter"}), 400

    graph_data = process_codebase(directory, filters)
    return jsonify(graph_data)

@app.route('/analyze_github', methods=['POST'])
def analyze_github():
    data = request.get_json()
    repo_url = data.get('repo_url')
    branch = data.get('branch', 'main')
   
    if not repo_url:
        return jsonify({"error": "Repository URL is required"}), 400
   
    temp_dir = None
    repo = None
   
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
       
        # Clone the repository
        print(f"Cloning {repo_url} (branch: {branch})...")
        repo = git.Repo.clone_from(repo_url, temp_dir, branch=branch, depth=1)
       
        # Process directly with the temporary directory path
        filters = {
            "node_types": data.get("node_types", []),
            "edge_types": data.get("edge_types", []),
            "search_term": data.get("search_term", ""),
            "max_nodes": data.get("max_nodes", 0)
        }
       
        graph_data = process_codebase(temp_dir, filters)
        return jsonify(graph_data)
   
    except Exception as e:
        print(f"Error analyzing repository: {str(e)}")
        return jsonify({"error": str(e)}), 500
   
    finally:
        # Clean up repository resources
        if repo is not None:
            try:
                repo.git.clear_cache()
                repo.close()
            except:
                pass
               
        # Clean up temporary directory with retry and error handling
        if temp_dir and os.path.exists(temp_dir):
            def handle_remove_readonly(func, path, exc_info):
                os.chmod(path, stat.S_IWRITE)
                func(path)
           
            time.sleep(1)
           
            try:
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
            except Exception as e:
                print(f"Warning: Could not remove temp dir {temp_dir}: {str(e)}")

@app.route('/upload', methods=['POST'])
def upload_code():
    if 'codebase' not in request.files:
        return jsonify({"error": "No file provided"}), 400
   
    file = request.files['codebase']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
       
    try:
        # Create temporary directory for extraction
        temp_dir = tempfile.mkdtemp()
        upload_path = os.path.join(temp_dir, file.filename)
       
        # Save and extract the zip file
        file.save(upload_path)
        with zipfile.ZipFile(upload_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
       
        # Get filter options from request
        filters = {}
        if request.form:
            filters = {
                "node_types": request.form.getlist("node_types"),
                "edge_types": request.form.getlist("edge_types"),
                "search_term": request.form.get("search_term", ""),
                "max_nodes": int(request.form.get("max_nodes", 0))
            }
       
        # Process directly with the temporary directory path
        graph_data = process_codebase(temp_dir, filters)
       
        # Clean up
        shutil.rmtree(temp_dir)
       
        return jsonify(graph_data)
   
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def filter_graph(graph, filters):
    """Filter the graph based on user-specified criteria."""
    import networkx as nx
   
    filtered_graph = graph.copy()
   
    # Filter by node type
    if filters["node_types"]:
        nodes_to_remove = [n for n, attrs in filtered_graph.nodes(data=True)
                         if attrs.get("type") not in filters["node_types"]]
        filtered_graph.remove_nodes_from(nodes_to_remove)
   
    # Filter by edge type
    if filters["edge_types"]:
        edges_to_remove = [(s, t) for s, t, attrs in filtered_graph.edges(data=True)
                         if attrs.get("type") not in filters["edge_types"]]
        filtered_graph.remove_edges_from(edges_to_remove)
   
    # Filter by search term
    if filters["search_term"]:
        search_term = filters["search_term"].lower()
        nodes_to_keep = [n for n, attrs in filtered_graph.nodes(data=True)
                        if search_term in n.lower() or
                           search_term in attrs.get("name", "").lower()]
        # Also keep adjacent nodes for context
        context_nodes = set()
        for node in nodes_to_keep:
            if node in filtered_graph:
                context_nodes.update(nx.neighbors(filtered_graph, node))
        nodes_to_keep.extend(context_nodes)
        filtered_graph = filtered_graph.subgraph(nodes_to_keep).copy()
   
    # Limit number of nodes (keep most connected nodes)
    if filters["max_nodes"] > 0 and len(filtered_graph) > filters["max_nodes"]:
        # Sort nodes by degree (number of connections)
        nodes_by_degree = sorted(filtered_graph.degree, key=lambda x: x[1], reverse=True)
        nodes_to_keep = [n[0] for n in nodes_by_degree[:filters["max_nodes"]]]
        filtered_graph = filtered_graph.subgraph(nodes_to_keep).copy()
   
    return filtered_graph

def calculate_edge_weights(graph):
    """Calculate edge weights based on relationship frequency."""
    # Create a counter for each unique source-target pair
    edge_counts = {}
   
    for source, target in graph.edges:
        if (source, target) not in edge_counts:
            edge_counts[(source, target)] = 0
        edge_counts[(source, target)] += 1
   
    # Normalize weights to a 1-10 scale
    if edge_counts:
        max_count = max(edge_counts.values())
        min_count = min(edge_counts.values())
        weight_range = max(1, max_count - min_count)
       
        # Set weights on edges
        for (source, target), count in edge_counts.items():
            if max_count == min_count:
                weight = 5  # Default middle weight if all edges have same count
            else:
                # Scale to 1-10 range
                weight = 1 + 9 * (count - min_count) / weight_range
            graph.edges[(source, target)]["weight"] = weight
   
    return graph

def detect_cycles(graph):
    """Detect cycles in the dependency graph."""
    import networkx as nx
   
    cycles = list(nx.simple_cycles(graph))
   
    # Mark nodes and edges involved in cycles
    cycle_nodes = set()
    cycle_edges = set()
   
    for cycle in cycles:
        # Add all nodes in this cycle
        cycle_nodes.update(cycle)
       
        # Add all edges in this cycle
        for i in range(len(cycle)):
            source = cycle[i]
            target = cycle[(i + 1) % len(cycle)]
            if graph.has_edge(source, target):
                cycle_edges.add((source, target))
   
    # Mark nodes involved in cycles
    for node in cycle_nodes:
        if "flags" not in graph.nodes[node]:
            graph.nodes[node]["flags"] = []
        graph.nodes[node]["flags"].append("in_cycle")
   
    # Mark edges involved in cycles
    for source, target in cycle_edges:
        if "flags" not in graph.edges[(source, target)]:
            graph.edges[(source, target)]["flags"] = []
        graph.edges[(source, target)]["flags"].append("in_cycle")
   
    return graph, cycles

def process_codebase(directory, filters=None):
    """
    Core function to analyze a codebase and generate graph data.
    This is used by analyze, analyze_github, and upload_code endpoints.
    """
    if filters is None:
        filters = {
            "node_types": [],
            "edge_types": [],
            "search_term": "",
            "max_nodes": 0
        }
   
    print(f"Analyzing directory: {directory}")
    analysis_result = analyze_codebase(directory)
    graph = build_dependency_graph(analysis_result)
   
    # Apply filters before processing
    if filters["node_types"] or filters["edge_types"] or filters["search_term"]:
        graph = filter_graph(graph, filters)

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

    # Add weight calculation
    graph = calculate_edge_weights(graph)
   
    # Detect cycles
    graph, cycles = detect_cycles(graph)
   
    # Convert to serializable format
    nodes_with_attrs = []
    for node in graph.nodes:
        attrs = graph.nodes[node]
        node_id = node
        node_name = attrs.get('name', node)
       
        # Always shorten node representation
        display_id = shorten_path(node_id, preserve_namespace=True)
        if attrs.get('type') == 'file':
            node_name = shorten_path(node_name, preserve_namespace=True)
       
        nodes_with_attrs.append({
            "id": node_id,
            "display_id": display_id,
            "type": attrs.get("type", "unknown"),
            "name": node_name,
            "flags": attrs.get("flags", [])
        })
   
    edges_with_attrs = []
    for source, target in graph.edges:
        attrs = graph.edges[(source, target)]
        edges_with_attrs.append({
            "source": source,
            "target": target,
            "type": attrs.get("type", "unknown"),
            "weight": attrs.get("weight", 1),
            "flags": attrs.get("flags", [])
        })
   
    # Add cycle information
    cycles_with_shortened_paths = []
    for cycle in cycles:
        shortened_cycle = [shorten_path(node, preserve_namespace=True) for node in cycle]
        cycles_with_shortened_paths.append({
            "nodes": cycle,
            "display_nodes": shortened_cycle,
            "length": len(cycle)
        })

    graph_data = {
        "nodes": nodes_with_attrs,
        "edges": edges_with_attrs,
        "cycles": cycles_with_shortened_paths
    }
    
   
    # Add warning for large graphs
    if len(graph.nodes()) > 100:
        graph_data["warning"] = "Large graph detected. Rendering may take time."
   
    return graph_data

if __name__ == '__main__':
    # For local development use debug mode and specific port
    # For Render deployment, use environment variables
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
