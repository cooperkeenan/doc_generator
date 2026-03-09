from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from github_client import GitHubClient
from ast_parser import parse_repository

load_dotenv()

app = FastAPI()

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store tokens in memory (for MVP only - use proper storage later)
user_tokens = {}

class AuthCallback(BaseModel):
    code: str

class RepoRequest(BaseModel):
    repo_owner: str
    repo_name: str
    access_token: str

@app.get("/")
def root():
    return {"status": "Doc Generator API"}

@app.post("/auth/github/callback")
async def github_callback(callback: AuthCallback):
    """Exchange OAuth code for access token"""
    client = GitHubClient()
    token = await client.exchange_code_for_token(callback.code)
    
    # In production, store this securely with user session
    user_id = "temp_user"  # For MVP, just one user
    user_tokens[user_id] = token
    
    return {"access_token": token}

@app.get("/repos")
async def list_repos(access_token: str):
    """List user's repositories"""
    client = GitHubClient(access_token)
    repos = await client.list_repositories()
    return {"repositories": repos}

@app.post("/analyze")
async def analyze_repo(repo: RepoRequest):
    """Download and analyze a repository"""
    client = GitHubClient(repo.access_token)
    
    # Download repository contents
    repo_contents = await client.download_repository(
        repo.repo_owner, 
        repo.repo_name
    )
    
    # Parse Python files using AST
    analysis = parse_repository(repo_contents)
    
    return {
        "repo": f"{repo.repo_owner}/{repo.repo_name}",
        "analysis": analysis
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)