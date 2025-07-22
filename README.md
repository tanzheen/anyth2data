# AnyTh2Data: Document to Q&A Pipeline

A comprehensive pipeline for converting documents (PDF/EPUB) to markdown and generating high-quality question-answer pairs using AI language models.

## 🚀 Features

- **Document Conversion**: Convert PDF and EPUB files to markdown format
- **Smart Chunking**: Intelligent markdown splitting based on headings with configurable word limits
- **AI-Powered Q&A Generation**: Generate high-quality question-answer pairs using OpenAI models
- **Class-Based Architecture**: Well-organized, maintainable code with proper separation of concerns
- **Comprehensive Testing**: Full test suite with support for testing specific files
- **Flexible Configuration**: Customizable parameters for chunking, LLM settings, and processing options

## 📁 Project Structure

```
anyth2data/
├── anyth2md/           # Document conversion (PDF/EPUB → Markdown)
│   └── anyth2md.py     # DocumentConverter class
├── utils/              # Core processing utilities
│   ├── process.py      # MarkdownProcessor class
│   └── config.py       # Configuration management
├── llm/                # Language model integration
│   └── llm.py         # LLMClient class
├── json2qa/            # Q&A generation
│   └── json2bibleQA.py # QAGenerator class
├── prompts/            # AI prompt templates
│   ├── qa_system.md   # System prompt for Q&A generation
│   └── qa_message.md  # Message template for Q&A pairs
├── pipelines/          # End-to-end processing pipelines
│   └── pdf2qa.py      # Complete PDF to Q&A pipeline
├── tests/              # Test suite
│   └── process_tests.py # Comprehensive test coverage
├── conversion_results/ # Output directory for converted files
├── qa_results/        # Output directory for Q&A pairs
├── to_convert/        # Input directory for documents
└── main.py            # Command-line interface
```

## 🛠️ Installation

### Prerequisites

1. **Python 3.13+**
2. **UV Package Manager** (recommended) or pip
3. **External Dependencies**:
   - `marker-pdf` for PDF conversion
   - `pandoc` for EPUB conversion

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd anyth2data
   ```

2. **Install dependencies**:
   ```bash
   # Using UV (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Install external tools**:
   ```bash
   # Install marker for PDF processing
   pip install marker-pdf
   
   # Install pandoc for EPUB processing
   # macOS
   brew install pandoc
   
   # Ubuntu/Debian
   sudo apt-get install pandoc
   
   # Windows
   # Download from https://pandoc.org/installing.html
   ```

4. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

## 🚀 Quick Start

### 1. Convert Documents to Markdown

```bash
# Convert all supported files in a directory
python main.py --foldername ./to_convert --output_dir ./conversion_results

# Check dependencies first
python main.py --check-deps

# Convert with custom options
python main.py --foldername ./docs --output_dir ./output --keep-source --quiet
```

### 2. Process Markdown Files into Chunks

```python
from utils.process import MarkdownProcessor

# Initialize processor
processor = MarkdownProcessor(min_words=150, join_token=" / ")

# Process a markdown file
output_file = processor.process_md_file("input.md", "output/")
print(f"Chunks saved to: {output_file}")
```

### 3. Generate Q&A Pairs

```python
from json2qa.json2bibleQA import QAGenerator

# Initialize Q&A generator
qa_generator = QAGenerator("gpt-4o")

# Generate Q&A pairs from JSONL chunks
qa_pairs = qa_generator.generate_qa_pairs("chunks.jsonl")

# Save results
qa_generator.save_qa_pairs(qa_pairs, "qa_results.json")
```

### 4. Complete Pipeline

```python
from pipelines.pdf2qa import pdf2qa

# Process PDF to Q&A pairs in one go
qa_pairs = pdf2qa("document.pdf")
```

## 📖 Detailed Usage

### DocumentConverter Class

```python
from anyth2md.anyth2md import DocumentConverter

# Initialize with custom settings
converter = DocumentConverter(
    delete_source=False,  # Keep original files
    verbose=True          # Show detailed output
)

# Convert single file
success = converter.convert_file("document.pdf", "output/")

# Convert entire directory
results = converter.convert_directory("./input", "./output")

# Check supported formats
formats = converter.get_supported_formats()  # ['.pdf', '.epub']

# Verify dependencies
deps = converter.check_dependencies()
```

