from urllib.parse import urldefrag
from typing import Dict, List, Any
import re

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher

from service.config.typex import IConfigService

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

    def _get_auth_headers(self, url: str) -> Dict[str, str]:
        """Get authentication headers for the given URL."""
        headers = {}
        if self._is_gitlab_url(url):
            gitlab_token = self.config_service.get_gitlab_token()
            if gitlab_token:
                headers['Authorization'] = f'Bearer {gitlab_token}'
        return headers

    async def crawl(self, start_urls, max_depth, max_concurrent) -> List[Dict[str,Any]]:
        """Returns list of dicts with url and markdown."""
        browser_config = BrowserConfig(headless=True, verbose=False)
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

        async with AsyncWebCrawler(config=browser_config) as crawler:
            for depth in range(max_depth):
                urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]
                if not urls_to_crawl:
                    break

                # For each batch of URLs, use appropriate headers
                configs_for_urls = []
                for url in urls_to_crawl:
                    url_headers = self._get_auth_headers(url)
                    url_config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS, 
                        stream=False,
                        headers=url_headers if url_headers else None
                    )
                    configs_for_urls.append(url_config)

                # Use the first config if all URLs need the same auth, otherwise crawl individually
                if len(set(str(config.headers) for config in configs_for_urls)) == 1:
                    results = await crawler.arun_many(urls=urls_to_crawl, config=configs_for_urls[0], dispatcher=dispatcher)
                else:
                    # Crawl each URL individually with its specific config
                    results = []
                    for url, config in zip(urls_to_crawl, configs_for_urls):
                        result = await crawler.arun(url=url, config=config)
                        results.append(result)
                next_level_urls = set()

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
