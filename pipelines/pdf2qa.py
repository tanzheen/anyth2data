from utils.process import MarkdownProcessor
from json2qa.json2QA import QAGenerator
from anyth2md.anyth2md import DocumentConverter
from utils.config import env
import os 

def pdf2qa(pdf_file): 
    # process the pdf file\
    doc_converter = DocumentConverter()
    doc_converter.run_marker(pdf_file, env.MD_DIR)
    # process the md file
    processor = MarkdownProcessor()
    md_file = pdf_file.split("/")[-1].split(".")[0] + ".md"
    chunks = processor.process_md_file(os.path.join(env.MD_DIR, md_file), env.JSONL_DIR)

    json_file = md_file.split("/")[-1].split(".")[0] + ".jsonl"
    # generate the qa pairs
    qa_generator = QAGenerator(api_key=env.LLM_API_KEY)
    qa_pairs = qa_generator.generate_qa_pairs(os.path.join(env.JSONL_DIR, json_file))
    # save the qa pairs
    qa_file = md_file.split("/")[-1].split(".")[0] + ".json"
    qa_generator.save_qa_pairs(qa_pairs, os.path.join(env.QA_DIR, qa_file))

    return qa_file


