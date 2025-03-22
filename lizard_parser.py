import os
import lizard
import logging
logging.basicConfig(level=logging.DEBUG)

def analyze_codebase(directory):
    """Analyze all code files in the given directory."""
    results = []
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return results
        
    # Walk through all files in the directory
    for root, _, files in os.walk(directory):
        for file in files:
            # Check for Python files
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Analyzing file: {file_path}")
                
                try:
                    # Analyze the file with lizard
                    analysis = lizard.analyze_file(file_path)
                    
                    # Extract file information
                    file_info = {
                        'path': file_path,
                        'name': file,
                        'functions': []
                    }
                    
                    # Extract function information
                    for func in analysis.function_list:
                        function_info = {
                            'name': func.name,
                            'start_line': func.start_line,
                            'end_line': func.end_line,
                            'complexity': func.cyclomatic_complexity,
                            'parameters': func.parameters
                        }
                        file_info['functions'].append(function_info)
                    
                    results.append(file_info)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {str(e)}")
    
    print(f"Found {len(results)} files with code")
    return results

# Example usage
if __name__ == "__main__":
    result = analyze_codebase("your_code_directory")
    print(result)
