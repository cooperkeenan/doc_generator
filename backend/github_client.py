import httpx
import os
from typing import List, Dict
import base64

class GitHubClient:
    def __init__(self, access_token: str = None):
        self.access_token = access_token
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        
    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange OAuth code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                }
            )
            data = response.json()
            return data.get("access_token")
    
    async def list_repositories(self) -> List[Dict]:
        """List user's repositories"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                params={"per_page": 100, "sort": "updated"}
            )
            repos = response.json()
            
            return [
                {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "owner": repo["owner"]["login"],
                    "description": repo.get("description"),
                    "url": repo["html_url"],
                    "language": repo.get("language")
                }
                for repo in repos
            ]
    
    async def download_repository(self, owner: str, repo: str) -> Dict:
        """Download repository file tree"""
        async with httpx.AsyncClient() as client:
            # Get repository tree
            tree_response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if tree_response.status_code == 404:
                # Try 'master' branch if 'main' doesn't exist
                tree_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
            
            tree = tree_response.json()
            
            # Download Python files only (for MVP)
            files = {}
            for item in tree.get("tree", []):
                if item["type"] == "blob" and item["path"].endswith(".py"):
                    # Download file content
                    file_response = await client.get(
                        f"https://api.github.com/repos/{owner}/{repo}/contents/{item['path']}",
                        headers={
                            "Authorization": f"Bearer {self.access_token}",
                            "Accept": "application/vnd.github.v3+json"
                        }
                    )
                    file_data = file_response.json()
                    
                    # Decode base64 content
                    content = base64.b64decode(file_data["content"]).decode("utf-8")
                    files[item["path"]] = content
            
            return files