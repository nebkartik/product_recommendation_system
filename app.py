from urllib import response
from langchain import messages

from flask import Flask, render_template, request, Response, jsonify
from prometheus_client import Counter, generate_latest
import uuid
from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
PREDICTION_COUNT = Counter("http_predictions_total", "Total Model Predictions")

def create_app():
    app = Flask(__name__,template_folder="frontend/templates", static_folder="frontend/static")
    THREAD_ID = str(uuid.uuid4())  
    print(f"[INFO] New chat thread created: {THREAD_ID}")

    vector_db = DataIngestor().ingest(load_existing=True)
    rag_agent = RAGAgentBuilder(vector_db).build_agent()

    @app.route("/")
    def index():
        REQUEST_COUNT.inc()
        return render_template("index.html")
    
    @app.route("/get", methods=["POST"])
    def get_response():
         user_input = request.form["msg"]
         response = rag_agent.invoke(
                {  
                   "messages" : [
                        {
                    "role": "user",
                    "content": user_input
                        }
                    ]
                }
                 ,
                    config={
                        "configurable": {
                            "thread_id": THREAD_ID
                        }
                     }
             
             )
         PREDICTION_COUNT.inc()

         messages = response.get("messages") if isinstance(response, dict) else None
         if not messages:
            return jsonify({"response": "Sorry, I couldn't find an answer. Please contact our customer care at +97 98652365."})

         last = messages[-1]
         if isinstance(last, dict):
            content_text = last.get("content", "") or ""
         elif hasattr(last, "content"):
            content_text = getattr(last, "content") or ""
         elif hasattr(last, "text"):
            content_text = getattr(last, "text") or ""
         else:
            content_text = str(last)
        #  content = last.get("content") if isinstance(last, dict) else last
         print("Content to return:", content_text)
        #  return jsonify({"response": content}) 
         return content_text  
        #  return jsonify({"response": content_text})     

        # ensure JSON serializable
        #  try:
        #     print("[DEBUG] Response content is serializable")
        #     return jsonify({"response": content})
        #  except TypeError:
        #     print("[ERROR] Response content is not JSON serializable:")
        #     return jsonify({"response": str(content)})
            
      
      
        #  if not response.get("messages"):
        #        return jsonify({"response": "Sorry, I couldn't find an answer. Please contact our customer care at +97 98652365."})
        
        #  return jsonify({"response": response["messages"][-1]["content"]}) 
    
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