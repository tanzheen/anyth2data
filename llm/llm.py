from langchain_openai import ChatOpenAI
import os
import logging
from langchain.schema import SystemMessage, HumanMessage
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)
from utils.config import env

class LLMClient:
    """
    A client for interacting with language models.
    
    This class provides a clean interface for creating and using LLM instances
    with proper configuration and error handling.
    """
    
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            model_name: The name of the model to use
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        logger.info(f"Initializing LLMClient with model: {model_name}")
        self.llm = self._create_llm()
        logger.debug("LLMClient initialized successfully")
    
    def _create_llm(self) -> ChatOpenAI:
        """
        Create and return a ChatOpenAI instance.
        
        Returns:
            Configured ChatOpenAI instance
        """
        return ChatOpenAI(model=self.model_name, api_key=self.api_key, base_url=env.LLM_BASE_URL)
    
    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM with system and user prompts.
        
        Args:
            system_prompt: The system prompt to set context
            user_prompt: The user prompt/question
            
        Returns:
            The LLM response content
        """
        logger.debug(f"Calling LLM with system prompt ({len(system_prompt)} chars) and user prompt ({len(user_prompt)} chars)")
        
        # Define messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Call the LLM
        response = self.llm(messages)
        logger.debug(f"LLM response received ({len(response.content)} chars)")
        return response.content
    
    def call_llm_with_config(self, system_prompt: str, user_prompt: str, 
                            temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Call the LLM with additional configuration options.
        
        Args:
            system_prompt: The system prompt to set context
            user_prompt: The user prompt/question
            temperature: Controls randomness (0.0 = deterministic, 1.0 = very random)
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            The LLM response content
        """
        logger.debug(f"Calling LLM with config: temperature={temperature}, max_tokens={max_tokens}")
        
        # Create a temporary LLM instance with custom config
        config = {"temperature": temperature}
        if max_tokens:
            config["max_tokens"] = max_tokens
            
        temp_llm = ChatOpenAI(
            model=self.model_name, 
            api_key=self.api_key,
            **config
        )
        
        # Define messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Call the LLM
        response = temp_llm(messages)
        logger.debug(f"LLM response received with config ({len(response.content)} chars)")
        return response.content
    
    def batch_call_llm(self, prompts: list, system_prompt: str) -> list:
        """
        Process multiple prompts in batch.
        
        Args:
            prompts: List of user prompts
            system_prompt: The system prompt to use for all calls
            
        Returns:
            List of LLM responses
        """
        logger.info(f"Processing batch of {len(prompts)} prompts")
        responses = []
        for i, prompt in enumerate(prompts):
            logger.debug(f"Processing prompt {i+1}/{len(prompts)}")
            response = self.call_llm(system_prompt, prompt)
            responses.append(response)
        logger.info(f"Batch processing completed, {len(responses)} responses received")
        return responses



