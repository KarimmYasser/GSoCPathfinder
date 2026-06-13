import httpx
import re
from typing import Optional, List
from pydantic import BaseModel

class GitHubIssue(BaseModel):
    title: str
    url: str
    labels: List[str]
    number: int

def parse_github_repo(url: str) -> Optional[str]:
    """Extract 'owner/repo' from a GitHub URL."""
    if not url:
        return None
    match = re.search(r'github\.com/([^/]+/[^/]+)(?:\.git|/|$)', url)
    if match:
        repo = match.group(1).rstrip('/')
        return repo
    return None

async def fetch_good_first_issues(url: str) -> List[GitHubIssue]:
    """Fetch 'good first issue' or 'help wanted' issues for a given repo URL."""
    repo = parse_github_repo(url)
    if not repo:
        return []
        
    api_url = f"https://api.github.com/repos/{repo}/issues"
    
    # Using a generic query for open issues with specific labels
    # Note: GitHub API limits unauthenticated requests to 60/hr
    params = {
        "state": "open",
        "labels": "good first issue",
        "sort": "updated",
        "direction": "desc",
        "per_page": 5
    }
    
    issues = []
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    # Exclude pull requests
                    if "pull_request" not in item:
                        issues.append(GitHubIssue(
                            title=item.get("title", ""),
                            url=item.get("html_url", ""),
                            labels=[label.get("name", "") for label in item.get("labels", [])],
                            number=item.get("number", 0)
                        ))
            elif response.status_code == 404:
                pass # Repo might be private or deleted
        except Exception as e:
            print(f"Error fetching GitHub issues for {repo}: {e}")
            
    # If no 'good first issue', try 'help wanted'
    if not issues:
        params["labels"] = "help wanted"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(api_url, params=params, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    for item in data:
                        if "pull_request" not in item:
                            issues.append(GitHubIssue(
                                title=item.get("title", ""),
                                url=item.get("html_url", ""),
                                labels=[label.get("name", "") for label in item.get("labels", [])],
                                number=item.get("number", 0)
                            ))
            except Exception:
                pass

    return issues
