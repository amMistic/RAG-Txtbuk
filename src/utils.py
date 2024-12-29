from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from pathlib import Path
import logging
import os

# Load the environment variables
load_dotenv()

def configure_logging(file_path: str):
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs//{file_path}', mode='a')
    ]
)
    

def get_embedding_model():   
    '''
    Load the embedding model
    '''
    try:
        model_name = 'sentence-transformers/all-mpnet-base-v2'
        
        # Access the Hugging Face API Key from environment variables
        hf_api_key = os.getenv("HF_API_KEY")
        
        if not hf_api_key:
            raise ValueError("Hugging Face API Key not found in environment variables.")
        
        # Set the Hugging Face API key in the environment
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_api_key

        lg_embed_model = HuggingFaceEmbeddings(model_name=model_name)
        embed_model = LangchainEmbedding(lg_embed_model)
        logging.info(f"Loaded embedding model: {model_name}")
        return embed_model

    except Exception as e:
        logging.error(f"Failed to load embedding model: {model_name}")
        raise ('Error: Failed to load embedding model - ', e)
