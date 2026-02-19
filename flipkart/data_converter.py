import pandas as pd
from langchain_core.documents import Document

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
            # docs.append(doc)
        return docs