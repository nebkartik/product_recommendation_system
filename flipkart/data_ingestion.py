# import requests, certifi
# print(certifi.where())
# print(requests.get("https://huggingface.co", verify=certifi.where()).status_code)

from langchain_astradb import AstraDBVectorStore
from flipkart.config import Config
from flipkart.data_converter import DataConverter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os, certifi
import requests

requests.get("https://router.huggingface.co", verify=False)
os.environ["SSL_CERT_FILE"] = certifi.where()


class DataIngestor:
    def __init__(self):
        self.embedding = HuggingFaceEndpointEmbeddings(model=Config.embedding_model)
        self.vstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name="product_database",
            api_endpoint=Config.astra_db_api_endpoint,
            token=Config.astra_db_token,
            namespace=Config.astra_db_keyspace
        )

    def ingest(self,load_existing=True):
        if load_existing==True:
            return self.vstore
        docs = DataConverter("data/flipkart_product_review.csv").doc_converter()
        self.vstore.add_documents(docs)
if __name__=="__main__":
    ingestor = DataIngestor()
    ingestor.ingest(load_existing=False)    

