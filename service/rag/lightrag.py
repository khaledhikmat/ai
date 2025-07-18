import os
from typing import List, Callable, Optional
from datetime import datetime

from lightrag import LightRAG, QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status

import numpy as np
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer

from lightrag import LightRAG
from lightrag.llm.openai import openai_complete, gpt_4o_mini_complete, openai_embed
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc

from .typex import IngestionResult
from service.config.typex import IConfigService
from service.crawl.typex import ICrawlService

# dictionary to map llm types to a callable function that returns a LightRAG instance
_LLM_LIGHTRAG = dict[str, Callable[..., LightRAG]]

# compliant with IRAGService protocol
class LightRAGService:
    def __init__(self, config_service: IConfigService, crawl_service: ICrawlService):
        self.config_service = config_service
        self.crawl_service = crawl_service
        self._llm_lightrag_istances: _LLM_LIGHTRAG = {
            "openai": self._get_openai_lightrag_instance,
            "gemini": self._get_gemini_lightrag_instance,
            "ollama": self._get_ollama_lightrag_instance
        }
        self.rag = None

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        return None

    async def ingest_md_urls(self, urls: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        await self._initialize()

        # Check if get_lightrag_working_dir() exists, delete and recreate it
        if os.path.exists(self.config_service.get_lightrag_work_dir()):
            import shutil
            shutil.rmtree(self.config_service.get_lightrag_work_dir())
        os.mkdir(self.config_service.get_lightrag_work_dir())
        
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

            start_time = datetime.now()
            await self.rag.ainsert(md)

            if progress_callback:
                progress_callback("lr:ingest_md_urls", i, len(crawl_results))

            results.append(IngestionResult(
                document_id=url,
                title=url,
                chunks_created=1,  # Assuming one chunk per document for simplicity
                entities_extracted=0,
                relationships_created=0,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                errors=[]
            ))    

        return results

    async def ingest_pdf_files(self, filespath: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]:
        await self._initialize()
        if progress_callback:
            progress_callback("lr:ingest_pdf_files", 0, 1)

        # TBA
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
        await self._initialize()
        if progress_callback:
            progress_callback("lr:ingest_txt_files", 0, 1)

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
        """Retrieve relevant documents from LightRAG based on a search query.
        
        Args:
            context: The run context containing dependencies.
            search_query: The search query to find relevant documents.
            
        Returns:
            Formatted context information from the retrieved documents.
        """
        await self._initialize()

        # Check if get_lightrag_working_dir() does not exists, throw an error
        if not os.path.exists(self.config_service.get_lightrag_work_dir()):
            raise ValueError(f"RAG work dir: {self.config_service.get_lightrag_work_dir()} does not exist.")
        
        return await self.rag.aquery(
            query, param=QueryParam(mode="mix")
        )

    ### PRIVATE FUNCTIONS ###
    async def _initialize(self) -> None:
        # Lazy-load rag
        if self.rag is not None:
            print("LightRAG instance already initialized.")
            return

        self.rag = self._get_lightrag_instance()
        await self.rag.initialize_storages()
        await initialize_pipeline_status()

    def _get_lightrag_instance(self) -> LightRAG:
        """Get the function based on the LLM type."""
        if self.config_service.get_lightrag_llm_type() not in self._llm_lightrag_istances:
            raise ValueError(f"Unsupported LLM type: {self.config_service.get_lightrag_llm_type()}")

        return self._llm_lightrag_istances[self.config_service.get_lightrag_llm_type()]()

    # from source code: lightrag -> examples -> lightrag_openai_demo.py
    def _get_openai_lightrag_instance(self) -> LightRAG:
        """Get an instance of LightRAG."""
        return LightRAG(
            working_dir=self.config_service.get_lightrag_work_dir(),
            embedding_func=openai_embed,
            llm_model_func=openai_complete, # gpt_4o_mini_complete
            llm_model_name=os.getenv("LLM_MODEL"),
        )

    # from source code: lightrag -> examples -> lightrag_ollama_demo.py
    def _get_ollama_lightrag_instance(self) -> LightRAG:
        """Get an instance of LightRAG."""
        return LightRAG(
            working_dir=self.config_service.get_lightrag_work_dir(),
            llm_model_func=ollama_model_complete,
            llm_model_name=os.getenv("LLM_MODEL", "qwen2.5-coder:7b"),
            llm_model_max_token_size=8192,
            llm_model_kwargs={
                "host": os.getenv("LLM_BINDING_HOST", "http://localhost:11434"),
                "options": {"num_ctx": 8192},
                "timeout": int(os.getenv("TIMEOUT", "300")),
            },
            embedding_func=EmbeddingFunc(
                embedding_dim=int(os.getenv("EMBEDDING_DIM", "1024")),
                max_token_size=int(os.getenv("MAX_EMBED_TOKENS", "8192")),
                func=lambda texts: ollama_embed(
                    texts,
                    embed_model=os.getenv("EMBEDDING_MODEL", "bge-m3:latest"),
                    host=os.getenv("EMBEDDING_BINDING_HOST", "http://localhost:11434"),
                ),
            ),
        )

    # from source code: lightrag -> examples -> lightrag_gemini_demo.py
    async def _gemini_model_func(self,
        prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
    ) -> str:
        # 1. Initialize the GenAI Client with your Gemini API Key
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # 2. Combine prompts: system prompt, history, and user prompt
        if history_messages is None:
            history_messages = []

        combined_prompt = ""
        if system_prompt:
            combined_prompt += f"{system_prompt}\n"

        for msg in history_messages:
            # Each msg is expected to be a dict: {"role": "...", "content": "..."}
            combined_prompt += f"{msg['role']}: {msg['content']}\n"

        # Finally, add the new user prompt
        combined_prompt += f"user: {prompt}"

        # 3. Call the Gemini model
        response = client.models.generate_content(
            model=os.getenv("LLM_MODEL", "gemini-1.5-flash"),
            contents=[combined_prompt],
            config=types.GenerateContentConfig(max_output_tokens=500, temperature=0.1),
        )

        # 4. Return the response text
        return response.text


    async def _gemini_embedding_func(self, texts: list[str]) -> np.ndarray:
        model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings

    # from source code: lightrag -> examples -> lightrag_gemini_demo.py
    def _get_gemini_lightrag_instance(self) -> LightRAG:
        """Get an instance of LightRAG."""
        return  LightRAG(
            working_dir=self.config_service.get_lightrag_work_dir(),
            llm_model_func=self._gemini_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=384,
                max_token_size=8192,
                func=self._gemini_embedding_func,
            ),
        )



