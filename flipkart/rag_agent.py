from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from flipkart.data_ingestion import DataIngestor
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from flipkart.config import Config
from utils.logger import get_logger
from utils.custom_exception import CustomException
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import  WikipediaAPIWrapper

from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper

def rag_retreiver_tool(retreiver):
    get_logger("RAGAgent").info("RAG Retreiver Called.")

    @tool("search_product", description="Search for a product in the vector store by query string")
    def rag_retriever_tool(query):
        docs = retreiver.invoke(query)
        return "\n\n".join(doc.page_content for doc in docs)
    return rag_retriever_tool


# Wikipedia Tool
wiki_api_wrapper = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=300)
wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api_wrapper)

    

class RAGAgentBuilder: 
    def __init__(self, vector_store):
        self.model = init_chat_model(Config.rag_model)
        self.vector_store = vector_store
    
    def build_agent(self):
        try:
            retreiver = self.vector_store.as_retriever(search_kwargs={"k": 3})
            rag_tool = rag_retreiver_tool(retreiver)

            get_logger("RAGAgent").info("Vector Store Docs Retreived")

            agent = create_agent(
                model=self.model,
                tools=[rag_tool,wiki_tool],
                system_prompt= """
                
                You're an e-commerce bot answering product-related queries 
                        based on reviews and titles.
                        
                        And To find the answers always use 
                        tools
                        if you do not know an 
                        answer politely say that 
                        i dont know the answer please 
                        contact our customer care +97 98652365.
                        Prefix your response with FINAL ANSWER so the team knows to stop.
                
                """,
                # checkpointer=InMemorySaver(),
                # middleware = [SummarizationMiddleware(
                #     model=self.model,
                #     trigger = ("messages", 10),
                #     keep = ("messages", 4)
                # )]
                
                )
        except Exception as e:
            get_logger("RAGAgent").error("Error during RAG Agent creation: %s", str(e))
            raise CustomException("Failed to build RAG Agent", e)
        
        get_logger("RAGAgent").info("RAG Agent Built.")
        return agent





