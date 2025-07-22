from langchain_openai import ChatOpenAI
import os 
from langchain.schema import SystemMessage, HumanMessage
from typing import Optional, Dict, Any


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
        
        self.llm = self._create_llm()
    
    def _create_llm(self) -> ChatOpenAI:
        """
        Create and return a ChatOpenAI instance.
        
        Returns:
            Configured ChatOpenAI instance
        """
        return ChatOpenAI(model=self.model_name, api_key=self.api_key)
    
    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM with system and user prompts.
        
        Args:
            system_prompt: The system prompt to set context
            user_prompt: The user prompt/question
            
        Returns:
            The LLM response content
        """
        # Define messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Call the LLM
        response = self.llm(messages)
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
        responses = []
        for prompt in prompts:
            response = self.call_llm(system_prompt, prompt)
            responses.append(response)
        return responses

# Global instance for backward compatibility
qa_llm = LLMClient("gpt-4o", os.getenv("OPENAI_API_KEY"))


# Backward compatibility functions
def create_llm(model_name: str, api_key: str) -> ChatOpenAI:
    """Backward compatibility function."""
    client = LLMClient(model_name, api_key)
    return client.llm


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Backward compatibility function."""
    return qa_llm.call_llm(system_prompt, user_prompt)