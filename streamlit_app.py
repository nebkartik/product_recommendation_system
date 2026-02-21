import streamlit as st
import uuid
from datetime import datetime

from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder


st.set_page_config(page_title="Flipkart Chatbot", layout="centered")


@st.cache_resource
def get_agent():
    vector_db = DataIngestor().ingest(load_existing=True)
    return RAGAgentBuilder(vector_db).build_agent()


def format_message(role: str, content: str) -> str:
    time = datetime.now().strftime("%H:%M")
    if role == "user":
        return f"**You** ({time}): {content}"
    return f"**Bot** ({time}): {content}"


def extract_text_from_message(msg) -> str:
    if isinstance(msg, dict):
        return msg.get("content") or msg.get("text") or ""
    if hasattr(msg, "content"):
        return getattr(msg, "content") or ""
    if hasattr(msg, "text"):
        return getattr(msg, "text") or ""
    return str(msg)


def main():
    st.title("Flipkart Chatbot")
    st.write("Ask product-related questions based on reviews and titles.")

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []

    agent = get_agent()

    with st.form(key="input_form", clear_on_submit=True):
        user_input = st.text_input("Your message", value="", key="input")
        submit = st.form_submit_button("Send")

    if submit and user_input:
        st.session_state.messages.append(("user", user_input))
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config={"configurable": {"thread_id": st.session_state.thread_id}},
            )
        except Exception as e:
            st.error(f"Agent error: {e}")
            return

        # Extract messages from agent response
        messages = response.get("messages") if isinstance(response, dict) else None
        if not messages:
            bot_text = "Sorry, I couldn't find an answer. Please contact customer care."
        else:
            last = messages[-1]
            bot_text = extract_text_from_message(last)

        st.session_state.messages.append(("bot", bot_text))

    # Display chat
    for role, text in st.session_state.get("messages", []):
        if role == "user":
            st.markdown(f"<div style='text-align:right'>{format_message(role, text)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left'>{format_message(role, text)}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()