import re
import os
import httpx
from typing import List

from service.config.typex import IConfigService

# compliant with IRepoService protocol
class GithubRepoService:
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service
        self.http_client = httpx.AsyncClient()

        if not self.config_service.get_github_token or not self.config_service.get_github_slug:
            raise ValueError("GITHUB_TOKEN and GITHUB_SLUG environment variables must be set")

    async def get_md_urls(self, repo_url: str) -> List[str]:
        """
        Get the directory structure of a GitLab repository. 
        and return .md files only

        Args:
            repo_url: The GitLab repository URL.

        Returns:
            Directory of files.
        """
        match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
        if not match:
            raise ValueError("Invalid GitHub URL format")
        
        if not self.config_service.get_github_token():
            raise ValueError("GITHUB_TOKEN environment variable must be set")

        owner, repo = match.groups()
        headers = {'Authorization': f'token {self.config_service.get_github_token()}'}
        
        response = await self.http_client.get(
            f'https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1',
            headers=headers
        )
        
        if response.status_code != 200:
            # Try with master branch if main fails
            response = await self.http_client.get(
                f'https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1',
                headers=headers
            )
            if response.status_code != 200:
                raise ValueError(f"Failed to get repository structure: {response.text}")
        
        data = response.json()
        tree = data['tree']
        
        # Build directory structure
        structure = []
        for item in tree:
            if not any(excluded in item['path'] for excluded in ['.git/', 'node_modules/', '__pycache__/']):
                # structure.append(f"{'📁 ' if item['type'] == 'tree' else '📄 '}{item['path']}")
                if item['path'].endswith('.md'):
                    structure.append(f"{repo_url}/{self.config_service.get_github_slug()}/{item['path']}")
        
        return structure

    def finalize(self) -> None:
        return None
