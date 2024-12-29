from llama_index.core.node_parser import SemanticSplitterNodeParser
from .utils import configure_logging, get_embedding_model
from llama_index.core.schema import Document, Node
from pathlib import Path
from typing import List
import logging
import os

# Configure logging
file_path = 'semantic_chunking.log'
configure_logging(file_path)

class SemanticChunking:
    def __init__(self, buffer_size: int = 512, breakpoint_threshold: int = 80,file_path: str = None, output_path: str = None):
        """
        Initialize the processor with HuggingFace model for embeddings and splitter configuration.

        Args:
            buffer_size (int): Buffer size for semantic chunking.
            breakpoint_threshold (int): Percentile threshold for semantic breaks.
            file_path (str): Input file path.
            output_path (str): Directory for output files.
        """
        self.file_path = Path(file_path) if file_path else None
        self.output_path = Path(output_path) if output_path else None
        self.embed_model = get_embedding_model()
        self.splitter = SemanticSplitterNodeParser(
            buffer_size=buffer_size,
            breakpoint_threshold=breakpoint_threshold,
            embed_model=self.embed_model,
        )
        self.node = None
    
    def load_text_file(self) -> str:
        """
        Load the text file.
        
        Returns:
            str: Content of the text file.
        """
        print('Enter load_text_file')
        try:
            logging.info(f"Loading text file: {self.file_path}")
            
            # Check file existence and extension
            if not self.file_path.is_file():
                logging.error(f"File does not exist: {self.file_path}")
                raise FileNotFoundError(f"File does not exist: {self.file_path}")
            
            if not self.file_path.suffix.lower() == '.txt':
                logging.error(f"Invalid file extension: {self.file_path.suffix}")
                raise ValueError(f"Invalid file extension: {self.file_path}")
            
            print('Reading file')
            with open(self.file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
        
        except Exception as e:
            with open(self.file_path, 'r', encoding='utf-16') as file:
                text = file.read()
            return text
            # logging.error(f"Failed to load text file: {e}")
            # raise Exception(f"Error loading text file: {e}")
    
    def perform_text_chunking(self, text: str) -> List[Node]:
        """
        Perform semantic chunking on the text.
        
        Args:
            text (str): Input text.
        
        Returns:
            List[Node]: List of chunked nodes.
        """
        print('Enter perform_text_chunking')
        try:
            print('Splitting text')
            document = Document(text=text)
            print('Getting nodes')
            nodes = self.splitter.get_nodes_from_documents([document])
            logging.info(f"Semantic chunking completed. Total nodes: {len(nodes)}")
            self.node = nodes
            return nodes
        except Exception as e:
            logging.error(f"Failed to process text: {e}")
            raise Exception(f"Error during text chunking: {e}")
    
    def save_chunks(self, nodes: List[Node]):
        """
        Save the chunked nodes to the output directory.
        
        Args:
            nodes (List[Node]): List of nodes to save.
        """
        print('Enter save_chunks')
        try:
            logging.info(f"Saving nodes to: {self.output_path}")
            
            # Ensure the output directory exists
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            print('Writing nodes')
            file_name = f"{self.file_path.stem}.json"
            file_path = self.output_path / file_name
            
            with open(file_path, 'w', encoding='utf-8') as file:
                for i, node in enumerate(nodes):
                    file.write(node.to_json() + '\n')
            
            logging.info(f"Nodes saved successfully to: {file_path}")
        
        except Exception as e:
            with open(file_path, 'w', encoding='utf-16') as file:
                for i, node in enumerate(nodes):
                    file.write(node.to_json() + '\n')
            
            logging.error(f"Failed to save nodes: {e}")
            raise Exception(f"Error saving nodes: {e}")
    
    def process(self):
        """
        Process the input text file: load, chunk, and save.
        """
        try:
            print('Enter process..')
            text = self.load_text_file()
            nodes = self.perform_text_chunking(text)
            self.save_chunks(nodes)
            logging.info("Processing completed successfully")
        except Exception as e:
            logging.error(f"Failed to process text file: {e}")
            raise Exception(f"Error processing text file: {e}")


if __name__ == '__main__':

    # Initialize the SemanticChunking processor
    input_file = 'data//testing//extracted//sample.txt'
    output_dir = 'data//chunked_data'
        
    sc = SemanticChunking(file_path=input_file, output_path=output_dir)
    sc.process()
