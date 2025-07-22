from utils.process import MarkdownProcessor
from json2qa.json2bibleQA import QAGenerator
from anyth2md.anyth2md import DocumentConverter

def pdf2qa(pdf_file): 
    # process the pdf file\
    doc_converter = DocumentConverter()
    doc_converter.run_marker(pdf_file, )
    # process the md file
    processor = MarkdownProcessor()
    chunks = processor.process_md_file(doc_converter.md_file, doc_converter.output_dir)

    # generate the qa pairs
    qa_generator = QAGenerator()
    qa_pairs = qa_generator.generate_qa_pairs(chunks)
    return qa_pairs