import os
import dotenv
from dotenv import load_dotenv

load_dotenv()


class Config:
    hf_token = os.getenv('HF_TOKEN')
    groq_api_key = os.getenv('GROQ_API_KEY')
    astra_db_token = os.getenv('ASTRA_DB_TOKEN')
    astra_db_api_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT') 
    astra_db_keyspace = os.getenv('ASTRA_DB_KEYSPACE')
    embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'
    rag_model = 'groq:qwen/qwen3-32b'