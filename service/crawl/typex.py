from typing import Dict, List, Protocol, Any

# crawl services must implement this protocol
class ICrawlService(Protocol): 
    async def crawl(self, urls, max_depth, max_concurrent) -> List[Dict[str,Any]]:
        """Crawl URLs."""
        pass

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        pass

