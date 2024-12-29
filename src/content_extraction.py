import os
import PyPDF2
import logging
from pathlib import Path


# Configure the logging
log_file_path = "logs/pdfExtraction.log"  
logging.basicConfig(
    level=logging.INFO,           
    filename=log_file_path,         
    filemode='a',                  
    format='%(asctime)s - %(levelname)s - %(message)s'  
)


class PDFExtractor:
    '''
    A class for extracting PDF textbooks.
    '''
    def __init__(self, dir_path: str = None, file_path: str = None):
        self.file_path = Path(file_path) if file_path else None
        self.dir_path = Path(dir_path) if dir_path else None
        self.pdfs = None
        self.pdf_file = None
        self.reader = None
        
    def validate_arguments(self):
        if self.file_path:
            if not self.file_path.is_file() or self.file_path.suffix.lower() != '.pdf':
                raise (f"Invalid file: {self.file_path}. Must be a valid PDF.")
        elif self.dir_path:
            if not self.dir_path.is_dir():
                raise (f"Invalid directory: {self.dir_path}. Must be a valid directory.")
        else:
            raise ("Either 'file_path' or 'dir_path' must be provided.")
            
    
    def load_file(self):
        '''
        Load the PDF document
        '''
        try:
            self.pdf_file = open(self.file_path, 'rb')  
            self.reader = PyPDF2.PdfReader(self.pdf_file)
            logging.info(f'Successfully loaded the file: {self.file_path}')
        except Exception as e:
            logging.error(f'Error in loading PDF document: {e}')
            raise
    
    def extract_content(self):
        '''
        Extract the content from the PDF document(s)
        '''
        try:
            if not self.reader:
                logging.error('PDF not loaded. Load the PDF first.')
                raise ValueError('PDF is not loaded.')
            
            # Extract content 
            text = ''
            for pg_num, page in enumerate(self.reader.pages):
                text += f"\n[PAGE_{pg_num + 1}]\n" + page.extract_text()
            
            logging.info(f'Successfully extracted the text from PDF: {self.file_path}')
            
            # Store extracted content in a txt file
            save_file_name = f'data/extracted/{self.file_path.stem}.txt'  
            save_file_path = Path(save_file_name)
            
            # Ensure directory exists
            save_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_file_path, 'w', encoding='utf-16') as file:
                file.writelines(text)
            logging.info(f'Successfully stored the raw extracted content of PDF: {self.file_path} at {save_file_name}')
                
        except Exception as e:
            logging.error(f'Unable to extract the content: {e}')
            raise
    
    def close_pdf(self):
        '''
        Close the open file to free up space
        '''
        if self.pdf_file:
            self.pdf_file.close()
            logging.info(f'Closed PDF: {self.file_path}')
    
    def process_single_pdf(self):
        '''Process a single PDF file (from file_path).'''
        self.load_file()
        self.extract_content()
        self.close_pdf()
    
    def process_multiple_pdfs(self):
        '''Process all PDFs in the directory (from dir_path).'''
        try:
            if not self.dir_path.is_dir():
                raise ValueError(f"Provided directory path is not valid: {self.dir_path}")
            
            self.pdfs = [file for file in os.listdir(self.dir_path)]
            logging.info(f'Loaded all PDF documents from directory: {self.dir_path}')
                
            for pdf in self.pdfs:
                self.file_path = self.dir_path / pdf
                self.process_single_pdf()
            
            logging.info('Successfully extracted content from all PDF documents.')
        
        except Exception as e:
            logging.error(f'Error while processing PDFs in directory: {e}')
            raise
    
    def process(self):
        '''
        Implement the whole process from load to extract and close the file.
        '''
        try:
            
            if not self.file_path and not self.dir_path:
                raise ValueError("Either 'file_path' or 'dir_path' must be provided.")
            elif self.dir_path:
                self.validate_arguments()
                self.process_multiple_pdfs()
            elif self.file_path:
                self.validate_arguments()
                self.process_single_pdf()
            else:
                raise ValueError("Both 'file_path' and 'dir_path' cannot be passed simultaneously.")
        
        except Exception as e:
            logging.error(f'Error in processing: {e}')
            raise 


# Test extractor
if __name__ == '__main__':
    dir_path = 'data\\pdfs'
    extractor = PDFExtractor(dir_path=dir_path)
    extractor.process()