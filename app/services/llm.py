from openai import OpenAI
from typing import List, Dict
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service to generate answers using OpenAI GPT."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.chat_model
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict],
        max_tokens: int = 1000
    ) -> str:
        """
        Generate an answer based on the question and retrieved context.
        
        Args:
            question: The user's question
            context_chunks: List of relevant context chunks
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated answer
        """
        # Build context from chunks
        context = self._build_context(context_chunks)
        
        # Create prompt
        system_prompt = """You are a helpful Q&A assistant. Your role is to answer questions based ONLY on the provided context from crawled website content.

Rules:
1. Only use information from the provided context to answer questions
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Be concise and accurate
4. Cite specific parts of the context when relevant
5. Do not make up or assume information not present in the context
6. If the question cannot be answered from the context, politely explain this limitation"""

        user_prompt = f"""Context from website:
{context}

Question: {question}

Please provide an answer based only on the context above. If the context doesn't contain relevant information, let me know."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more focused answers
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from chunks."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            doc = chunk.get('document', '')
            metadata = chunk.get('metadata', {})
            url = metadata.get('url', 'Unknown')
            title = metadata.get('title', 'Untitled')
            
            context_parts.append(f"[Source {i}] {title} ({url}):\n{doc}\n")
        
        return "\n".join(context_parts)
