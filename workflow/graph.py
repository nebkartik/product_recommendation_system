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

class GraphInstance:
        def __init__(self):
            get_logger("Graph").info("Inside Constructor")
            self.vector_db = DataIngestor().ingest(load_existing=True)
            self.rag_agent = RAGAgentBuilder(self.vector_db).build_agent()
                

        def get_next_node(self, last_msg: BaseMessage, goto: str):
            if last_msg.content:
                return END
            return goto

        def rag_node(self, state: MessagesState) -> Command[Literal["search_agent", END]]:
            get_logger("Graph").info("Rag Node")
            result = self.rag_agent.invoke(state)
            goto = self.get_next_node(result["messages"][-1], "search_agent")
            result["messages"][-1] = HumanMessage(
                content=result["messages"][-1].content, name="rag_agent"
            )
            return Command(update={"messages": result["messages"]}, goto=goto)

        def search_node(self, state: MessagesState) -> Command[Literal["rag_agent", END]]:
            get_logger("Graph").info("Search Node")
            search_agent = SearchAgent.build_agent()
            result = search_agent.invoke(state)
            goto = self.get_next_node(result["messages"][-1], "rag_agent")
            result["messages"][-1] = HumanMessage(
                content=result["messages"][-1].content, name="search_agent"
            )
            return Command(update={"messages": result["messages"]}, goto=goto)

        def workflow(self):
            get_logger("Graph").info("Inside Workflow")
            workflow = StateGraph(MessagesState)
            workflow.add_node("rag_agent", self.rag_node)
            workflow.add_node("search_agent", self.search_node)
            workflow.add_edge(START, "rag_agent")
            graph = workflow.compile()
            return graph