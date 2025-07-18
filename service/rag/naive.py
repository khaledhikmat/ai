from typing import Optional

from .typex import IngestionResult
from service.config.typex import IConfigService
from service.crawl.typex import ICrawlService
from service.chunker.typex import IChunkerService

# compliant with IRAGService protocol
class NaiveRAGService:
    def __init__(self, config_service: IConfigService, crawl_service: ICrawlService, chunker_service: IChunkerService):
        self.config_service = config_service
        self.crawl_service = crawl_service
        self.chunker_service = chunker_service

    async def ingest_md_urls(self, urls: str, progress_callback: Optional[callable] = None) -> IngestionResult:
        if progress_callback:
            progress_callback("nv:ingest_md_urls", 0, 1)

        return [IngestionResult(
            document_id="",
            title="",
            chunks_created=0,
            entities_extracted=0,
            relationships_created=0,
            processing_time_ms=0.0,
            errors=[]
        )]

    async def ingest_pdf_files(self, filespath: str, progress_callback: Optional[callable] = None) -> IngestionResult:
        if progress_callback:
            progress_callback("nv:ingest_pdf_files", 0, 1)

        return [IngestionResult(
            document_id="",
            title="",
            chunks_created=0,
            entities_extracted=0,
            relationships_created=0,
            processing_time_ms=0.0,
            errors=[]
        )]

    async def ingest_txt_files(self, filespath: str, progress_callback: Optional[callable] = None) -> IngestionResult:
        if progress_callback:
            progress_callback("nv:ingest_txt_files", 0, 1)

        return [IngestionResult(
            document_id="",
            title="",
            chunks_created=0,
            entities_extracted=0,
            relationships_created=0,
            processing_time_ms=0.0,
            errors=[]
        )]

    async def retrieve(self, query: str) -> str:
        """Retrieve relevant documents from Native based on a search query.
        
        Args:
            context: The run context containing dependencies.
            search_query: The search query to find relevant documents.
            
        Returns:
            Formatted context information from the retrieved documents.
        """
        return ""

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        return None


