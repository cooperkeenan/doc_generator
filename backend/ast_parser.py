import ast
from typing import Dict, List, Tuple


def parse_file(content: str, filepath: str) -> Dict:
    """Parse a Python file and extract structure including function calls"""
    try:
        tree = ast.parse(content)
        
        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "module": alias.name,
                        "alias": alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "from": module,
                        "import": alias.name,
                        "alias": alias.asname
                    })
        
        # Extract functions
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "lineno": node.lineno
                })
        
        # Extract classes
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    n.name for n in node.body 
                    if isinstance(n, ast.FunctionDef)
                ]
                classes.append({
                    "name": node.name,
                    "methods": methods,
                    "lineno": node.lineno
                })
        
        # NEW: Extract function calls
        function_calls = extract_function_calls(tree)
        
        return {
            "imports": imports,
            "functions": functions,
            "classes": classes,
            "function_calls": function_calls,  # NEW
            "filepath": filepath
        }
    except Exception as e:
        return {"error": str(e), "filepath": filepath}


def extract_function_calls(tree: ast.AST) -> List[Dict]:
    """Extract all function/method calls from the AST"""
    calls = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_info = parse_call_node(node)
            if call_info:
                calls.append(call_info)
    
    return calls


def parse_call_node(node: ast.Call) -> Dict:
    """Parse a function call node to extract what's being called"""
    
    # Direct function call: foo()
    if isinstance(node.func, ast.Name):
        return {
            "type": "function",
            "name": node.func.id,
            "full_call": node.func.id
        }
    
    # Method call: obj.method()
    elif isinstance(node.func, ast.Attribute):
        # Try to resolve the object name
        obj_name = get_name_from_node(node.func.value)
        method_name = node.func.attr
        
        return {
            "type": "method",
            "object": obj_name,
            "method": method_name,
            "full_call": f"{obj_name}.{method_name}" if obj_name else method_name
        }
    
    return None


def get_name_from_node(node) -> str:
    """Recursively extract name from nested attribute/name nodes"""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        base = get_name_from_node(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    elif isinstance(node, ast.Call):
        # Handle chained calls: foo().bar()
        return get_name_from_node(node.func)
    else:
        return ""


def build_dependency_graph(files: Dict) -> Dict:
    """Build a simple dependency graph showing which files import which"""
    graph = {}
    
    # First, create a mapping of module names to file paths
    module_to_file = {}
    for filepath in files.keys():
        if "error" in files[filepath]:
            continue
            
        # Convert filepath to module name
        # e.g., "agents/supervisor/service.py" -> "agents.supervisor.service"
        module_name = filepath.replace("/", ".").replace(".py", "")
        module_to_file[module_name] = filepath
        
        # Also add shorter versions
        parts = module_name.split(".")
        for i in range(len(parts)):
            partial = ".".join(parts[i:])
            if partial not in module_to_file:
                module_to_file[partial] = filepath
    
    for filepath, file_data in files.items():
        if "error" in file_data:
            continue
            
        dependencies = []
        for imp in file_data.get("imports", []):
            # Try to match import to a file in the repo
            module = imp.get("from") or imp.get("module")
            if not module:
                continue
            
            # Try exact match first
            if module in module_to_file:
                dependencies.append(module_to_file[module])
                continue
            
            # Try with .py extension
            potential_file = module.replace(".", "/") + ".py"
            if potential_file in files:
                dependencies.append(potential_file)
                continue
            
            # Try partial matches (for relative imports)
            for module_key, file_path in module_to_file.items():
                if module_key.endswith(module) or module in module_key:
                    dependencies.append(file_path)
                    break
        
        graph[filepath] = dependencies
    
    return graph


def build_call_graph(files: Dict) -> Dict:
    """
    Build a call graph showing which files call functions in other files.
    Returns: {source_file: [(target_file, function_name), ...]}
    """
    call_graph = {}
    
    # Build a map of function names to files that define them
    function_to_file = {}
    for filepath, file_data in files.items():
        if "error" in file_data:
            continue
        
        for func in file_data.get("functions", []):
            func_name = func["name"]
            if func_name not in function_to_file:
                function_to_file[func_name] = []
            function_to_file[func_name].append(filepath)
        
        for cls in file_data.get("classes", []):
            for method in cls.get("methods", []):
                method_name = f"{cls['name']}.{method}"
                if method_name not in function_to_file:
                    function_to_file[method_name] = []
                function_to_file[method_name].append(filepath)
    
    # Now match function calls to their definitions
    for filepath, file_data in files.items():
        if "error" in file_data:
            continue
        
        calls_to = []
        
        for call in file_data.get("function_calls", []):
            call_name = call["full_call"]
            
            # Try to find which file defines this function
            if call_name in function_to_file:
                for target_file in function_to_file[call_name]:
                    if target_file != filepath:  # Don't include self-calls
                        calls_to.append((target_file, call_name))
        
        if calls_to:
            call_graph[filepath] = calls_to
    
    return call_graph