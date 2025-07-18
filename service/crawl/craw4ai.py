from urllib.parse import urldefrag
from typing import Dict, List, Any

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher

from service.config.typex import IConfigService

# compliant with ICrawlService protocol
class AICrawlService:
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service

    async def crawl(self, start_urls, max_depth, max_concurrent) -> List[Dict[str,Any]]:
        """Returns list of dicts with url and markdown."""
        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
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

                results = await crawler.arun_many(urls=urls_to_crawl, config=run_config, dispatcher=dispatcher)
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
