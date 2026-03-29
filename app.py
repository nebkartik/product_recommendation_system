from flask import Flask, render_template, request, Response, jsonify
from prometheus_client import Counter, generate_latest
import uuid
from utils.logger import get_logger
from utils.custom_exception import CustomException
from workflow.graph import GraphInstance
from langchain_core.messages import HumanMessage
from flipkart.guardrails import GuardRails
from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_astradb import AstraDBSemanticCache
from langchain_core.globals import set_llm_cache
from flask import session


REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
PREDICTION_COUNT = Counter("http_predictions_total", "Total Model Predictions")

def create_app():
    app = Flask(__name__,template_folder="frontend/templates", static_folder="frontend/static")
    app.secret_key = 'ChatbotSecretKey'  # Replace with a secure key in production
    thread_cache = {}
    graph = GraphInstance().workflow()      

    # Initialize these once to keep connections warm
    # embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
    # semantic_cache = AstraDBSemanticCache(
    #     collection_name="rag_app_cache",
    #     api_endpoint=Config.astra_db_api_endpoint,
    #     token=Config.astra_db_token,
    #     embedding=embeddings
    # )
    # set_llm_cache(semantic_cache)

    @app.route("/")
    def index():
        REQUEST_COUNT.inc()
        return render_template("index.html")
    
    
    @app.route("/get", methods=["POST"])
    def get_response():
         try:
            if 'thread_id' not in session:
                session['thread_id'] = str(uuid.uuid4())
            thread_id = session['thread_id']            

            get_logger("App").info("Flask app created with unique thread ID:", thread_id)  

            user_input = request.form["msg"]
            get_logger("App").info("Received user input: ", user_input)


            # Thread Cache
            # if thread_id in thread_cache and user_input in thread_cache[thread_id]:
            #     get_logger("App").info("Thread Cache Hit", thread_id)
            #     # return jsonify({"content": thread_cache[thread_id][user_input]})
            #     return thread_cache[thread_id][user_input]


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
                
            #     
            # cache_resp = semantic_cache.lookup(user_input,llm_string=Config.rag_model)
            # get_logger("App").info("Cache: %s",cache_resp)
            # if cache_resp:
            #     get_logger("App").info("Cache Response Received",cache_resp)


            config = {"configurable": {"thread_id":thread_id}}
            response = graph.invoke({"messages": [HumanMessage(content=user_input)]},config=config)
          
            # get_logger("App").info("Graph Message",HumanMessage(content=user_input))

            last_message = response["messages"][-1]
            if hasattr(last_message, 'content'):
                content_str = last_message.content
            elif isinstance(content_str, dict):
             content_str = content_str.get('content', str(content_str))
            else:
                content_str = str(content_str)

            get_logger("App").info("LLM Response: ", content_str)
            # final_content = GuardRails().validate_response(content_str)
            PREDICTION_COUNT.inc()
            
            # if thread_id not in thread_cache:
            #     thread_cache[thread_id] = {}

            # if len(thread_cache[thread_id]) > 20:
            #      thread_cache[thread_id].pop(next(iter(thread_cache[thread_id]))) 

            # thread_cache[thread_id][user_input] = final_content

            # print("Thread Cache", thread_cache)
            return content_str
         except Exception as e:
            get_logger("App").error("Error generating response: %s", str(e))
            raise CustomException("Failed to generate response", e)
         
        #  get_logger("App").info("Final response to user: %s", content_text)
        #  return content_text  

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