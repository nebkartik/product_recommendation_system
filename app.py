from flask import Flask, render_template, request, Response, jsonify
from prometheus_client import Counter, generate_latest
import uuid
from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder
from utils.logger import get_logger
from utils.custom_exception import CustomException
from workflow.graph import workflow
from flipkart.web_search_agent import SearchAgent
from langchain_core.messages import HumanMessage
from langchain_core.messages import HumanMessage


REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
PREDICTION_COUNT = Counter("http_predictions_total", "Total Model Predictions")

def create_app():
    app = Flask(__name__,template_folder="frontend/templates", static_folder="frontend/static")
    THREAD_ID = str(uuid.uuid4())  
    get_logger("App").info("Flask app created with unique thread ID: %s", THREAD_ID)

    # vector_db = DataIngestor().ingest(load_existing=True)
    # rag_agent = RAGAgentBuilder(vector_db)
    # # search_agent = SearchAgent.agent_tools()

    get_logger("App").info("RAG Agent initialized with vector store.")

    # Helper function to extract text from agent response
    # def generate_response(last):
    #     if isinstance(last, dict):
    #         content = last.get("content", "") or ""
    #     elif hasattr(last, "content"):
    #         content = getattr(last, "content") or ""
    #     elif hasattr(last, "text"):
    #         content = getattr(last, "text") or ""
    #     else:
    #         content = str(last)

    #     return content



    @app.route("/")
    def index():
        REQUEST_COUNT.inc()
        return render_template("index.html")
    
    @app.route("/get", methods=["POST"])
    def get_response():
         try:
            user_input = request.form["msg"]
            # response = rag_agent.invoke(
            #         {  
            #         "messages" : [
            #                 {
            #             "role": "user",
            #             "content": user_input
            #                 }
            #             ]
            #         }
            #         ,
            #             config={
            #                 "configurable": {
            #                     "thread_id": THREAD_ID
            #                 }
            #             }
                
            #     )
            # workflow = create_workflow(rag_agent=rag_agent,recommendation_agent=search_agent)
            # response = workflow.invoke(user_input)
            graph = workflow()
            response = graph.invoke({"messages": [HumanMessage(content=user_input)]})
            PREDICTION_COUNT.inc()

            get_logger("App").info("Received user input: %s", user_input)

        # #     messages = response.get("messages") if isinstance(response, dict) else None
        # #     if not messages:
        # #         return jsonify({"response": "Sorry, I couldn't find an answer. Please contact our customer care at +97 98652365."})

        # #     last = messages[-1]
        # #     content_text = generate_response(last)
        # #  except Exception as e:
        # #     get_logger("App").error("Error generating response: %s", str(e))
        # #     raise CustomException("Failed to generate response", e)
         
        #  get_logger("App").info("Final response to user: %s", content_text)
        #  return content_text  
            return response["messages"][-1].content
    
         except Exception as e:
                get_logger("App").error("Error generating response: %s", str(e))
                raise CustomException("Failed to generate response", e)
       
 

    @app.route("/metrics")
    def metrics():
         return Response(generate_latest(), mimetype="text/plain")
    
    @app.route("/health")
    def health():
         return jsonify({"status": "healthy"}), 200
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000,debug=True)