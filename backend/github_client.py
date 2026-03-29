import httpx
import os
from typing import List, Dict
import base64


class GitHubClient:
    def __init__(self, client_id: str = None, client_secret: str = None):
        """Initialize GitHub client with OAuth credentials"""
        self.client_id = client_id or os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GITHUB_CLIENT_SECRET")
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange OAuth code for access token (synchronous)"""
        with httpx.Client() as client:
            response = client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                }
            )
            response.raise_for_status()
            return response.json()
    
    def list_repositories(self, access_token: str) -> List[Dict]:
        """List user's repositories (synchronous)"""
        with httpx.Client() as client:
            response = client.get(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                params={"per_page": 100, "sort": "updated"}
            )
            response.raise_for_status()
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
    
    def download_repository(self, access_token: str, repo_full_name: str) -> Dict:
        """
        Download repository file tree
        
        Args:
            access_token: GitHub OAuth token
            repo_full_name: Full repository name (e.g., "username/repo")
        
        Returns:
            Dictionary mapping file paths to file contents
        """
        # Parse owner and repo from full name
        owner, repo = repo_full_name.split("/")
        
        with httpx.Client() as client:
            # Try 'main' branch first
            tree_response = client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            # Fallback to 'master' if 'main' doesn't exist
            if tree_response.status_code == 404:
                tree_response = client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
            
            tree_response.raise_for_status()
            tree = tree_response.json()
            
            # Download Python files only (for MVP)
            files = {}
            for item in tree.get("tree", []):
                if item["type"] == "blob" and item["path"].endswith(".py"):
                    try:
                        # Download file content
                        file_response = client.get(
                            f"https://api.github.com/repos/{owner}/{repo}/contents/{item['path']}",
                            headers={
                                "Authorization": f"Bearer {access_token}",
                                "Accept": "application/vnd.github.v3+json"
                            }
                        )
                        file_response.raise_for_status()
                        file_data = file_response.json()
                        
                        # Decode base64 content
                        content = base64.b64decode(file_data["content"]).decode("utf-8")
                        files[item["path"]] = content
                    except Exception as e:
                        print(f"Error downloading {item['path']}: {e}")
                        # Skip files that fail to download
                        continue
            
            return files