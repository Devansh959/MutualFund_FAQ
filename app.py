import streamlit as st
import requests
import uuid

import os

# Configuration
# Default to local for development, override with env var for deployment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
API_URL = f"{BACKEND_URL}/ask"

st.set_page_config(
    page_title="MF FAQ Assistant",
    page_icon="💰",
    layout="centered"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #ff4b4b;
        font-weight: bold;
        border: 1px solid #ff4b4b;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State for Multi-Threading
if "threads" not in st.session_state:
    # Each thread: {"id": str, "name": str, "messages": list}
    initial_thread_id = str(uuid.uuid4())
    st.session_state.threads = {
        initial_thread_id: {
            "name": "Chat 1",
            "messages": []
        }
    }
    st.session_state.current_thread_id = initial_thread_id

# Helper to get current thread data
def get_current_thread():
    return st.session_state.threads[st.session_state.current_thread_id]

# Sidebar for Thread Management
with st.sidebar:
    st.title("💬 Chat Sessions")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        thread_count = len(st.session_state.threads) + 1
        st.session_state.threads[new_id] = {
            "name": f"Chat {thread_count}",
            "messages": []
        }
        st.session_state.current_thread_id = new_id
        st.rerun()

    st.markdown("---")
    
    # Thread Selector
    for tid, tdata in st.session_state.threads.items():
        is_current = (tid == st.session_state.current_thread_id)
        btn_label = f"{'🟢' if is_current else '⚪'} {tdata['name']}"
        if st.button(btn_label, key=tid, use_container_width=True):
            st.session_state.current_thread_id = tid
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.markdown('<div class="disclaimer">Facts-only. No investment advice. This assistant provides objective data from official sources only.</div>', unsafe_allow_html=True)
    
    st.markdown("### Example Questions")
    examples = [
        "What is the exit load for HDFC Mid Cap Fund?",
        "Minimum SIP amount for HDFC Flexi Cap?",
        "What is the expense ratio of HDFC Small Cap Fund?"
    ]
    for q in examples:
        if st.button(q, key=f"ex_{q}"):
            st.session_state.input_query = q

    if st.button("🗑️ Clear All Sessions", use_container_width=True):
        st.session_state.threads = {}
        initial_thread_id = str(uuid.uuid4())
        st.session_state.threads[initial_thread_id] = {
            "name": "Chat 1",
            "messages": []
        }
        st.session_state.current_thread_id = initial_thread_id
        st.rerun()

st.title("💰 Mutual Fund FAQ Assistant")
st.caption(f"Active Session: {get_current_thread()['name']} | Verified factual information.")

# Display Chat History for CURRENT Thread
current_thread = get_current_thread()
for message in current_thread["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "source" in message and message["source"] != "N/A":
            st.caption(f"Source: [Groww Official]({message['source']}) | Updated: {message.get('updated', 'Recently')}")

# Chat Input
query = st.chat_input("Ask a question about HDFC Mutual Funds...")
if hasattr(st.session_state, "input_query"):
    query = st.session_state.input_query
    del st.session_state.input_query

if query:
    # Add user message to current thread
    current_thread["messages"].append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Call API with current_thread_id
    with st.chat_message("assistant"):
        with st.spinner("Retrieving factual data..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"query": query, "thread_id": st.session_state.current_thread_id}
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    source = data["source_link"]
                    updated = data["last_updated"]
                    
                    st.markdown(answer)
                    if source != "N/A":
                        st.caption(f"Source: [Official Portal]({source}) | Updated: {updated}")
                    
                    # Store assistant message in current thread
                    current_thread["messages"].append({
                        "role": "assistant", 
                        "content": answer, 
                        "source": source,
                        "updated": updated
                    })
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Connection Error: Is the FastAPI server running at {API_URL}?")

