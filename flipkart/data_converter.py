import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DataConverter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def doc_converter(self):
        docs = []
        df = pd.read_csv(self.file_path)[['product_id', 'review']]
        for _, row in df.iterrows():    
            docs.append(Document(
                page_content=row['review'],
                metadata={'product_id': row['product_id']}
            ))
        chunker = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        chunks = chunker.split_documents(docs)
        return chunks
