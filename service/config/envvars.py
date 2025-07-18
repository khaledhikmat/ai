import os

from .typex import ChunkingConfig

# compliant with IConfigService protocol
class EnvVarsConfigService:
    def __init__(self):
        return None

    # repo service 
    def get_repo_type(self) -> str:
        """Get Repo type."""
        return os.environ.get("REPO_TYPE", "github")

    def get_repo_urls(self) -> str:
        """Get Repo urls."""
        return os.environ.get("REPO_URLS", "")

    def get_github_token(self) -> str:
        """Get Github token."""
        return os.environ.get("GITHUB_TOKEN", "")

    def get_github_slug(self) -> str:
        """Get Github slug."""
        return os.environ.get("GITHUB_SLUG", "")

    def get_gitlab_token(self) -> str:
        """Get Gitlab roken."""
        return os.environ.get("GITLAB_TOKEN", "")

    def get_gitlab_slug(self) -> str:
        """Get Gitlab slug."""
        return os.environ.get("GITLAB_SLUG", "")

    def get_gitlab_base_url(self) -> str:
        """Get Gitlab base url."""
        return os.environ.get("GITLAB_BASE_URL", "")

    # lightrag service
    def get_lightrag_work_dir(self) -> str:
        """Get RAG work dir."""
        return os.environ.get("LIGHTRAG_WORK_DIR", "")

    def get_lightrag_llm_type(self) -> str:
        """Get llm type."""
        return os.environ.get("LIGHTRAG_LLM_TYPE", "")

    def get_lightrag_llm_model(self) -> str:
        """Get llm model."""
        return os.environ.get("LIGHTRAG_LLM_MODEL", "")

    # neo4j service
    def get_neo4j_uri(self) -> str:
        """Get Neo4j URI."""
        return os.environ.get("NEO4J_URI", "")

    def get_neo4j_user(self) -> str:
        """Get Neo4j user."""
        return os.environ.get("NEO4J_USER", "")

    def get_neo4j_password(self) -> str:
        """Get Neo4j password."""
        return os.environ.get("NEO4J_PASSWORD", "")

    # chunking service
    def get_chunking_config(self) -> ChunkingConfig:
        """Get chunking configuration."""
        return ChunkingConfig(
            chunk_size=int(os.environ.get("CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.environ.get("CHUNK_OVERLAP", 200)),
            max_chunk_size=int(os.environ.get("MAX_CHUNK_SIZE", 2000)),
            min_chunk_size=int(os.environ.get("MIN_CHUNK_SIZE", 100)),
            use_semantic_splitting=os.environ.get("USE_SEMANTIC_SPLITTING", "true").lower() == "true",
            preserve_structure=os.environ.get("PRESERVE_STRUCTURE", "true").lower() == "true"
        )

    # llm service
    def get_llm_provider(self) -> str:
        """Get LLM provider."""
        return os.environ.get("LLM_PROVIDER", "openai")

    def get_llm_choice(self) -> str:
        """Get LLM choice."""
        return os.environ.get("LLM_CHOICE", "gpt-4.1-mini") 

    def get_llm_base_url(self) -> str:
        """Get LLM base URL."""
        return os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")

    def get_llm_api_key(self) -> str:
        """Get LLM API KEY."""
        return os.environ.get("LLM_API_KEY", "")

    def get_llm_choice(self) -> str:
        """Get LLM choice."""
        return os.environ.get("LLM_CHOICE", "gpt-4.1-mini")

    # embedder service
    def get_embedded_base_url(self) -> str:
        return os.environ.get("EMBEDDING_BASE_URL", "https://api.openai.com/v1")

    def get_embedded_api_key(self) -> str:
        """Get api KEY for embedding."""
        return os.environ.get("EMBEDDING_API_KEY", "")

    def get_embedded_model(self) -> str:
        """Get model for embedding."""
        #print("********* get_embedded_model")
        #md = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
        #print(f"********* get_embedded_model2 {md}")
        return "text-embedding-3-small"

    def get_embedded_batch_size(self) -> int:
        """Get batch size for embedding."""
        return int(os.environ.get("EMBEDDED_BATCH_SIZE", 100))

    def get_embedded_max_retries(self) -> int:
        """Get max retries for embedding."""
        return int(os.environ.get("EMBEDDED_MAX_RETRIES", 3))

    def get_embedded_retry_delay(self) -> float:
        """Get retry delay for embedding."""
        return float(os.environ.get("EMBEDDED_RETRY_DELAY", 1.0))

    def get_embedded_max_tokens(self) -> int:
        """Get max tokens for embedding."""
        return int(os.environ.get("EMBEDDED_MAX_TOKENS", 8191))

    def get_embedded_dimensions(self) -> int:
        """Get dimensions for embedding."""
        return int(os.environ.get("EMBEDDED_DIMENSIONS", 1024))

    def finalize(self) -> None:
        return None

