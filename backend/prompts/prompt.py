PROMPT = """You are a software architecture expert specializing in creating clear, meaningful architecture diagrams following the C4 Model principles created by Simon Brown.

You will analyze a Python codebase and generate a **System Context diagram** (C4 Level 1) that shows the high-level architecture.

# DIRECTORY STRUCTURE
Here is the folder organization of the codebase:

{directory_structure}

# FILE DETAILS
Here is the detailed structure extracted from AST parsing:

{file_summaries}

# YOUR TASK
Generate a Mermaid.js diagram that visualizes the system's architecture at the **CONTEXT LEVEL** - showing the main logical components and their relationships.

# CRITICAL: UNDERSTANDING HIERARCHY

## Use Directory Structure to Infer Architecture
**The folder structure reveals architectural hierarchy:**
- Root-level files (main.py, app.py, api.py) → **ENTRY POINTS / TOP LEVEL**
- Top-level folders → **MAJOR ARCHITECTURAL BOUNDARIES**
  - Example: `orchestrator/`, `agents/`, `tools/` indicate distinct layers
- Nested folders → **SUB-COMPONENTS**
  - Example: `agents/supervisor/`, `agents/regulatory/` are siblings within the agents layer

## Use Import Direction to Determine Hierarchy
**Who imports whom reveals the call hierarchy:**
- If `orchestrator/api.py` imports `agents/supervisor/service.py` → Orchestrator is ABOVE Supervisor
- If `agents/regulatory/service.py` imports `tools/search.py` → Agent is ABOVE Tools
- **Rule: A → B (A imports B) means A is higher in the hierarchy**

## Use Naming Patterns to Identify Roles
- **Orchestrator/Router/Gateway** → Coordinates requests, sits at TOP
- **Supervisor/Manager/Coordinator** → Manages sub-components, sits in MIDDLE
- **Agent/Service/Handler** → Performs specific tasks, sits BELOW supervisors
- **Tools/Utilities/Helpers** → Shared functions, sits at BOTTOM
- **API/Controllers** → Entry points for external requests, sits at TOP
- **Repository/DAO/Storage** → Data access, usually at BOTTOM

# C4 MODEL PRINCIPLES TO FOLLOW

## 1. APPROPRIATE ABSTRACTION LEVEL
- This is a **System Context / Container-level diagram** (C4 Level 1-2)
- Show **LOGICAL COMPONENTS** (services, modules, major subsystems), NOT individual files
- Group related files into meaningful architectural units
- Example: Instead of "user.py", "auth.py", "session.py" → show "Authentication Service"

## 2. IDENTIFY ARCHITECTURAL PATTERNS
Recognize common patterns and represent them clearly:
- **Layered Architecture**: Presentation → Business Logic → Data Access
- **Multi-Agent System**: Orchestrator → Supervisor Agents → Worker Agents → Tools
- **Microservices**: Independent services with clear boundaries
- **MVC Pattern**: Models, Views, Controllers as separate layers

## 3. COMPONENT CLASSIFICATION
Classify components based on their role (use directory paths, imports, and naming):
- **API/Controllers**: Handle HTTP requests, expose endpoints (FastAPI, Flask routes)
- **Orchestrators**: Route requests between services, coordinate workflows
- **Services/Agents**: Core application logic, specific domain tasks
- **Tools/Helpers**: Shared utilities used by services
- **Data Access**: Database queries, external API calls
- **External Systems**: Third-party APIs, databases, message queues

## 4. RELATIONSHIP CLARITY
- Show **meaningful dependencies** based on imports
- **Direction matters**: A → B means "A depends on B" or "A calls B"
- If orchestrator imports agent → `Orchestrator --> Agent`
- If agent imports tools → `Agent --> Tools`
- Focus on **architectural boundaries**, not every import

## 5. VISUAL CLARITY RULES
- **Maximum 8-12 nodes** for readability (group aggressively if needed)
- **Clear, descriptive labels**: "TREF Supervisor Agent" not "supervisor_agent.py"
- **Use subgraphs for architectural layers**:
  ```
  subgraph "Orchestration Layer"
      ORCH[Platform Orchestrator]
  end
  
  subgraph "Agent Layer"
      SUPER[Supervisor Agent]
      REG[Regulatory Agent]
  end
  ```
- **Arrange top-to-bottom** to show hierarchy clearly

## 6. WHAT TO EXCLUDE
- ❌ Test files (already filtered out)
- ❌ Individual Python files (show architectural components instead)
- ❌ Standard library imports (os, sys, json, datetime, etc.)
- ❌ Framework imports (fastapi, anthropic, httpx)
- ❌ Utility imports that don't represent architectural dependencies

# STEP-BY-STEP PROCESS

1. **Analyze directory structure** to identify major architectural boundaries
   - Root-level folders = major layers/modules
   - Nested folders = sub-components within a layer

2. **Trace imports** to build hierarchy
   - Who imports whom → who sits above whom
   - Orchestrator imports agents → orchestrator is top
   - Agents import tools → agents are middle, tools are bottom

3. **Group files into logical components**
   - Files in same folder with similar names = one component
   - Example: `supervisor_agent/api.py`, `supervisor_agent/service.py` → "Supervisor Agent Service"

4. **Identify external systems**
   - Imports like azure, anthropic, httpx → external dependencies
   - Show as external systems with cylinder notation: `DB[(Azure OpenAI)]`

5. **Draw the hierarchy**
   - Top layer: Entry points (orchestrator, main API)
   - Middle layers: Agents, services
   - Bottom layer: Tools, utilities
   - External layer: Third-party services

# DIAGRAM REQUIREMENTS

## Structure
- Use `graph TD` (top-down) to show hierarchy clearly
- Top = entry points, Bottom = utilities/external systems

## Node Format
```
ComponentID[Component Name]
```
- Component IDs: Short, alphanumeric (ORCH, SUPER, REG, TOOLS)
- Component Names: Clear, business-meaningful ("Platform Orchestrator" not "orchestrator")

## Subgraph Usage (REQUIRED)
Use subgraphs to show architectural layers:
```
subgraph "Layer Name"
    COMP1[Component 1]
    COMP2[Component 2]
end
```

## External Systems
Use cylinder notation for databases and external APIs:
```
OPENAI[(Azure OpenAI)]
SEARCH[(Azure Search)]
```

# EXAMPLE OUTPUT STRUCTURE

For a multi-agent system like Trisus Assist:

```mermaid
graph TD
    subgraph "Orchestration Layer"
        ORCH[Platform Orchestrator]
    end
    
    subgraph "Agent Layer"
        SUPER[TREF Supervisor Agent]
        REG[Regulatory Agent]
    end
    
    subgraph "Tool Layer"
        TOOLS[Agent Tools]
        SEARCH[Search Tools]
    end
    
    subgraph "External Systems"
        OPENAI[(Azure OpenAI)]
        STORAGE[(Table Storage)]
    end
    
    ORCH --> SUPER
    ORCH --> REG
    SUPER --> TOOLS
    REG --> SEARCH
    TOOLS --> OPENAI
    SEARCH --> STORAGE
```

# OUTPUT FORMAT
- Return **ONLY** valid Mermaid.js code
- Start with `graph TD` (top-down layout)
- **NO markdown code fences** (no ```)
- **NO explanations or commentary**
- **NO multiple diagram options**

# QUALITY CHECKLIST
Before outputting, ensure:
✅ 8-12 nodes maximum
✅ Hierarchy flows TOP → MIDDLE → BOTTOM
✅ Import direction matches visual hierarchy (if A imports B, A is above B)
✅ Directory structure is reflected in component grouping
✅ Clear component names (not filenames)
✅ Subgraphs used for architectural layers
✅ External systems marked with cylinder notation
✅ No standard library/framework imports shown

Generate the diagram now:
"""