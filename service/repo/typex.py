from typing import List, Protocol

# repo services must implement this protocol
class IRepoService(Protocol): 
    async def get_md_urls(self, repo_url: str) -> List[str]:
        """Get repository markdown URLs."""
        pass

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        pass

