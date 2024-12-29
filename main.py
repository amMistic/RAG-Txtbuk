from src.content_extraction import PDFExtractor
from src.hierarchical_indexing import process_textbooks
from typing import List
import os

def main():
    # Define the directory containing the PDF files
    dir_path = 'data//pdfs'
    
    # Step 1: Extracted the pdfs content and store it into the data/extracted directory
    extractor = PDFExtractor(dir_path=dir_path)
    extractor.process()
    
    # Step 2: Process the extracted content and store the processed content into the data/processed directory
    dir_path = 'data//extracted'
    textbooks = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.txt')]
    output_directory = "data//processed"
    process_textbooks(textbooks, output_directory)
    
    # Step 3: Perform the semantic chunking and store thes chunked content into the data/chunked_data directory
    semantic_chunking = 'data//processed'
    

if __name__ == '__main__':
    main()