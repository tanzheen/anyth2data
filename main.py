import argparse
import os
from anyth2md.anyth2md import DocumentConverter, run_marker, run_epub
from pipelines.pipelines import pdf2qa, md2qa

def run_main(foldername, output_dir):
    """Legacy function for backward compatibility."""
    converter = DocumentConverter()
    results = converter.convert_directory(foldername, output_dir)
    
    # Print summary
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    print(f"\nConversion complete: {successful}/{total} files converted successfully")
    
    # Print detailed results
    for filename, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {filename}: {status}")


def run_main_legacy(foldername, output_dir):
    """Original implementation for backward compatibility."""
    for file in os.listdir(foldername):
        print("Processing file: {0}".format(file))
        if file.endswith(".pdf"):
            run_marker(os.path.join(foldername, file), output_dir)
        elif file.endswith(".epub"):
            run_epub(os.path.join(foldername, file), output_dir)
        else:
            print("Unknown file type: {0}".format(file))


def check_dependencies():
    """Check if required dependencies are installed."""
    converter = DocumentConverter(verbose=False)
    deps = converter.check_dependencies()
    print("Dependency Check:")
    for tool, available in deps.items():
        status = "✅ Available" if available else "❌ Not found"
        print(f"  {tool}: {status}")
    
    if not all(deps.values()):
        print("\n⚠️  Some dependencies are missing. Install them to use all features:")
        if not deps.get('marker'):
            print("  - Install marker: pip install marker-pdf")
        if not deps.get('pandoc'):
            print("  - Install pandoc: https://pandoc.org/installing.html")


def main():
    """Main function to handle command line arguments and conversion."""
    parser = argparse.ArgumentParser(description="Document to Markdown Converter")
    parser.add_argument("--foldername", required=False, default="./to_convert", 
                       help="Input folder name")
    parser.add_argument("--output_dir", required=False, default="./conversion_results", 
                       help="Output directory")
    parser.add_argument("--keep-source", action="store_true", 
                       help="Keep source files after conversion (default: delete)")
    parser.add_argument("--quiet", action="store_true", 
                       help="Suppress verbose output")
    parser.add_argument("--check-deps", action="store_true", 
                       help="Check if required dependencies are installed")

    args = parser.parse_args()
    
    # Check dependencies if requested
    if args.check_deps:
        check_dependencies()
        return
    
    # Use new class-based approach
    converter = DocumentConverter(
        delete_source=not args.keep_source,
        verbose=not args.quiet
    )
    
    # Check if input directory exists
    if not os.path.exists(args.foldername):
        print(f"Error: Input directory not found: {args.foldername}")
        exit(1)
    
    # Convert files
    results = converter.convert_directory(args.foldername, args.output_dir)
    
    # Print summary
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    if total > 0:
        print(f"\n🎉 Conversion complete: {successful}/{total} files converted successfully")
        
        if not args.quiet:
            # Print detailed results
            for filename, success in results.items():
                status = "✅ Success" if success else "❌ Failed"
                print(f"  {filename}: {status}")
    else:
        print(f"\n📁 No supported files found in {args.foldername}")
        print(f"Supported formats: {', '.join(converter.get_supported_formats())}")


if __name__ == "__main__":
    main()
