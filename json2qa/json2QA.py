import json
from llm.llm import LLMClient
from langchain.prompts import PromptTemplate
import pathlib
from process.process import MarkdownProcessor
from typing import List, Dict, Optional


class QAGenerator:
    """
    A class for generating Bible Q&A pairs from processed markdown chunks.
    
    This class handles the complete pipeline from JSONL chunks to Q&A pairs
    using language models.
    """
    
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None):
        """
        Initialize the BibleQAGenerator.
        
        Args:
            model_name: The LLM model to use for Q&A generation
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.llm_client = LLMClient(model_name, api_key)
        self.processor = MarkdownProcessor()
        self.system_prompt = pathlib.Path("qa_system.md").read_text()
    
    def load_template(self, template_path: str = "qa_message.md") -> PromptTemplate:
        """
        Load a prompt template from file.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            LangChain PromptTemplate instance
        """
        try:
            template_content = pathlib.Path(template_path).read_text()
            return PromptTemplate.from_template(
                template_content,
                input_variables=["heading", "chunk_text"]
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {template_path}")
    
    def load_jsonl_file(self, jsonl_file: str) -> List[Dict[str, str]]:
        """
        Load chunks from a JSONL file.
        
        Args:
            jsonl_file: Path to the JSONL file
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        with open(jsonl_file, 'r') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    chunks.append(json.loads(line.strip()))
        return chunks
    
    def generate_qa_pairs(self, jsonl_file: str, template_path: str = "qa_template.md") -> List[str]:
        """
        Generate Q&A pairs from a JSONL file.
        
        Args:
            jsonl_file: Path to the JSONL file containing chunks
            template_path: Path to the prompt template file
            
        Returns:
            List of Q&A pair responses
        """
        # Load the JSONL file
        chunks = self.load_jsonl_file(jsonl_file)
        
        # Load the template
        prompt_template = self.load_template(template_path)
        
        # Generate Q&A pairs for each chunk
        qa_pairs = []
        
        for chunk in chunks:
            # Process the chunk with the template
            message = self.processor.process_chunk(chunk, prompt_template)
            
            # Call the LLM to generate Q&A pairs
            response = self.llm_client.call_llm(self.system_prompt, message)
            qa_pairs.append(response)
        
        return qa_pairs
    
    def generate_qa_pairs_with_config(self, jsonl_file: str, template_path: str = "qa_template.md",
                                    temperature: float = 0.7, max_tokens: Optional[int] = None) -> List[str]:
        """
        Generate Q&A pairs with custom LLM configuration.
        
        Args:
            jsonl_file: Path to the JSONL file containing chunks
            template_path: Path to the prompt template file
            temperature: Controls randomness in LLM responses
            max_tokens: Maximum tokens for each response
            
        Returns:
            List of Q&A pair responses
        """
        # Load the JSONL file
        chunks = self.load_jsonl_file(jsonl_file)
        
        # Load the template
        prompt_template = self.load_template(template_path)
        
        # Generate Q&A pairs for each chunk
        qa_pairs = []
        
        for chunk in chunks:
            # Process the chunk with the template
            message = self.processor.process_chunk(chunk, prompt_template)
            
            # Call the LLM with custom configuration
            response = self.llm_client.call_llm_with_config(
                self.system_prompt, 
                message, 
                temperature=temperature, 
                max_tokens=max_tokens
            )
            qa_pairs.append(response)
        
        return qa_pairs
    
    def save_qa_pairs(self, qa_pairs: List[str], output_file: str) -> str:
        """
        Save Q&A pairs to a JSON file.
        
        Args:
            qa_pairs: List of Q&A pair responses
            output_file: Path to the output JSON file
            
        Returns:
            Path to the created output file
        """
        with open(output_file, 'w') as file:
            json.dump(qa_pairs, file, indent=2)
        
        return output_file
    
    def process_pipeline(self, jsonl_file: str, output_file: str, 
                        template_path: str = "qa_template.md") -> str:
        """
        Complete pipeline: load chunks, generate Q&A pairs, and save results.
        
        Args:
            jsonl_file: Path to the input JSONL file
            output_file: Path to the output JSON file
            template_path: Path to the prompt template file
            
        Returns:
            Path to the created output file
        """
        # Generate Q&A pairs
        qa_pairs = self.generate_qa_pairs(jsonl_file, template_path)
        
        # Save the results
        return self.save_qa_pairs(qa_pairs, output_file)
    
    def get_processing_stats(self, jsonl_file: str) -> Dict[str, any]:
        """
        Get statistics about the processing.
        
        Args:
            jsonl_file: Path to the JSONL file
            
        Returns:
            Dictionary with processing statistics
        """
        chunks = self.load_jsonl_file(jsonl_file)
        
        total_chunks = len(chunks)
        total_text_length = sum(len(chunk.get('text', '')) for chunk in chunks)
        avg_chunk_length = total_text_length / total_chunks if total_chunks > 0 else 0
        
        return {
            "total_chunks": total_chunks,
            "total_text_length": total_text_length,
            "average_chunk_length": avg_chunk_length,
            "model_info": self.llm_client.get_model_info()
        }


# Backward compatibility functions
def generate_bible_qa_pairs(jsonl_file: str) -> List[str]:
    """Backward compatibility function."""
    generator = BibleQAGenerator()
    return generator.generate_qa_pairs(jsonl_file)


def save_qa_pairs(qa_pairs: List[str], output_file: str) -> str:
    """Backward compatibility function."""
    generator = BibleQAGenerator()
    return generator.save_qa_pairs(qa_pairs, output_file)



