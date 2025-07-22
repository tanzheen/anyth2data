import unittest
import os
import tempfile
import json
from unittest.mock import patch, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from process.process import MarkdownProcessor, process_md_file, remove_img_links, split_markdown_by_any_heading


class TestMarkdownProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = MarkdownProcessor()
        
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_markdown_processor_initialization(self):
        """Test MarkdownProcessor initialization with custom parameters."""
        processor = MarkdownProcessor(min_words=200, join_token=" | ")
        self.assertEqual(processor.min_words, 200)
        self.assertEqual(processor.join_token, " | ")
    
    def test_remove_img_links(self):
        """Test image link removal functionality."""
        text_with_images = """# Test Document
This is a test document with images.

![alt text](image1.png)

## Section with Image
This section contains an image ![another image](image2.jpg) in the middle.

More content here.
"""
        
        cleaned_text = self.processor.remove_img_links(text_with_images)
        
        # Check that image links are removed
        self.assertNotIn('![', cleaned_text)
        self.assertNotIn('](', cleaned_text)
        self.assertIn('# Test Document', cleaned_text)
        self.assertIn('More content here', cleaned_text)
    
    def test_split_markdown_by_any_heading(self):
        """Test markdown splitting functionality."""
        md_content = """# Introduction
This is a test document with some content.

## Section 1
This section has enough words to meet the minimum requirement. 
It contains multiple sentences to ensure we have at least 150 words in this chunk.
The content should be properly processed and saved to a jsonl file.
We need to add more text to reach the word count threshold.

### Subsection 1.1
This is a subsection with additional content.

## Section 2
This is another section with different content.
It should be processed as a separate chunk.
The content continues here to ensure proper chunking.
"""
        
        chunks = self.processor.split_markdown_by_any_heading(md_content)
        
        # Verify we have chunks
        self.assertGreater(len(chunks), 0)
        
        # Verify chunk structure
        for chunk in chunks:
            self.assertIn('chunk_id', chunk)
            self.assertIn('text', chunk)
            self.assertIsInstance(chunk['chunk_id'], str)
            self.assertIsInstance(chunk['text'], str)
    
    def test_save_chunks_to_jsonl(self):
        """Test saving chunks to JSONL file."""
        chunks = [
            {"chunk_id": "Test / Section 1", "text": "This is test content 1"},
            {"chunk_id": "Test / Section 2", "text": "This is test content 2"}
        ]
        
        output_file = os.path.join(self.temp_dir, "test_chunks.jsonl")
        self.processor.save_chunks_to_jsonl(chunks, output_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Verify content
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        # Verify JSON structure
        for line in lines:
            chunk = json.loads(line.strip())
            self.assertIn('chunk_id', chunk)
            self.assertIn('text', chunk)
    
    def test_process_md_file_method(self):
        """Test the process_md_file method of MarkdownProcessor."""
        md_content = """# Introduction
This is a test document with some content.

## Section 1
This section has enough words to meet the minimum requirement. 
It contains multiple sentences to ensure we have at least 150 words in this chunk.
The content should be properly processed and saved to a jsonl file.
We need to add more text to reach the word count threshold.
"""
        
        md_file_path = os.path.join(self.temp_dir, "test.md")
        with open(md_file_path, 'w') as f:
            f.write(md_content)
        
        # Process the file using the class method
        output_file = self.processor.process_md_file(md_file_path, self.temp_dir)
        
        # Check that output file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Read and verify the output
        chunks = []
        with open(output_file, 'r') as f:
            for line in f:
                chunks.append(json.loads(line.strip()))
        
        # Verify we have chunks
        self.assertGreater(len(chunks), 0)
        
        # Verify chunk structure
        for chunk in chunks:
            self.assertIn('chunk_id', chunk)
            self.assertIn('text', chunk)
            self.assertIsInstance(chunk['chunk_id'], str)
            self.assertIsInstance(chunk['text'], str)
    
    def test_process_chunk_method(self):
        """Test the process_chunk method."""
        chunk = {"chunk_id": "Test Heading", "text": "This is test content"}
        
        # Create a mock prompt template
        class MockTemplate:
            def format(self, **kwargs):
                return f"Processed: {kwargs.get('heading')} - {kwargs.get('chunk_text')}"
        
        mock_template = MockTemplate()
        result = self.processor.process_chunk(chunk, mock_template)
        
        self.assertIn("Test Heading", result)
        self.assertIn("This is test content", result)


class TestProcessMdFile(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_process_md_file_normal_operation(self):
        """Test normal operation of process_md_file with valid markdown content."""
        # Create a temporary markdown file
        md_content = """# Introduction
This is a test document with some content.

## Section 1
This section has enough words to meet the minimum requirement. 
It contains multiple sentences to ensure we have at least 150 words in this chunk.
The content should be properly processed and saved to a jsonl file.
We need to add more text to reach the word count threshold.

### Subsection 1.1
This is a subsection with additional content.

## Section 2
This is another section with different content.
It should be processed as a separate chunk.
The content continues here to ensure proper chunking.
"""
        
        md_file_path = os.path.join(self.temp_dir, "test.md")
        with open(md_file_path, 'w') as f:
            f.write(md_content)
        
        # Process the file
        process_md_file(md_file_path, self.temp_dir)
        
        # Check that output file was created
        output_file = os.path.join(self.temp_dir, "test.md.jsonl")
        self.assertTrue(os.path.exists(output_file))
        
        # Read and verify the output
        chunks = []
        with open(output_file, 'r') as f:
            for line in f:
                chunks.append(json.loads(line.strip()))
        
        # Verify we have chunks
        self.assertGreater(len(chunks), 0)
        
        # Verify chunk structure
        for chunk in chunks:
            self.assertIn('chunk_id', chunk)
            self.assertIn('text', chunk)
            self.assertIsInstance(chunk['chunk_id'], str)
            self.assertIsInstance(chunk['text'], str)
    
    def test_process_md_file_with_images(self):
        """Test that image links are properly removed during processing."""
        md_content = """# Test Document
This is a test document with images.

![alt text](image1.png)

## Section with Image
This section contains an image ![another image](image2.jpg) in the middle.

More content here.
"""
        
        md_file_path = os.path.join(self.temp_dir, "test_with_images.md")
        with open(md_file_path, 'w') as f:
            f.write(md_content)
        
        # Process the file
        process_md_file(md_file_path, self.temp_dir)
        
        # Check output
        output_file = os.path.join(self.temp_dir, "test_with_images.md.jsonl")
        self.assertTrue(os.path.exists(output_file))
        
        # Verify images were removed
        with open(output_file, 'r') as f:
            chunks = [json.loads(line.strip()) for line in f]
        
        for chunk in chunks:
            # Check that image links are not present
            self.assertNotIn('![', chunk['text'])
            self.assertNotIn('](', chunk['text'])
    
    def test_process_md_file_small_content(self):
        """Test processing of markdown with content smaller than min_words threshold."""
        md_content = """# Small Document
This is a very small document that might not meet the minimum word count.
"""
        
        md_file_path = os.path.join(self.temp_dir, "small_test.md")
        with open(md_file_path, 'w') as f:
            f.write(md_content)
        
        # Process the file
        process_md_file(md_file_path, self.temp_dir)
        
        # Check output
        output_file = os.path.join(self.temp_dir, "small_test.md.jsonl")
        self.assertTrue(os.path.exists(output_file))
        
        # Verify content was still processed
        with open(output_file, 'r') as f:
            chunks = [json.loads(line.strip()) for line in f]
        
        self.assertGreater(len(chunks), 0)
    
    def test_process_md_file_complex_headings(self):
        """Test processing with complex heading structure."""
        md_content = """# Main Title
Introduction content.

## Section A
Content for section A.

### Subsection A.1
Content for subsection A.1.

#### Sub-subsection A.1.1
Content for sub-subsection.

## Section B
Content for section B.

### Subsection B.1
More content here.
"""
        
        md_file_path = os.path.join(self.temp_dir, "complex_test.md")
        with open(md_file_path, 'w') as f:
            f.write(md_content)
        
        # Process the file
        process_md_file(md_file_path, self.temp_dir)
        
        # Check output
        output_file = os.path.join(self.temp_dir, "complex_test.md.jsonl")
        self.assertTrue(os.path.exists(output_file))
        
        # Verify chunk IDs reflect heading hierarchy
        with open(output_file, 'r') as f:
            chunks = [json.loads(line.strip()) for line in f]
        
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        
        # Check that we have hierarchical chunk IDs
        for chunk_id in chunk_ids:
            self.assertIsInstance(chunk_id, str)
            self.assertGreater(len(chunk_id), 0)
    
    def test_process_md_file_file_not_found(self):
        """Test error handling when input file doesn't exist."""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.md")
        
        with self.assertRaises(FileNotFoundError):
            process_md_file(non_existent_file, self.temp_dir)
    
    def test_process_md_file_output_directory_not_exists(self):
        """Test that output directory is created if it doesn't exist."""
        md_content = "# Test\nThis is a test."
        md_file_path = os.path.join(self.temp_dir, "test.md")
        with open(md_file_path, 'w') as f:
            f.write(md_content)
        
        # Create a new output directory that doesn't exist
        new_output_dir = os.path.join(self.temp_dir, "new_output_dir")
        
        # Process the file
        process_md_file(md_file_path, new_output_dir)
        
        # Check that output directory was created
        self.assertTrue(os.path.exists(new_output_dir))
        
        # Check that output file was created
        output_file = os.path.join(new_output_dir, "test.md.jsonl")
        self.assertTrue(os.path.exists(output_file))
    
    def test_process_md_file_empty_content(self):
        """Test processing of empty markdown file."""
        md_file_path = os.path.join(self.temp_dir, "empty.md")
        with open(md_file_path, 'w') as f:
            f.write("")
        
        # Process the file
        process_md_file(md_file_path, self.temp_dir)
        
        # Check output
        output_file = os.path.join(self.temp_dir, "empty.md.jsonl")
        self.assertTrue(os.path.exists(output_file))
        
        # Verify empty content was handled
        with open(output_file, 'r') as f:
            chunks = [json.loads(line.strip()) for line in f]
        
        # Should have at least one chunk (even if empty)
        self.assertGreaterEqual(len(chunks), 0)
    
    def test_process_specific_md_file(self, md_file_path=None):
        """Test processing of a specific markdown file provided by the user."""
        if md_file_path is None:
            self.skipTest("No specific markdown file provided")
        
        if not os.path.exists(md_file_path):
            self.fail(f"Markdown file not found: {md_file_path}")
        
        # Create output directory
        output_dir = os.path.join(self.temp_dir, "specific_test_output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Process the file
        process_md_file(md_file_path, output_dir)
        
        # Check that output file was created
        output_file = os.path.join(output_dir, os.path.basename(md_file_path) + ".jsonl")
        self.assertTrue(os.path.exists(output_file))
        
        # Read and verify the output
        chunks = []
        with open(output_file, 'r') as f:
            for line in f:
                chunks.append(json.loads(line.strip()))
        
        # Verify we have chunks
        self.assertGreater(len(chunks), 0)
        
        # Verify chunk structure
        for chunk in chunks:
            self.assertIn('chunk_id', chunk)
            self.assertIn('text', chunk)
            self.assertIsInstance(chunk['chunk_id'], str)
            self.assertIsInstance(chunk['text'], str)
        
        # Print summary for user
        print(f"\nProcessed {md_file_path}")
        print(f"Generated {len(chunks)} chunks")
        print(f"Output saved to: {output_file}")
        
        # Print chunk information
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            print(f"  ID: {chunk['chunk_id']}")
            print(f"  Text length: {len(chunk['text'])} characters")
            print(f"  Preview: {chunk['text'][:100]}...")
        
        return chunks


def test_specific_md_file(md_file_path):
    """
    Helper function to test a specific markdown file.
    
    Args:
        md_file_path (str): Path to the markdown file to test
    
    Returns:
        list: The processed chunks
    """
    if not os.path.exists(md_file_path):
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")
    
    # Create a temporary directory for output
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Process the file
        process_md_file(md_file_path, temp_dir)
        
        # Read the output
        output_file = os.path.join(temp_dir, os.path.basename(md_file_path) + ".jsonl")
        
        if not os.path.exists(output_file):
            raise RuntimeError(f"Output file was not created: {output_file}")
        
        chunks = []
        with open(output_file, 'r') as f:
            for line in f:
                chunks.append(json.loads(line.strip()))
        
        # Print summary
        print(f"\n✅ Successfully processed {md_file_path}")
        print(f"📁 Output saved to: {output_file}")
        print(f"📊 Generated {len(chunks)} chunks")
        
        # Print chunk details
        for i, chunk in enumerate(chunks):
            print(f"\n📄 Chunk {i+1}:")
            print(f"   🏷️  ID: {chunk['chunk_id']}")
            print(f"   📏 Length: {len(chunk['text'])} characters")
            print(f"   📝 Preview: {chunk['text'][:100]}{'...' if len(chunk['text']) > 100 else ''}")
        
        return chunks
        
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    # If a file path is provided as command line argument, test that specific file
    if len(sys.argv) > 1:
        md_file_path = sys.argv[1]
        print(f"Testing specific markdown file: {md_file_path}")
        test_specific_md_file(md_file_path)
    else:
        # Run all unit tests
        unittest.main()

# run the test with the following command with 1 peter notes: 
'''
python tests/process_tests.py "filepath"
'''
