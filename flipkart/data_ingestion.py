from langchain_astradb import AstraDBVectorStore
from flipkart.config import Config
from flipkart.data_converter import DataConverter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain.embeddings.base import Embeddings
from utils.logger import get_logger
from utils.custom_exception import CustomException

# print("API endpoint:", os.getenv("ASTRA_DB_API_ENDPOINT"))


# requests.get("https://router.huggingface.co", verify=False)
# os.environ["SSL_CERT_FILE"] = certifi.where()

# Testing Dummy Embeddings 
# class DummyEmbeddings(Embeddings):
#     def embed_documents(self, texts):
#         return [[0.0] * 10 for _ in texts]  # fixed 10-dim zero vector
#     def embed_query(self, text):
#         return [0.0] * 10

get_logger("DataIngestion").info("Starting data ingestion process...")
class DataIngestor:
    def __init__(self):
        self.embedding = HuggingFaceEndpointEmbeddings(model=Config.embedding_model)
        # self.embedding = DummyEmbeddings()
        self.vstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name="product_database",
            api_endpoint=Config.astra_db_api_endpoint,
            token=Config.astra_db_token,
            namespace=Config.astra_db_keyspace
        )
    get_logger("DataIngestion").info("DataIngestor initialized with VectorDB")

    def ingest(self,load_existing=True):
     try:

        if load_existing==True:
            return self.vstore
        docs = DataConverter("data/flipkart_product_review.csv").doc_converter()
        self.vstore.add_documents(docs)

     except Exception as e:
        get_logger("DataIngestion").error("Error during data ingestion: %s", str(e))
        raise CustomException("Failed to ingest data", e)

    get_logger("DataIngestion").info("Data ingestion completed successfully.")

if __name__=="__main__":
    ingestor = DataIngestor()
    ingestor.ingest(load_existing=False)    

