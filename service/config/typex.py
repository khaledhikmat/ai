from typing import Protocol
from dataclasses import dataclass

@dataclass
class ChunkingConfig:
    """Configuration for chunking."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunk_size: int = 2000
    min_chunk_size: int = 100
    use_semantic_splitting: bool = True
    preserve_structure: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")
        if self.min_chunk_size <= 0:
            raise ValueError("Minimum chunk size must be positive")

# config services must implement this protocol
class IConfigService(Protocol): 
    # repo service
    def get_repo_type(self) -> str:
        """Get Repo type."""
        pass

    def get_repo_urls(self) -> str:
        """Get Repo urls."""
        pass

    def get_github_token(self) -> str:
        """Get Github token."""
        pass

    def get_github_slug(self) -> str:
        """Get Github slug."""
        pass

    def get_gitlab_token(self) -> str:
        """Get Gitlab roken."""
        pass

    def get_gitlab_slug(self) -> str:
        """Get Gitlab slug."""
        pass

    def get_gitlab_base_url(self) -> str:
        """Get Gitlab base url."""
        pass

    # lightrag service
    def get_lightrag_work_dir(self) -> str:
        """Get RAG work dir."""
        pass

    def get_lightrag_llm_type(self) -> str:
        """Get LLM type."""
        pass

    def get_lightrag_llm_model(self) -> str:
        """Get LLM model."""
        pass

    # chunking service
    def get_chunking_config(self) -> ChunkingConfig:
        """Get chunking configuration."""
        pass

    # neo4j service
    def get_neo4j_uri(self) -> str:
        """Get Neo4j URI."""
        pass

    def get_neo4j_user(self) -> str:
        """Get Neo4j user."""
        pass

    def get_neo4j_password(self) -> str:
        """Get Neo4j password."""
        pass

    # llm service
    def get_llm_provider(self) -> str:
        """Get LLM provider."""
        pass

    def get_llm_choice(self) -> str:
        """Get LLM choice."""
        pass

    def get_llm_base_url(self) -> str:
        """Get LLM base URL."""
        pass

    def get_llm_api_key(self) -> str:
        """Get LLM API KEY."""
        pass

    # embedded service
    def get_embedded_base_url(self) -> str:
        """Get base URL for embedding."""
        pass

    def get_embedded_api_key(self) -> str:
        """Get api KEY for embedding."""
        pass

    def get_embedded_model(self) -> str:
        """Get model for embedding."""
        pass

    def get_embedded_batch_size(self) -> int:
        """Get batch size for embedding."""
        pass

    def get_embedded_max_retries(self) -> int:
        """Get max retries for embedding."""
        pass

    def get_embedded_retry_delay(self) -> float:
        """Get retry delay for embedding."""
        pass

    def get_embedded_max_tokens(self) -> int:
        """Get max tokens for embedding."""
        pass

    def get_embedded_dimensions(self) -> int:
        """Get dimensions for embedding."""
        pass

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        pass

