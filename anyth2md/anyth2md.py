import subprocess
import argparse
import os
import logging
import ebooklib
from ebooklib import epub
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class DocumentConverter:
    """
    A class for converting various document formats to markdown.
    
    This class handles the conversion of PDF and EPUB files to markdown format
    using external tools like marker and pandoc.
    """
    
    def __init__(self, delete_source: bool = True, verbose: bool = True):
        """
        Initialize the DocumentConverter.
        
        Args:
            delete_source: Whether to delete source files after successful conversion
            verbose: Whether to print detailed output during conversion
        """
        self.delete_source = delete_source
        self.verbose = verbose
        logger.info(f"DocumentConverter initialized with delete_source={delete_source}, verbose={verbose}")
    
    def _log(self, message: str) -> None:
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def _check_file_exists(self, filename: str) -> bool:
        """Check if the input file exists."""
        if not os.path.exists(filename):
            self._log(f"Error: File not found: {filename}")
            return False
        return True
    
    def _create_output_dir(self, output_dir: str) -> bool:
        """Create output directory if it doesn't exist."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            return True
        except Exception as e:
            self._log(f"Error creating output directory: {e}")
            return False
    
    def run_marker(self, filename: str, output_dir: str) -> bool:
        """
        Convert PDF to markdown using marker.
        
        Args:
            filename: Path to the PDF file
            output_dir: Directory to save the output markdown file
            
        Returns:
            True if conversion was successful, False otherwise
        """
        logger.info(f"Converting PDF to markdown: {filename} -> {output_dir}")
        if not self._check_file_exists(filename):
            logger.error(f"File not found: {filename}")
            return False
        
        if not self._create_output_dir(output_dir):
            logger.error(f"Failed to create output dir: {output_dir}")
            return False
        
        command = [
            "uv", "run", "marker_single",
            filename,
            "--output_dir", output_dir,
            "--output_format", "markdown"
        ]

        try:
            self._log(f"Running command: {' '.join(command)}")
            subprocess.run(command, check=True)
            
            # If succeeded and delete_source is enabled, delete the source file
            if self.delete_source:
                os.remove(filename)
                self._log(f"Deleted source file: {filename}")
            
            self._log(f"Successfully converted {filename} to markdown")
            logger.info(f"Successfully converted {filename} to markdown")
            return True

        except subprocess.CalledProcessError as e:
            self._log(f"Command failed: {e}")
            logger.error(f"Marker conversion failed: {e}")
            return False
        except FileNotFoundError:
            self._log("Error: 'uv' or 'marker_single' command not found. Please ensure marker is installed.")
            logger.error("'uv' or 'marker_single' command not found.")
            return False
    
    def run_epub(self, filename: str, output_dir: str) -> bool:
        """
        Convert EPUB to markdown using pandoc.
        
        Args:
            filename: Path to the EPUB file
            output_dir: Directory to save the output markdown file
            
        Returns:
            True if conversion was successful, False otherwise
        """
        logger.info(f"Converting EPUB to markdown: {filename} -> {output_dir}")
        if not self._check_file_exists(filename):
            logger.error(f"File not found: {filename}")
            return False
        
        if not self._create_output_dir(output_dir):
            logger.error(f"Failed to create output dir: {output_dir}")
            return False
        
        output_file = os.path.join(output_dir, os.path.basename(filename) + ".md")
        
        try:
            self._log(f"Converting EPUB to markdown: {filename} -> {output_file}")
            command = [
                "pandoc", filename,
                "-f", "epub",
                "-t", "markdown",
                "-o", output_file
            ]
            
            self._log(f"Running command: {' '.join(command)}")
            subprocess.run(command, check=True)
            
            # If succeeded and delete_source is enabled, delete the source file
            if self.delete_source:
                os.remove(filename)
                self._log(f"Deleted source file: {filename}")
            
            self._log(f"Successfully converted {filename} to markdown: {output_file}")
            logger.info(f"Successfully converted {filename} to markdown")
            return True

        except subprocess.CalledProcessError as e:
            self._log(f"Command failed: {e}")
            logger.error(f"EPUB conversion failed: {e}")
            return False
        except FileNotFoundError:
            self._log("Error: 'pandoc' command not found. Please ensure pandoc is installed.")
            logger.error("'pandoc' command not found.")
            return False
    
    def convert_file(self, filename: str, output_dir: str) -> bool:
        """
        Convert a file to markdown based on its extension.
        
        Args:
            filename: Path to the file to convert
            output_dir: Directory to save the output markdown file
            
        Returns:
            True if conversion was successful, False otherwise
        """
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension == '.pdf':
            return self.run_marker(filename, output_dir)
        elif file_extension == '.epub':
            return self.run_epub(filename, output_dir)
        else:
            self._log(f"Unsupported file type: {file_extension}")
            return False
    
    def convert_directory(self, input_dir: str, output_dir: str) -> Dict[str, bool]:
        """
        Convert all supported files in a directory.
        
        Args:
            input_dir: Directory containing files to convert
            output_dir: Directory to save the output markdown files
            
        Returns:
            Dictionary mapping filenames to conversion success status
        """
        if not os.path.exists(input_dir):
            self._log(f"Error: Input directory not found: {input_dir}")
            return {}
        
        results = {}
        supported_extensions = {'.pdf', '.epub'}
        
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            if os.path.isfile(file_path):
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in supported_extensions:
                    self._log(f"Processing file: {filename}")
                    success = self.convert_file(file_path, output_dir)
                    results[filename] = success
                else:
                    self._log(f"Skipping unsupported file: {filename}")
                    results[filename] = False
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        return ['.pdf', '.epub']
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if required external tools are available.
        
        Returns:
            Dictionary mapping tool names to availability status
        """
        dependencies = {}
        
        # Check for marker
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            subprocess.run(["uv", "run", "marker_single", "--help"], 
                         capture_output=True, check=True)
            dependencies['marker'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            dependencies['marker'] = False
        
        # Check for pandoc
        try:
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
            dependencies['pandoc'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            dependencies['pandoc'] = False
        
        return dependencies


# Backward compatibility functions
def run_marker(filename, output_dir):
    """Backward compatibility function."""
    converter = DocumentConverter()
    return converter.run_marker(filename, output_dir)


def run_epub(filename, output_dir):
    """Backward compatibility function."""
    converter = DocumentConverter()
    return converter.run_epub(filename, output_dir)