from typing import List, Optional
import asyncio

from openai import RateLimitError, APIError

from helpers.providers import get_embedding_client, get_embedding_model
from service.config.typex import IConfigService

# compliant with IEmbedderService protocol
class GenericEmbedderService:
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service
        self.model = get_embedding_model()
        self.client = get_embedding_client()
        self.batch_size = self.config_service.get_embedded_batch_size()
        self.max_retries = self.config_service.get_embedded_max_retries()
        self.retry_delay = self.config_service.get_embedded_retry_delay()
        self.max_tokens = self.config_service.get_embedded_max_tokens()
        self.dimensions = self.config_service.get_embedded_dimensions()

    async def embed(
        self,
        text: str) -> List[float]:
        """Embed TEXT."""
        # Truncate text if too long
        if len(text) > self.max_tokens * 4:  # Rough token estimation
            text = text[:self.max_tokens * 4]
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                
                return response.data[0].embedding
                
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential backoff for rate limits
                delay = self.retry_delay * (2 ** attempt)
                print(f"Rate limit hit, retrying in {delay}s")
                await asyncio.sleep(delay)
                
            except APIError as e:
                print(f"OpenAI API error: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
                
            except Exception as e:
                print(f"Unexpected error generating embedding: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)

    def finalize(self) -> None:
        """Destruct the service and close resources."""
        return None
