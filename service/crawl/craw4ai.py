from urllib.parse import urldefrag
from typing import Dict, List, Any
import re
import logging

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher

from service.config.typex import IConfigService

logger = logging.getLogger(__name__)

# compliant with ICrawlService protocol
class AICrawlService:
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service

    def _is_gitlab_url(self, url: str) -> bool:
        """Check if the URL is a GitLab URL."""
        gitlab_base_url = self.config_service.get_gitlab_base_url()
        if gitlab_base_url:
            return gitlab_base_url in url
        return 'gitlab' in url.lower()

    def _convert_to_api_url(self, url: str) -> str:
        """Convert GitLab web URL to API URL for better access."""
        if self.config_service.get_repo_type() == "gitlab" and self._is_gitlab_url(url):
            gitlab_base_url = self.config_service.get_gitlab_base_url()
            if gitlab_base_url and gitlab_base_url in url:
                # Convert URLs like:
                # https://gitlab.com/user/repo/-/blob/main/README.md
                # to API format:
                # https://gitlab.com/api/v4/projects/user%2Frepo/repository/files/README.md/raw?ref=main
                
                # Extract project path and file path
                parts = url.split('/-/')
                if len(parts) >= 2:
                    base_part = parts[0]
                    file_part = parts[1]
                    
                    # Extract project path (remove base URL)
                    project_path = base_part.replace(gitlab_base_url.rstrip('/') + '/', '')
                    
                    # Handle blob URLs
                    if file_part.startswith('blob/'):
                        file_info = file_part.replace('blob/', '')
                        path_parts = file_info.split('/', 1)
                        if len(path_parts) >= 2:
                            ref = path_parts[0]
                            file_path = path_parts[1]
                            
                            # Encode project path for API
                            import urllib.parse
                            encoded_project = urllib.parse.quote(project_path, safe='')
                            encoded_file_path = urllib.parse.quote(file_path, safe='')
                            
                            api_url = f"{gitlab_base_url.rstrip('/')}/api/v4/projects/{encoded_project}/repository/files/{encoded_file_path}/raw?ref={ref}"
                            return api_url
        
        return url

    def _get_auth_headers(self, url: str) -> Dict[str, str]:
        """Get authentication headers for the given URL."""
        headers = {
            # Always add User-Agent to avoid being blocked
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        if self.config_service.get_repo_type() == "gitlab" and self._is_gitlab_url(url):
            gitlab_token = self.config_service.get_gitlab_token()
            logger.info(f"Processing GitLab URL: {url}")
            logger.info(f"GitLab token available: {'Yes' if gitlab_token else 'No'}")
            
            if gitlab_token:
                # GitLab authentication methods:
                # 1. PRIVATE-TOKEN header (most common for Personal Access Tokens)
                # 2. Authorization: Bearer (for OAuth tokens)
                # 3. Authorization: Basic (for username:token)
                
                if '/api/v4/' in url:
                    # API URL - use PRIVATE-TOKEN
                    headers['PRIVATE-TOKEN'] = gitlab_token
                    logger.info("Using PRIVATE-TOKEN for GitLab API URL")
                else:
                    # Web URL - try multiple auth methods
                    headers['PRIVATE-TOKEN'] = gitlab_token
                    headers['Authorization'] = f'Bearer {gitlab_token}'
                    logger.info("Using both PRIVATE-TOKEN and Bearer for GitLab web URL")
                
                # Accept headers for better compatibility
                headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                headers['Accept-Language'] = 'en-US,en;q=0.5'
                headers['Accept-Encoding'] = 'gzip, deflate, br'
                headers['Connection'] = 'keep-alive'
                headers['Upgrade-Insecure-Requests'] = '1'
            else:
                logger.warning("No GitLab token found in environment variables")
            
        return headers

    async def crawl(self, start_urls, max_depth, max_concurrent) -> List[Dict[str,Any]]:
        """Returns list of dicts with url and markdown."""
        dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=70.0,
            check_interval=1.0,
            max_session_permit=max_concurrent
        )

        visited = set()

        def normalize_url(url):
            return urldefrag(url)[0]

        current_urls = set([normalize_url(u) for u in start_urls])
        results_all = []

        # Group URLs by their required headers
        for depth in range(max_depth):
            urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]
            if not urls_to_crawl:
                break

            # Group URLs by their auth requirements
            auth_groups = {}
            for url in urls_to_crawl:
                # Convert GitLab URLs to API format if possible
                processed_url = self._convert_to_api_url(url)
                url_headers = self._get_auth_headers(processed_url)
                headers_key = str(sorted(url_headers.items())) if url_headers else "no_auth"
                if headers_key not in auth_groups:
                    auth_groups[headers_key] = {'urls': [], 'headers': url_headers}
                auth_groups[headers_key]['urls'].append(processed_url)

            next_level_urls = set()
            
            # Process each group with appropriate headers
            for group_data in auth_groups.values():
                group_urls = group_data['urls']
                group_headers = group_data['headers']
                
                # Create browser config with appropriate headers
                browser_config = BrowserConfig(
                    headless=True, 
                    verbose=False,
                    headers=group_headers if group_headers else None
                )
                
                # Create crawler run config
                run_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS, 
                    stream=False
                )

                async with AsyncWebCrawler(config=browser_config) as crawler:
                    if len(group_urls) == 1:
                        # Single URL
                        result = await crawler.arun(url=group_urls[0], config=run_config)
                        results = [result]
                    else:
                        # Multiple URLs with same headers
                        results = await crawler.arun_many(urls=group_urls, config=run_config, dispatcher=dispatcher)

                    for result in results:
                        norm_url = normalize_url(result.url)
                        visited.add(norm_url)

                        if result.success and result.markdown:
                            results_all.append({'url': result.url, 'markdown': result.markdown})
                            for link in result.links.get("internal", []):
                                next_url = normalize_url(link["href"])
                                if next_url not in visited:
                                    next_level_urls.add(next_url)

            current_urls = next_level_urls

        return results_all

    def finalize(self) -> None:
        return None