### MarkdownProcessor Class

```python
from utils.process import MarkdownProcessor

# Initialize with custom parameters
processor = MarkdownProcessor(
    min_words=200,        # Minimum words per chunk
    join_token=" | "      # Custom separator for chunk IDs
)

# Process markdown file
output_file = processor.process_md_file("input.md", "output/")

# Process text directly
chunks = processor.split_markdown_by_any_heading("Title", markdown_text)

# Clean text
cleaned_text = processor.remove_img_links(markdown_text)
```

### LLMClient Class

```python
from llm.llm import LLMClient

# Initialize LLM client
llm_client = LLMClient("gpt-4o", api_key="your-key")

# Basic LLM call
response = llm_client.call_llm(system_prompt, user_prompt)

# Call with custom configuration
response = llm_client.call_llm_with_config(
    system_prompt, 
    user_prompt, 
    temperature=0.7, 
    max_tokens=1000
)

# Batch processing
responses = llm_client.batch_call_llm(prompts, system_prompt)
```

### QAGenerator Class

```python
from json2qa.json2bibleQA import QAGenerator

# Initialize Q&A generator
qa_generator = QAGenerator("gpt-4o")

# Generate Q&A pairs with custom settings
qa_pairs = qa_generator.generate_qa_pairs_with_config(
    "chunks.jsonl",
    temperature=0.5,
    max_tokens=800
)

# Complete pipeline
output_file = qa_generator.process_pipeline(
    "chunks.jsonl", 
    "qa_results.json"
)

# Get processing statistics
stats = qa_generator.get_processing_stats("chunks.jsonl")
```

## 🧪 Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Test Specific File

```bash
python tests/process_tests.py "/path/to/your/file.md"
```

### Test Individual Components

```python
from tests.process_tests import test_specific_md_file

# Test a specific markdown file
chunks = test_specific_md_file("document.md")
```

## ⚙️ Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export PYTHONPATH="${PYTHONPATH}:/path/to/anyth2data"
```

### Custom Prompts

Edit the prompt templates in the `prompts/` directory:
- `qa_system.md`: System prompt for Q&A generation
- `qa_message.md`: Message template for Q&A pairs

### Processing Parameters

```python
# Custom chunking parameters
processor = MarkdownProcessor(
    min_words=200,        # Minimum words per chunk
    join_token=" | "      # Custom separator
)

# Custom LLM parameters
llm_client = LLMClient(
    model_name="gpt-4o",
    temperature=0.7
)
```

## 📊 Output Formats

### JSONL Chunks Format

```json
{"chunk_id": "Document Title / Section 1 / Subsection 1.1", "text": "Chunk content..."}
{"chunk_id": "Document Title / Section 2", "text": "Another chunk..."}
```

### Q&A Pairs Format

```json
[
  {
    "question": "What does verse X teach about...?",
    "answer": "Verse X teaches that...",
    "chunk_id": "Document Title / Section 1"
  }
]
```

## 🔧 Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --foldername TEXT     Input folder name (default: ./to_convert)
  --output_dir TEXT     Output directory (default: ./conversion_results)
  --keep-source         Keep source files after conversion
  --quiet              Suppress verbose output
  --check-deps         Check if required dependencies are installed
  --help               Show this message and exit
```


## 🆘 Troubleshooting

### Common Issues

1. **"marker command not found"**
   ```bash
   pip install marker-pdf
   ```

2. **"pandoc command not found"**
   ```bash
   # macOS
   brew install pandoc
   
   # Ubuntu/Debian
   sudo apt-get install pandoc
   ```

3. **"OpenAI API key not found"**
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

4. **Import errors**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/anyth2data"
   ```

### Dependency Check

```bash
python main.py --check-deps
```

This will verify that all required tools are properly installed.

## 📈 Performance Tips

1. **Batch Processing**: Use `convert_directory()` for multiple files
2. **Custom Chunking**: Adjust `min_words` based on your content
3. **LLM Configuration**: Use appropriate temperature and token limits
4. **Parallel Processing**: Consider using multiprocessing for large datasets

## 🔗 Related Projects

- [Marker PDF](https://github.com/fread-ink/marker) - PDF to markdown conversion
- [Pandoc](https://pandoc.org/) - Universal document converter
- [LangChain](https://langchain.com/) - LLM application framework
- [OpenAI API](https://openai.com/api/) - Language model API
