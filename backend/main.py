from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import anthropic
import json
import logging

from github_client import GitHubClient
from ast_parser import parse_file, build_dependency_graph
from prompts.prompt import PROMPT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
github_client = GitHubClient(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET")
)
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class GitHubCallbackRequest(BaseModel):
    code: str


class AnalyzeRequest(BaseModel):
    access_token: str
    repo_name: str


@app.get("/")
async def root():
    return {"message": "Doc Generator API"}


@app.post("/auth/github/callback")
async def github_callback(request: GitHubCallbackRequest):
    """Exchange GitHub OAuth code for access token"""
    try:
        token_data = github_client.exchange_code_for_token(request.code)
        logger.info("Successfully exchanged OAuth code for access token")
        return {"access_token": token_data["access_token"]}
    except Exception as e:
        logger.error(f"Failed to exchange OAuth code: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/repos")
async def list_repos(access_token: str):
    """List user's repositories"""
    try:
        repos = github_client.list_repositories(access_token)
        python_repos = [
            repo for repo in repos 
            if repo.get("language") == "Python"
        ]
        logger.info(f"Found {len(python_repos)} Python repositories out of {len(repos)} total")
        return {"repositories": python_repos}
    except Exception as e:
        logger.error(f"Failed to list repositories: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze")
async def analyze_repo(request: AnalyzeRequest):
    """Analyze a repository and generate diagrams"""
    try:
        logger.info(f"Starting analysis for repository: {request.repo_name}")
        
        # Download repository files
        files = github_client.download_repository(
            request.access_token,
            request.repo_name
        )
        logger.info(f"Downloaded {len(files)} files from repository")
        
        # Filter out test files and unwanted directories
        python_files = []
        for file_path, content in files.items():
            if any(exclude in file_path.lower() for exclude in [
                'test_', 'tests/', '__pycache__', '.pytest_cache', 
                'venv/', '.git/', '.github/', 'node_modules/'
            ]):
                continue
            if file_path.endswith('.py'):
                python_files.append((file_path, content))
        
        logger.info(f"Filtered to {len(python_files)} Python files (excluding tests)")
        
        # Parse files with AST
        files_analysis = {}
        for file_path, content in python_files:
            files_analysis[file_path] = parse_file(content, file_path)
        
        logger.info(f"Parsed {len(files_analysis)} files with AST")
        
        # Build basic dependency graph
        dependency_graph = build_dependency_graph(files_analysis)
        logger.info("Built dependency graph")
        
        # Generate diagram using LLM
        logger.info("Calling LLM to generate diagram...")
        mermaid_code = await generate_diagram_with_llm(files_analysis, dependency_graph)
        logger.info("Diagram generated successfully")
        
        return {
            "repo": request.repo_name,
            "analysis": {
                "summary": {
                    "total_files": len(files_analysis),
                    "total_functions": sum(len(f.get("functions", [])) for f in files_analysis.values() if "functions" in f),
                    "total_classes": sum(len(f.get("classes", [])) for f in files_analysis.values() if "classes" in f),
                },
                "files": files_analysis,
                "dependency_graph": dependency_graph
            },
            "diagrams": {
                "architecture": mermaid_code
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing repository: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def generate_diagram_with_llm(files_analysis: dict, dependency_graph: dict) -> str:
    """Use Claude to generate a meaningful Mermaid diagram from AST data"""
    
    # Prepare structured summary for the LLM
    file_summaries = []
    for filepath, data in files_analysis.items():
        if "error" in data:
            continue
        
        summary = {
            "file": filepath,
            "imports": [imp.get("module") or imp.get("from") for imp in data.get("imports", [])],
            "functions": [f["name"] for f in data.get("functions", [])],
            "classes": [c["name"] for c in data.get("classes", [])]
        }
        file_summaries.append(summary)
    
    logger.info(f"Prepared summaries for {len(file_summaries)} files")
    
    # Format prompt with actual file data
    prompt = PROMPT.format(
        file_summaries=json.dumps(file_summaries, indent=2)
    )
    
    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        mermaid_code = message.content[0].text.strip()
        
        # Remove markdown code fences if present
        if mermaid_code.startswith("```"):
            lines = mermaid_code.split("\n")
            mermaid_code = "\n".join(lines[1:-1])
        
        logger.info("LLM successfully generated Mermaid diagram")
        return mermaid_code
    except Exception as e:
        logger.error(f"Error generating diagram with LLM: {str(e)}", exc_info=True)
        return "graph LR\n    A[Error generating diagram] --> B[Check API key and logs]"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)