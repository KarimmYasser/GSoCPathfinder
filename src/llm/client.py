"""Unified LLM and Embedding client using LangChain."""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config.settings import get_settings

class LLMClient:
    """Wrapper for LLM and Embedding models."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Initialize Chat Model
        self.chat_model = ChatOpenAI(
            base_url=self.settings.llm_base_url,
            api_key=self.settings.llm_api_key,
            model=self.settings.llm_chat_model,
            temperature=0.1
        )
        
        # Initialize Embedding Model
        self.embed_model = OpenAIEmbeddings(
            base_url=self.settings.embed_base_url,
            api_key=self.settings.embed_api_key,
            model=self.settings.embed_model,
            check_embedding_ctx_length=False
        )
        
    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a batch of texts."""
        if not texts:
            return []
        # LangChain supports async embeddings natively
        return await self.embed_model.aembed_documents(texts)
        
    async def get_single_embedding(self, text: str) -> list[float]:
        """Get embedding for a single text."""
        return await self.embed_model.aembed_query(text)

# Singleton instance
_client: LLMClient | None = None

def get_llm_client() -> LLMClient:
    """Get the global LLM client."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
