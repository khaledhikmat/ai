from typing import List, Dict, Any, Optional

from service.config.typex import IConfigService
from .typex import DocumentChunk

# compliant with IChunkerService protocol
class SimpleChunkerService:
    """
    Simple non-semantic chunker for faster processing.
    From Cole Medin (https://github.com/coleam00/ottomator-agents)
    """
    
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service
        self.config = config_service.get_chunking_config()

    def chunk_document(
        self,
        content: str,
        title: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """
        Chunk document using simple rules.
        
        Args:
            content: Document content
            title: Document title
            source: Document source
            metadata: Additional metadata
        
        Returns:
            List of document chunks
        """
        if not content.strip():
            return []
        
        base_metadata = {
            "title": title,
            "source": source,
            "chunk_method": "simple",
            **(metadata or {})
        }
        
        # Split on paragraphs first
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        current_chunk = ""
        current_pos = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph exceeds chunk size
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(potential_chunk) <= self.config.chunk_size:
                current_chunk = potential_chunk
            else:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk,
                        chunk_index,
                        current_pos,
                        current_pos + len(current_chunk),
                        base_metadata.copy()
                    ))
                    
                    # Move position, but ensure overlap is respected
                    overlap_start = max(0, len(current_chunk) - self.config.chunk_overlap)
                    current_pos += overlap_start
                    chunk_index += 1
                
                # Start new chunk with current paragraph
                current_chunk = paragraph
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk,
                chunk_index,
                current_pos,
                current_pos + len(current_chunk),
                base_metadata.copy()
            ))
        
        # Update total chunks in metadata
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    def _create_chunk(
        self,
        content: str,
        index: int,
        start_pos: int,
        end_pos: int,
        metadata: Dict[str, Any]
    ) -> DocumentChunk:
        """Create a DocumentChunk object."""
        return DocumentChunk(
            content=content.strip(),
            index=index,
            start_char=start_pos,
            end_char=end_pos,
            metadata=metadata
        )

