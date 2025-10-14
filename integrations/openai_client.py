"""
OpenAI client integration using LangChain
"""
import time
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import Config


class OpenAIClient:
    """OpenAI client wrapper using LangChain"""
    
    def __init__(self):
        """Initialize the OpenAI client"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your environment.")
        
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0.3,  # Lower temperature for more consistent outputs
            max_tokens=2000,
            request_timeout=Config.REQUEST_TIMEOUT
        )
    
    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        max_retries: int = Config.MAX_RETRIES
    ) -> str:
        """
        Generate response using OpenAI with retry logic
        
        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            max_retries: Maximum number of retries
            
        Returns:
            str: The generated response
            
        Raises:
            Exception: If all retries fail
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(messages)
                return response.content.strip()
            
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    break
        
        # If we get here, all retries failed
        raise Exception(f"OpenAI API call failed after {max_retries} attempts. Last error: {last_exception}")
    
    def test_connection(self) -> bool:
        """
        Test the OpenAI connection
        
        Returns:
            bool: True if connection is successful
        """
        try:
            test_response = self.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say 'Connection successful' if you can read this.",
                max_retries=1
            )
            return "successful" in test_response.lower()
        except Exception:
            return False

