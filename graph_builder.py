import networkx as nx
import matplotlib.pyplot as plt
import os

def build_dependency_graph(analysis_results):
    """Build a dependency graph from code analysis results."""
    G = nx.DiGraph()
    
    # No files analyzed
    if not analysis_results:
        print("No files to build graph from")
        return G
    
    # Add nodes for each file
    for file_info in analysis_results:
        file_path = file_info['path']
        G.add_node(file_path, type='file', name=file_info['name'])
        
        # Add nodes for each function
        for func in file_info.get('functions', []):
            func_id = f"{file_path}::{func['name']}"
            G.add_node(func_id, type='function', name=func['name'])
            
            # Connect file to function
            G.add_edge(file_path, func_id, type='contains')
    
    # Try to infer dependencies between files
    # This is a simplified approach - you might need more sophisticated parsing
    for file_info in analysis_results:
        file_path = file_info['path']
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                
                # Look for import statements (very basic approach)
                for other_file in analysis_results:
                    other_name = os.path.splitext(other_file['name'])[0]
                    if f"import {other_name}" in content or f"from {other_name}" in content:
                        G.add_edge(file_path, other_file['path'], type='imports')
            except Exception as e:
                print(f"Error processing {file_path} for dependencies: {str(e)}")
    
    print(f"Built graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
    return G

def visualize_graph(graph):
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=3000, font_size=10)
    plt.show()

# Example usage
if __name__ == "__main__":
    sample_data = [
        {"path": "main.py", "name": "main", "functions": [{"name": "process_data"}], "dependencies": ["utils.py"]},
        {"path": "utils.py", "name": "utils", "functions": [{"name": "helper_func"}], "dependencies": []}
    ]
    graph = build_dependency_graph(sample_data)
    visualize_graph(graph)
