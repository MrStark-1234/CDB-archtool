import ast
import os

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
        self.function_calls = set()
        self.classes = set()
        self.functions = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self.classes.add(node.name)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        self.generic_visit(node)

def analyze_python_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read())
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        return {
            "imports": list(analyzer.imports), 
            "function_calls": list(analyzer.function_calls),
            "classes": list(analyzer.classes),
            "functions": list(analyzer.functions)
        }
    except Exception as e:
        return {"error": str(e)}

def analyze_directory(directory_path):
    nodes = []
    edges = []
    file_data = {}
    
    # Walk through all files in directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory_path)
                nodes.append(relative_path)
                
                # Analyze the Python file
                analysis = analyze_python_code(file_path)
                file_data[relative_path] = analysis
                
                # Create edges based on imports
                for imported in analysis.get("imports", []):
                    possible_file = f"{imported.replace('.', '/')}.py"
                    if os.path.exists(os.path.join(directory_path, possible_file)):
                        edges.append({
                            "source": relative_path,
                            "target": possible_file,
                            "type": "import"
                        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "file_data": file_data
    }

# Example usage
if __name__ == "__main__":
    result = analyze_directory("./")
    print(result)
