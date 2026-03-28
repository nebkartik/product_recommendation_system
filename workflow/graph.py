from langgraph.graph import StateGraph
from utils.logger import get_logger
from typing import Literal
# Agent to Agent Communication
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import MessagesState, END, START
from langgraph.types import Command
from flipkart.rag_agent import RAGAgentBuilder
from flipkart.web_search_agent import SearchAgent
from flipkart.data_ingestion import DataIngestor
import uuid




class GraphInstance:
        def __init__(self):
            get_logger("Graph").info("Inside Constructor")
            self.vector_db = DataIngestor().ingest(load_existing=True)
            self.rag_agent = RAGAgentBuilder(self.vector_db).build_agent()
            self.thread_id = str(uuid.uuid4())
                

        def get_next_node(self, last_msg: BaseMessage, goto: str):
            if last_msg.content:
                return END
            return goto

        def rag_node(self, state: MessagesState) -> Command[Literal["search_agent", END]]:
            # get_logger("Graph").info("Rag Node with State: ",type(state), state)
            # get_logger("Graph").info(f"Rag Node with State Type: {type(state)}")
            # result = self.rag_agent.invoke(state)
            if isinstance(state, dict) and "messages" in state:
                user_text = state["messages"][-1].content
            else:
                user_text = str(state)    

            result = self.rag_agent.invoke(
                    {  
                    "messages" : [
                            {
                        "role": "user",
                        "content": user_text
                            }
                        ]
                    }
                    ,
                        config={
                            "configurable": {
                                "thread_id": self.thread_id
                            }
                        }
                )
            # get_logger("Graph").info("Res",result, "Type",type(result)) 
            last_message = result["messages"][-1]

            if hasattr(last_message, 'content'):
                content_str = last_message.content
            elif isinstance(last_message, dict):
            # Fallback if the agent returned a plain dict instead of a message object
                content_str = last_message.get('content', str(last_message))
            else:
                content_str = str(last_message)

            # get_logger("Graph").info("Agent Response", content_str)
            # goto = self.get_next_node(content_str, "search_agent")
            # result["messages"][-1] = HumanMessage(
            #     content=content_str, name="rag_agent"
            # )
            return Command(update={"messages": content_str}, goto=END)

        def search_node(self, state: MessagesState) -> Command[Literal["rag_agent", END]]:
            get_logger("Graph").info("Search Node")
            search_agent = SearchAgent.build_agent()
            result = search_agent.invoke(state)
            goto = self.get_next_node(result["messages"][-1], "rag_agent")
            result["messages"][-1] = HumanMessage(
                content=result["messages"][-1].content, name="search_agent"
            )
            return Command(update={"messages": result["messages"]}, goto=goto)
        

        
        # def validate_response_with_llm(query: str, context: str, answer: str):
        #     """
        #     Use LLM-as-a-Judge to evaluate groundedness and relevance.
        #     """
        #     judge_model = init_chat_model("gpt-4")  # or whichever model you prefer

        #     prompt = f"""
        #     You are an evaluator. Given the user query, retrieved context, and the answer:

        #     Query: {query}
        #     Context: {context}
        #     Answer: {answer}

        #     Evaluate the following metrics on a scale of 1 (poor) to 5 (excellent):

        #     1. Groundedness: Is the answer supported by the provided context?
        #     2. Relevance: Is the answer relevant to the query?

        #     Return your evaluation as JSON with keys 'groundedness' and 'relevance'.
        #     """

        #     result = judge_model.invoke(prompt)
        #     get_logger("RAGAgent").info("Validation Result: %s", result.content)

            return result.content

        def workflow(self):
            get_logger("Graph").info("Inside Workflow")
            workflow = StateGraph(MessagesState)
            workflow.add_node("rag_agent", self.rag_node)
            workflow.add_node("search_agent", self.search_node)
            workflow.add_edge(START, "rag_agent")
            graph = workflow.compile()
            return graph