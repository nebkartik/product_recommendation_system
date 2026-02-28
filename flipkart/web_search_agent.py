from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from flipkart.config import Config
from utils.logger import get_logger
from utils.custom_exception import CustomException

class SearchAgent:

    def build_agent():   
        try: 
            arxiv_api_wrapper = ArxivAPIWrapper(top_k_results=2,doc_content_chars_max=500)
            arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api_wrapper)

            duckduckgo_wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", safesearch="moderate", time="w")
            duckduckgo_tool = DuckDuckGoSearchRun(api_wrapper=duckduckgo_wrapper)

            search_agent = create_agent(
                model = Config.rag_model,
                tools=[arxiv_tool,duckduckgo_tool],
                system_prompt="You're a web search Agent. " \
                "Get context from the tools and return info for the User Query." \
                "prefix your response with FINAL ANSWER so the team knows to stop." 
            )
            # return search_agent
        except Exception as e:
            get_logger("SearchAgent").error("Error during RAG Agent creation: %s", str(e))
            raise CustomException("Failed to build RAG Agent", e)
        
        return search_agent