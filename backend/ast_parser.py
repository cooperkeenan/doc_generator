import ast
from typing import Dict, List

def parse_repository(files: Dict[str, str]) -> Dict:
    """Parse all Python files in repository"""
    analysis = {
        "files": {},
        "dependency_graph": {},
        "summary": {
            "total_files": len(files),
            "total_functions": 0,
            "total_classes": 0
        }
    }
    
    for filepath, content in files.items():
        file_analysis = parse_python_file(content, filepath)
        analysis["files"][filepath] = file_analysis
        analysis["summary"]["total_functions"] += len(file_analysis["functions"])
        analysis["summary"]["total_classes"] += len(file_analysis["classes"])
    
    # Build dependency graph
    analysis["dependency_graph"] = build_dependency_graph(analysis["files"])
    
    return analysis

def parse_python_file(content: str, filepath: str) -> Dict:
    """Parse a single Python file using AST"""
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"error": str(e), "filepath": filepath}
    
    imports = []
    functions = []
    classes = []
    
    for node in ast.walk(tree):
        # Extract imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "module": alias.name,
                    "alias": alias.asname
                })
        
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append({
                    "module": f"{node.module}.{alias.name}" if node.module else alias.name,
                    "alias": alias.asname,
                    "from": node.module
                })
        
        # Extract function definitions
        elif isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                "calls": extract_function_calls(node)
            })
        
        # Extract class definitions
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                "methods": [
                    method.name for method in node.body 
                    if isinstance(method, ast.FunctionDef)
                ]
            })
    
    return {
        "filepath": filepath,
        "imports": imports,
        "functions": functions,
        "classes": classes
    }

def extract_function_calls(function_node: ast.FunctionDef) -> List[str]:
    """Extract function calls within a function"""
    calls = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return calls

def build_dependency_graph(files: Dict) -> Dict:
    """Build a simple dependency graph showing which files import which"""
    graph = {}
    
    for filepath, file_data in files.items():
        if "error" in file_data:
            continue
            
        dependencies = []
        for imp in file_data.get("imports", []):
            # Try to match import to a file in the repo
            module = imp.get("from") or imp.get("module")
            if module:
                # Convert module path to file path
                potential_file = module.replace(".", "/") + ".py"
                if potential_file in files:
                    dependencies.append(potential_file)
        
        graph[filepath] = dependencies
    
    return graph