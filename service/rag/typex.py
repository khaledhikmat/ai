from typing import List, Protocol, Optional
from dataclasses import dataclass, field

@dataclass
class IngestionResult:
    document_id: str
    title: str
    chunks_created: int
    entities_extracted: int
    relationships_created: int
    processing_time_ms: float
    errors: List[str] = field(default_factory=list)

# rag services must implement this protocol
class IRAGService(Protocol): 
    async def ingest_md_urls(self, urls: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        """Ingest MD URLS into knowledge base."""
        pass

    async def ingest_pdf_files(self, files: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        """Ingest PDF files into knowledge base."""
        pass

    async def ingest_txt_files(self, files: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        """Ingest TXT files into knowledge base."""
        pass

    async def retrieve(query: str) -> str:
        """Retrieve relevant documents based on a search query."""
        pass
        
    def finalize(self) -> None:
        """Destruct the service and close resources."""
        pass