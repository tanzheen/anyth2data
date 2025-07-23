import re
import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class MarkdownProcessor:
    """
    A class for processing markdown files into chunks for QA generation.
    
    This class handles the complete pipeline from markdown files to JSONL chunks
    that can be used for generating question-answer pairs.
    """
    
    def __init__(self, min_words: int = 150, join_token: str = " / "):
        """
        Initialize the MarkdownProcessor.
        
        Args:
            min_words: Minimum number of words required for a chunk
            join_token: Token used to join heading paths in chunk IDs
        """
        self.min_words = min_words
        self.join_token = join_token
        self.HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')
        logger.debug(f"MarkdownProcessor initialized with min_words={min_words}, join_token='{join_token}'")
    
    def remove_img_links(self, text: str) -> str:
        """
        Remove image links from markdown text.
        
        Args:
            text: The markdown text to clean
            
        Returns:
            Cleaned text with image links removed
        """
        logger.debug(f"Removing image links from text of length {len(text)}")
        # Remove image links
        text = re.sub(r'!\[\]\([^)]+\)', '', text)
        # Normalize excess newlines
        text = re.sub(r'\n{2,}', '\n\n', text.strip())
        logger.debug(f"Text cleaned, new length: {len(text)}")
        return text
    
    def split_markdown_by_any_heading(self, title: str, text: str) -> List[Dict[str, str]]:
        """
        Break a long markdown string into chunks.
        
        Chunks start at *any* heading level (# … ######)
        A chunk is emitted once it reaches ≥ `min_words`
        Each chunk_id is the concatenation of the current heading path
        e.g.  "# Text notes / ### 1. Opening Greeting, 1.1–2 / #### a) The Apostle Paul"
        
        Args:
            text: The markdown text to split
            
        Returns:
            List of dictionaries with "chunk_id" and "text" keys
        """
        logger.info(f"Splitting markdown for title: {title}, text length: {len(text)}")
        chunks = []
        heading_path = [""] * 6  # slot for each possible level
        buffer_lines = []  # lines for the current chunk

        def current_chunk_id() -> str:
            """Return non‑empty headings joined."""
            titles = [t for t in heading_path if t]
            return self.join_token.join(titles) if titles else "ROOT"

        def flush_buffer():
            """Commit buffer to `chunks` if it has content."""
            if buffer_lines:
                chunk_id = title + " / " + current_chunk_id()
                chunk_text = "\n".join(buffer_lines).strip()
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text
                })
                logger.debug(f"Created chunk: {chunk_id} ({len(chunk_text)} chars)")
                buffer_lines.clear()

        for line in text.splitlines():
            # Check if this line is a heading
            m = self.HEADING_RE.match(line)
            if m:
                # If we already have ≥ min_words, flush before starting a new heading
                if len(" ".join(buffer_lines).split()) >= self.min_words:
                    flush_buffer()

                level = len(m.group(1))  # number of '#'
                title = m.group(2).strip()

                # Update heading path: set current level, clear deeper levels
                heading_path[level - 1] = title
                for i in range(level, 6):
                    heading_path[i] = ""

                buffer_lines.append(line)  # keep the heading itself
            else:
                buffer_lines.append(line)

            # If after adding the line we're over the limit *and* the next line
            # will be a heading (look‑ahead) we postpone flushing to that heading
            # logic so headings stay with their content.

        # Flush any remaining text (even if < min_words)
        flush_buffer()
        logger.info(f"Split markdown into {len(chunks)} chunks")
        return chunks
    
    def save_chunks_to_jsonl(self, chunks: List[Dict[str, str]], output_file: str) -> None:
        """
        Save chunks to a JSONL file.
        
        Args:
            chunks: List of chunk dictionaries
            output_file: Path to the output JSONL file
        """
        logger.info(f"Saving {len(chunks)} chunks to {output_file}")
        with open(output_file, 'w') as file:
            for chunk in chunks:
                json.dump(chunk, file)
                file.write('\n')
        logger.debug(f"Successfully saved chunks to {output_file}")
    
    def process_md_file(self, md_file: str, output_dir: str) -> str:
        """
        Process a markdown file into chunks and save to JSONL.
        
        Args:
            md_file: Path to the input markdown file
            output_dir: Directory to save the output JSONL file
            
        Returns:
            Path to the created JSONL file
        """
        logger.info(f"Processing markdown file: {md_file}")
        
        # Read the md file
        title = md_file.split("/")[-1].split(".")[0]
        logger.debug(f"Extracted title: {title}")
        
        with open(md_file, 'r') as file:
            md_content = file.read()
        logger.debug(f"Read {len(md_content)} characters from file")
        
        # Clean the md file
        md_content = self.remove_img_links(md_content)

        # Split the md file into chunks
        chunks = self.split_markdown_by_any_heading(title, md_content)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_dir}")
        
        # Save the chunks to a jsonl file
        output_file = os.path.join(output_dir, os.path.basename(md_file) + ".jsonl")
        self.save_chunks_to_jsonl(chunks, output_file)
        
        logger.info(f"Successfully processed {md_file} -> {output_file}")
        return output_file
    
    def process_chunk(self, chunk: Dict[str, str], prompt_template) -> str:
        """
        Process a single chunk with a prompt template.
        
        Args:
            chunk: Dictionary with "chunk_id" and "text" keys
            prompt_template: LangChain prompt template
            
        Returns:
            Formatted prompt string
        """
        chunk_id = chunk["chunk_id"]
        chunk_text = chunk["text"]
        
        logger.debug(f"Processing chunk: {chunk_id} ({len(chunk_text)} chars)")
        
        # Format the prompt template using LangChain's format method
        filled_prompt = prompt_template.format(
            heading=chunk_id, 
            chunk_text=chunk_text
        )
        
        logger.debug(f"Formatted prompt length: {len(filled_prompt)}")
        return filled_prompt

# # test the process
# if __name__ == "__main__":
#     processor = MarkdownProcessor()
#     processor.process_md_file("/Users/tannicholas/anyth2data/conversion_results/2 peter/2 peter.md", "qa_results")