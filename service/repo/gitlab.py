import re
import os
import httpx
from typing import List

http_client = httpx.AsyncClient()

# compliant with IRepoService protocol
class GitlabRepoService:
    def __init__(self, config_service):
        self.config_service = config_service
        self.http_client = httpx.AsyncClient()

        if not self.config_service.get_gitlab_token() or not self.config_service.get_gitlab_slug() or not self.config_service.get_gitlab_base_url():
            raise ValueError("GITLAB_TOKEN, GITLAB_SLUG and GITLAB_BASE_URL environment variables must be set")

    async def get_md_urls(self, repo_url: str) -> List[str]:
        """
        Get the directory structure of a GitLab repository.
        and return .md files only

        Args:
            repo_url: The GitLab repository URL.

        Returns:
            Directory of files.
        """
        match = re.search(r'gitlab\.[^/]+/([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
        if not match:
            raise ValueError("Invalid GitLab URL format")
        
        owner, repo = match.groups()
        headers = {'Authorization': f'Bearer {self.config_service.get_gitlab_token() }'}
        
        structure = []
        page = 1
        per_page = 100

        while True:
            params = {"recursive": "true", "page": page, "per_page": per_page}
            response = await self.http_client.get(
                f'{self.config_service.get_gitlab_base_url()}/api/v4/projects/{owner}%2F{repo}/repository/tree',
                headers=headers,
                params=params
            )

            response.raise_for_status()
        
            data = response.json()
            if not data:
                break

            for item in data:
                if item.get('type') == 'blob' and not any(excluded in item['path'] for excluded in ['.git/', 'node_modules/', '__pycache__/']):
                    if item['path'].endswith('.md'):
                        structure.append(f"{repo_url}/{self.config_service.get_gitlab_slug()}/{item['path']}")

            next_page_header = response.headers.get('x-next-page')
            if next_page_header:
                page = int(next_page_header)
            else:
                break
        
        return structure

    def finalize(self) -> None:
        return None
