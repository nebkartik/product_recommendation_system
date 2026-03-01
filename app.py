from flask import Flask, render_template, request, Response, jsonify
from prometheus_client import Counter, generate_latest
import uuid
from utils.logger import get_logger
from utils.custom_exception import CustomException
from workflow.graph import GraphInstance
from langchain_core.messages import HumanMessage
from flipkart.guardrails import GuardRails


REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
PREDICTION_COUNT = Counter("http_predictions_total", "Total Model Predictions")

def create_app():
    app = Flask(__name__,template_folder="frontend/templates", static_folder="frontend/static")
    THREAD_ID = str(uuid.uuid4())  
    get_logger("App").info("Flask app created with unique thread ID: %s", THREAD_ID)

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
            
            graph = GraphInstance().workflow()
            response = graph.invoke({"messages": [HumanMessage(content=user_input)]})
            raw_content = response["messages"][-1].content
            final_content = GuardRails().validate_response(raw_content)
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
            return final_content
    
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