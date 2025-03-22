from flask import Flask, request, jsonify
from lizard_parser import analyze_codebase
from graph_builder import build_dependency_graph
import networkx as nx

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    directory = data.get("directory")
    
    if not directory:
        return jsonify({"error": "Missing directory parameter"}), 400

    print(f"Analyzing directory: {directory}")
    analysis_result = analyze_codebase(directory)
    graph = build_dependency_graph(analysis_result)

    # Convert to serializable format
    nodes_with_attrs = []
    for node in graph.nodes:
        attrs = graph.nodes[node]
        nodes_with_attrs.append({
            "id": node,
            "type": attrs.get("type", "unknown"),
            "name": attrs.get("name", node)
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
    
    return jsonify(graph_data)

if __name__ == "__main__":
    app.run(debug=True)
