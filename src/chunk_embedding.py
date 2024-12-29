from .utils import configure_logging, get_embedding_model
from .semantic_chunking import SemanticChunking

from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.schema import  Document, Node
from llama_index.core import VectorStore
from dotenv import load_dotenv
from typing import List
import logging
import faiss

# Load the environment variables
load_dotenv()

# Configure logging
configure_logging('chunk_embedding.log')

class ChunkEmbedding:
    def __init__(self, vector_store: FaissVectorStore = None, node: List[Node] = None):
        """
        Initialize the processor with HuggingFace model for embeddings and splitter configuration.
        """
        self.node = node
        self.embed_model = get_embedding_model()
        self.embedding_size = self.embed_model.get_embedding_size()
        self.faiss_index = faiss.IndexFlatL2(self.embedding_size) 
        self.vector_store = vector_store if vector_store else FaissVectorStore(self.faiss_index)
    
    def embed_chunk(self) -> None:
        """
        Embed the chunk using the embedding model.
        
        Args:
            node (List[Node]): List of nodes to embed.
        """
        embeddings= []
        metadata = []
        try:
            for n in self.node:
                if n.text:
                    embeddings.append(self.embed_model.encode(n.text))
                    n_metadata = {
                        "node_id": n.node_id,
                        "text": n.text
                    }
                    metadata.append(n_metadata)
                    
            # Store embeddings and metadata in the vector store
            self.vector_store.add_embeddings(embeddings, metadata)
            logging.info(f"Successfully stored {len(embeddings)} embeddings in the vector store.")
            
        except Exception as e:
            logging.error(f"Failed to embed chunk: {self.node}")
            raise ('Error: Failed to embed chunk - ', e)
        
    
    def process(self):
        """
        Process the chunk embeddings.
        """
        try:
            # Embed the chunk
            self.embed_chunk()
            logging.info(f"Successfully processed chunk embeddings.")
        
        except Exception as e:
            logging.error(f"Failed to process chunk embeddings.")
            raise ('Error: Failed to process chunk embeddings - ', e)

if __name__ == '__main__':
    # Initialize the processor
    chunk_embedding = ChunkEmbedding()
    chunk_embedding.process()