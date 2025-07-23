import click
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from pipelines.pipelines import pdf2qa, md2qa
from anyth2md.anyth2md import DocumentConverter
from markdown_process.process import MarkdownProcessor
from json2qa.json2QA import QAGenerator
from utils.config import env

# Configure logging
def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('anyth2data.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', default='anyth2data.log', help='Log file path')
def cli(verbose: bool, log_file: str):
    """AnyTh2Data - Document processing and Q&A generation pipeline."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Update file handler
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logging.getLogger().removeHandler(handler)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    logger.info("Starting AnyTh2Data CLI")


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='qa_results', help='Output directory for Q&A files')
@click.option('--pipeline', '-p', type=click.Choice(['pdf2qa', 'md2qa', 'auto']), 
              default='auto', help='Pipeline to use (auto detects based on file extension)')
@click.option('--template', '-t', default='prompts/qa_message.md', help='Prompt template path')
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--model', default='gpt-4o', help='LLM model to use')
@click.option('--temperature', default=0.7, type=float, help='LLM temperature')
@click.option('--max-tokens', type=int, help='Maximum tokens for LLM responses')
def convert(input_path: str, output_dir: str, pipeline: str, template: str, 
           api_key: str, model: str, temperature: float, max_tokens: Optional[int]):
    """Convert a single file to Q&A format."""
    logger.info(f"Starting conversion of: {input_path}")
    logger.info(f"Pipeline: {pipeline}, Output dir: {output_dir}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine pipeline if auto
    if pipeline == 'auto':
        file_ext = Path(input_path).suffix.lower()
        if file_ext == '.pdf':
            pipeline = 'pdf2qa'
        elif file_ext == '.md':
            pipeline = 'md2qa'
        else:
            logger.error(f"Unsupported file extension: {file_ext}")
            return
    
    try:
        if pipeline == 'pdf2qa':
            result = pdf2qa(input_path)
            logger.info(f"PDF to Q&A conversion completed: {result}")
        elif pipeline == 'md2qa':
            result = md2qa(input_path)
            logger.info(f"Markdown to Q&A conversion completed: {result}")
        
        click.echo(f"✅ Conversion completed successfully!")
        click.echo(f"📁 Output: {output_dir}")
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        click.echo(f"❌ Conversion failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--output-dir', '-o', default='qa_results', help='Output directory for Q&A files')
@click.option('--pipeline', '-p', type=click.Choice(['pdf2qa', 'md2qa', 'auto']), 
              default='auto', help='Pipeline to use')
@click.option('--file-pattern', default='*', help='File pattern to match (e.g., "*.pdf")')
@click.option('--template', '-t', default='prompts/qa_message.md', help='Prompt template path')
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--model', default='gpt-4o', help='LLM model to use')
@click.option('--temperature', default=0.7, type=float, help='LLM temperature')
@click.option('--max-tokens', type=int, help='Maximum tokens for LLM responses')
@click.option('--parallel', is_flag=True, help='Process files in parallel')
def batch_convert(input_dir: str, output_dir: str, pipeline: str, file_pattern: str,
                 template: str, api_key: str, model: str, temperature: float, 
                 max_tokens: Optional[int], parallel: bool):
    """Convert all files in a directory to Q&A format."""
    logger.info(f"Starting batch conversion of directory: {input_dir}")
    logger.info(f"Pipeline: {pipeline}, Pattern: {file_pattern}, Output dir: {output_dir}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find matching files
    input_path = Path(input_dir)
    if pipeline == 'auto':
        pdf_files = list(input_path.glob(f"{file_pattern}.pdf"))
        md_files = list(input_path.glob(f"{file_pattern}.md"))
        files = pdf_files + md_files
    elif pipeline == 'pdf2qa':
        files = list(input_path.glob(f"{file_pattern}.pdf"))
    elif pipeline == 'md2qa':
        files = list(input_path.glob(f"{file_pattern}.md"))
    
    if not files:
        logger.warning(f"No matching files found in {input_dir}")
        click.echo(f"⚠️  No matching files found in {input_dir}")
        return
    
    logger.info(f"Found {len(files)} files to process")
    click.echo(f"📁 Found {len(files)} files to process")
    
    successful = 0
    failed = 0
    
    for file_path in files:
        try:
            logger.info(f"Processing: {file_path}")
            click.echo(f"🔄 Processing: {file_path.name}")
            
            if pipeline == 'pdf2qa' or (pipeline == 'auto' and file_path.suffix == '.pdf'):
                result = pdf2qa(str(file_path))
            elif pipeline == 'md2qa' or (pipeline == 'auto' and file_path.suffix == '.md'):
                result = md2qa(str(file_path))
            
            successful += 1
            logger.info(f"Successfully processed: {file_path}")
            click.echo(f"✅ Completed: {file_path.name}")
            
        except Exception as e:
            failed += 1
            logger.error(f"Failed to process {file_path}: {str(e)}")
            click.echo(f"❌ Failed: {file_path.name} - {str(e)}")
    
    logger.info(f"Batch conversion completed. Successful: {successful}, Failed: {failed}")
    click.echo(f"\n📊 Batch conversion completed!")
    click.echo(f"✅ Successful: {successful}")
    click.echo(f"❌ Failed: {failed}")


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='chunks', help='Output directory for chunks')
def extract_chunks(input_path: str, output_dir: str):
    """Extract chunks from a markdown file without generating Q&A."""
    logger.info(f"Extracting chunks from: {input_path}")
    
    try:
        processor = MarkdownProcessor()
        chunks_file = processor.process_md_file(input_path, output_dir)
        
        logger.info(f"Chunks extracted successfully: {chunks_file}")
        click.echo(f"✅ Chunks extracted successfully!")
        click.echo(f"📁 Output: {chunks_file}")
        
    except Exception as e:
        logger.error(f"Chunk extraction failed: {str(e)}")
        click.echo(f"❌ Chunk extraction failed: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('chunks_file', type=click.Path(exists=True))
@click.option('--output-file', '-o', help='Output file for Q&A pairs')
@click.option('--template', '-t', default='prompts/qa_message.md', help='Prompt template path')
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--model', default='gpt-4o', help='LLM model to use')
@click.option('--temperature', default=0.7, type=float, help='LLM temperature')
@click.option('--max-tokens', type=int, help='Maximum tokens for LLM responses')
def generate_qa(chunks_file: str, output_file: str, template: str, api_key: str, 
                model: str, temperature: float, max_tokens: Optional[int]):
    """Generate Q&A pairs from existing chunks file."""
    logger.info(f"Generating Q&A from chunks: {chunks_file}")
    
    try:
        qa_generator = QAGenerator(model_name=model, api_key=api_key)
        
        if max_tokens:
            qa_pairs = qa_generator.generate_qa_pairs_with_config(
                chunks_file, template, temperature, max_tokens
            )
        else:
            qa_pairs = qa_generator.generate_qa_pairs(chunks_file, template)
        
        if not output_file:
            output_file = chunks_file.replace('.jsonl', '_qa.json')
        
        result = qa_generator.save_qa_pairs(qa_pairs, output_file)
        
        logger.info(f"Q&A generation completed: {result}")
        click.echo(f"✅ Q&A generation completed!")
        click.echo(f"📁 Output: {result}")
        
    except Exception as e:
        logger.error(f"Q&A generation failed: {str(e)}")
        click.echo(f"❌ Q&A generation failed: {str(e)}")
        sys.exit(1)

@cli.command()
def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    try:
        converter = DocumentConverter()
        deps = converter.check_dependencies()
        
        click.echo("🔍 Dependency Check Results:")
        for dep, available in deps.items():
            status = "✅" if available else "❌"
            click.echo(f"  {status} {dep}")
        
        if all(deps.values()):
            click.echo("\n✅ All dependencies are available!")
        else:
            click.echo("\n⚠️  Some dependencies are missing. Please install them.")
            
    except Exception as e:
        logger.error(f"Dependency check failed: {str(e)}")
        click.echo(f"❌ Dependency check failed: {str(e)}")

@cli.command()
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
def test_llm(api_key: str):
    """Test LLM connectivity and configuration."""
    logger.info("Testing LLM connectivity...")
    
    try:
        from llm.llm import LLMClient
        client = LLMClient(api_key=api_key)
        info = client.get_model_info()
        
        click.echo("🤖 LLM Test Results:")
        click.echo(f"  Model: {info.get('model_name', 'Unknown')}")
        click.echo(f"  Available: ✅")
        
        # Test a simple call
        response = client.call_llm(
            "You are a helpful assistant.",
            "Say 'Hello, world!'"
        )
        click.echo(f"  Test response: {response[:50]}...")
        
        click.echo("\n✅ LLM is working correctly!")
        
    except Exception as e:
        logger.error(f"LLM test failed: {str(e)}")
        click.echo(f"❌ LLM test failed: {str(e)}")

if __name__ == '__main__':
    cli()
