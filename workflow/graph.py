from langgraph.graph import StateGraph
from workflow.state import ConversationState
from utils.logger import get_logger
from typing import Literal
# Agent to Agent Communication
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import MessagesState, END, START
from langgraph.types import Command
from flipkart.rag_agent import RAGAgentBuilder
from flipkart.web_search_agent import SearchAgent
from flipkart.data_ingestion import DataIngestor
# def create_workflow(rag_agent, recommendation_agent):

    # get_logger("Graph").info("Inside Workflow")
    # """Build a multi-agent workflow."""
    
    # graph = StateGraph(ConversationState)
    
    # # Define nodes
    # # def route_to_agent(state: ConversationState):
    # def route_to_agent(state: ConversationState):
    #     """Decide which agent to call based on intent."""
    #     get_logger("Graph").info("User Input",state)
    #     user_input = state["messages"]
    #     get_logger("Graph").info("User Input",user_input)
    #     if "recommend" in user_input.lower():
    #         return recommendation_agent.invoke(
    #             user_input, 
    #             state["thread_id"]
    #         )
    #     else:
    #         get_logger("Graph").info("Rag Pipeline")
    #         return rag_agent.invoke(
    #             user_input, 
    #             state["thread_id"]
    #         )
    
    # graph.add_node("route", route_to_agent)
    # graph.set_entry_point("route")
    # graph.set_finish_point("route")
    
    # return graph.compile()


vector_db = DataIngestor().ingest(load_existing=True)
rag_agent = RAGAgentBuilder(vector_db).build_agent()


# RAG Node

def rag_node(state:MessagesState) -> Command[Literal["search_agent", END]]:
    print("Rag Node")
    result = rag_agent.invoke(state)
    goto = get_next_node(result["messages"][-1],"search_agent")
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="rag_agent"
    )
    return Command(
        update= {
            "messages": result["messages"]
        },
        goto=goto
    )


def get_next_node(last_msg:BaseMessage,goto:str):
    if last_msg.content:
        return END
    return goto


# Web Search Node
def search_node(state:MessagesState) -> Command[Literal["rag_agent", END]]:
    print("Search Node")
    search_agent = SearchAgent.build_agent()
    result = search_agent.invoke(state)
    goto = get_next_node(result["messages"][-1],"rag_agent")
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="search_agent"
    )
    return Command(
        update= {
            "messages": result["messages"]
        },
        goto=goto
    )


# Workflow
def workflow():
    get_logger("Graph").info("Inside Workflow")
    workflow = StateGraph(MessagesState)

    workflow.add_node("rag_agent",rag_node)
    workflow.add_node("search_agent",search_node)
    workflow.add_edge(START,"search_agent")

    graph = workflow.compile()
    return graph