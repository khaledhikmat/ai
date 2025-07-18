from typing import Dict, List, Protocol, Optional, Any
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    """Represents a document chunk."""
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    token_count: Optional[int] = None
    
    def __post_init__(self):
        """Calculate token count if not provided."""
        if self.token_count is None:
            # Rough estimation: ~4 characters per token
            self.token_count = len(self.content) // 4


# chunker services must implement this protocol
class IChunkerService(Protocol): 
    async def chunk_document(
        self,
        content: str,
        title: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Chunk TEXT."""
        pass

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        pass

