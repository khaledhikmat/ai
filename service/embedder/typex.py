from typing import List, Protocol

# embedder services must implement this protocol
class IEmbedderService(Protocol): 
    async def embed(
        self,
        text: str) -> List[float]:
        """Embed TEXT."""
        pass

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        pass

