from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from flipkart.data_ingestion import DataIngestor
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from flipkart.config import Config


def rag_retreiver_tool(retreiver):

    @tool("search_product", description="Search for a product in the vector store by query string")
    def rag_retriever_tool(query):
        docs = retreiver.invoke(query)
        return "\n\n".join(doc.page_content for doc in docs)
    return rag_retriever_tool
    

class RAGAgentBuilder: 
    def __init__(self, vector_store):
        self.model = init_chat_model(Config.rag_model)
        self.vector_store = vector_store
    
    def build_agent(self):
        retreiver = self.vector_store.as_retriever(search_kwargs={"k": 3})
        rag_tool = rag_retreiver_tool(retreiver)
        agent = create_agent(
            model=self.model,
            tools=[rag_tool],
            system_prompt= """
            
            You're an e-commerce bot answering product-related queries 
                    based on reviews and titles.
                    
                    And To find the answers always use 
                    rag_retreiver_tool
                    
                    if you do not know an 
                    answer politely say that 
                    i dont know the answer please 
                    contact our customer care +97 98652365.
            
            """,
            checkpointer=InMemorySaver(),
            middleware = [SummarizationMiddleware(
                model=self.model,
                trigger = ("messages", 10),
                keep = ("messages", 4)
            )]
            
            )
        return agent





