from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import asyncio

from .typex import IngestionResult
from service.config.typex import IConfigService
from service.crawl.typex import ICrawlService
from service.chunker.typex import IChunkerService, DocumentChunk
from service.graph.typex import IGraphService

# compliant with IRAGService protocol
class GraphRAGService:
    def __init__(self, config_service: IConfigService, crawl_service: ICrawlService, chunker_service: IChunkerService, graph_service: IGraphService):
        self.config_service = config_service
        self.crawl_service = crawl_service
        self.chunker_service = chunker_service
        self.graph_service = graph_service

    async def ingest_md_urls(self, urls: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        # Clear graph
        await self.graph_service.clear_graph()

        print(f"Received the following URLs to crawl and vectorize: {urls}")
        crawl_results = []
        crawl_results.extend(await self.crawl_service.crawl(urls, max_depth=1, max_concurrent=10))

        results = []

        # Initialize RAG instance and insert docs
        for i, doc in enumerate(crawl_results):
            url = doc['url']
            md = doc['markdown']
            if not md:
                print(f"Skipping {url} - no markdown content found")
                continue
            print(f"Inserting document from {url} into RAG...")

            results.append(await self._ingest_single_document(md))

            if progress_callback:
                progress_callback("gr:ingest_md_urls", i, len(crawl_results))

        return results

    async def ingest_pdf_files(self, filespath: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        if progress_callback:
            progress_callback("gr:ingest_pdf_files", 0, 1)

        return [IngestionResult(
            document_id="",
            title="",
            chunks_created=0,
            entities_extracted=0,
            relationships_created=0,
            processing_time_ms=0.0,
            errors=[]
        )]

    async def ingest_txt_files(self, filespath: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        if progress_callback:
            progress_callback("gr:ingest_txt_files", 0, 1)

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
        """Retrieve relevant documents from GraphRAG based on a search query.
        
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

    async def _ingest_single_document(
            self, 
            source: str, 
            title: str, 
            content: str,
            metadata: Optional[Dict[str, Any]] = None) -> IngestionResult:
        """
        Ingest a single document.
        
        Args:
            source
            title
            content
        
        Returns:
            Ingestion result
        """
        start_time = datetime.now()
        document_id = f"{source}_{title}_{datetime.now().timestamp()}"

        # Chunk the document
        chunks = await self.chunker_service.chunk_document(
            content=content,
            title=title,
            source=source,
            metadata=metadata
        )
        
        if not chunks:
            return IngestionResult(
                document_id=document_id,
                title=title,
                chunks_created=0,
                entities_extracted=0,
                relationships_created=0,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                errors=["No chunks created"]
            )
        
        print(f"Created {len(chunks)} chunks")
        
        # Add to knowledge graph (if enabled)
        graph_errors = []
        
        print("Building knowledge graph relationships (this may take several minutes)...")
        episodes_created = 0
        errors = []
        
        # Process chunks one by one to avoid overwhelming Graphiti
        for i, chunk in enumerate(chunks):
            try:
                # Create episode ID
                episode_id = f"{source}_{chunk.index}_{datetime.now().timestamp()}"
                
                # Prepare episode content with size limits
                episode_content = self._prepare_episode_content(
                    chunk,
                    title
                )
                
                # Add episode to graph
                await self.graph_service.add_episode(
                    episode_id=episode_id,
                    content=episode_content,
                    source=f"Document: {title} (Chunk: {chunk.index})",
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "document_title": title,
                        "document_source": source,
                        "chunk_index": chunk.index,
                        "original_length": len(chunk.content),
                        "processed_length": len(episode_content)
                    }
                )
                
                episodes_created += 1
                print(f"✓ Added episode {episode_id} to knowledge graph ({episodes_created}/{len(chunks)})")
                
                # Small delay between each episode to reduce API pressure
                if i < len(chunks) - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                error_msg = f"Failed to add chunk {chunk.index} to graph: {str(e)}"
                errors.append(error_msg)
                
                # Continue processing other chunks even if one fails
                continue
            
        return IngestionResult(
            document_id=document_id,
            title=title,
            chunks_created=len(chunks),
            entities_extracted=0,
            relationships_created=0,
            processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            errors=graph_errors
        )

    def _prepare_episode_content(
        self,
        chunk: DocumentChunk,
        title: str
    ) -> str:
        """
        Prepare episode content with minimal context to avoid token limits.
        
        Args:
            chunk: Document chunk
            title: Title of the document
            metadata: Additional metadata
        
        Returns:
            Formatted episode content (optimized for Graphiti)
        """
        # Limit chunk content to avoid Graphiti's 8192 token limit
        # Estimate ~4 chars per token, keep content under 6000 chars to leave room for processing
        max_content_length = 6000
        
        content = chunk.content
        if len(content) > max_content_length:
            # Truncate content but try to end at a sentence boundary
            truncated = content[:max_content_length]
            last_sentence_end = max(
                truncated.rfind('. '),
                truncated.rfind('! '),
                truncated.rfind('? ')
            )
            
            if last_sentence_end > max_content_length * 0.7:  # If we can keep 70% and end cleanly
                content = truncated[:last_sentence_end + 1] + " [TRUNCATED]"
            else:
                content = truncated + "... [TRUNCATED]"
            
        
        # Add minimal context (just document title for now)
        if title and len(content) < max_content_length - 100:
            episode_content = f"[Doc: {title[:50]}]\n\n{content}"
        else:
            episode_content = content
        
        return episode_content    

