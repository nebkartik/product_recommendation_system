import os
import dotenv

# load_dotenv()


class Config:
    hf_token = os.getenv('hf_token')
    groq_api_key = os.getenv('groq_api_key')
    astra_db_token = os.getenv('astra_db_token')
    astra_db_api_endpoint = os.getenv('astra_db_api_endpoint') 
    astra_db_keyspace = os.getenv('astra_db_keyspace')
    embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'
    rag_model = 'groq:qwen/qwen3-32b'