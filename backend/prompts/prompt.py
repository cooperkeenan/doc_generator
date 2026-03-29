PROMPT = """You are analyzing a Python codebase. Here is the structure extracted from AST parsing:

{file_summaries}

Generate a Mermaid.js architecture diagram that shows the key components and their relationships.

REQUIREMENTS:
1. Use 'graph LR' or 'graph TD' syntax
2. Show main components (classes/modules that represent logical units)
3. Show meaningful relationships between components (data flow, dependencies)
4. Use clear, descriptive node labels (not raw filenames)
5. Group related components if there are architectural patterns (e.g., models, services, controllers, utilities)

EXCLUDE:
- Test files (already filtered out)
- Utility/helper imports (like 'os', 'sys', 'json')
- Every single import (only show architecturally significant dependencies)

KEEP IT CLEAN:
- Maximum 10-15 nodes for readability
- Focus on the most important components and relationships
- If there are many similar files, group them into a single node (e.g., "Data Models" instead of listing every model file)

OUTPUT FORMAT:
Return ONLY valid Mermaid.js code. Do not include:
- Markdown code fences (```)
- Explanations or commentary
- Multiple diagram options

Start with 'graph LR' or 'graph TD' and provide clean, renderable Mermaid syntax.

EXAMPLE OUTPUT FORMAT:
graph LR
    A[User Service] --> B[Database]
    A --> C[Authentication]
    D[API Controller] --> A
    E[Product Service] --> B
    D --> E
"""