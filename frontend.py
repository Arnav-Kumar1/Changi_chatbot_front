# # streamlit_app.py
# import os
# import requests
# import streamlit as st
# from dotenv import load_dotenv

# # --- Load environment variables ---
# load_dotenv()
# API_KEY = os.getenv("GOOGLE_API_KEY")
# API_ENDPOINT = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/qa")

# st.set_page_config(page_title="🛫 Changi & Jewel Chatbot", layout="wide")
# st.title("🛫 Changi & Jewel Airport RAG Chatbot")
# st.markdown("Ask anything about Changi or Jewel websites using a RAG-powered assistant.")

# # Use the loaded API_KEY directly
# user_api_key = API_KEY

# # --- User Query ---
# user_query = st.text_input("💬 What would you like to know?")
# ask_button = st.button("Ask")

# # --- Query the RAG API ---
# if ask_button:
#     if not user_query.strip():
#         st.warning("❗ Please enter a question.")
#     else:
#         with st.spinner("🤖 Generating answer..."):
#             try:
#                 res = requests.post(
#                     API_ENDPOINT,
#                     json={"user_query": user_query, "api_key": user_api_key},
#                     timeout=45
#                 )

#                 if res.status_code == 200:
#                     result = res.json()
#                     st.success("✅ Answer:")
#                     st.write(result.get("answer", "No answer returned."))

#                     sources = result.get("sources", [])
#                     if sources:
#                         st.markdown("### 📎 Sources:")
#                         for url in sources:
#                             st.markdown(f"- [{url}]({url})")
#                     else:
#                         st.info("ℹ️ No sources provided.")
#                 else:
#                     st.error(f"❌ {res.status_code} - {res.text}")

#             except requests.exceptions.Timeout:
#                 st.error("⏱️ Request timed out. Try again later.")
#             except Exception as e:
#                 st.error(f"🚨 Unexpected error: {str(e)}")
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
DEFAULT_API_KEY = os.getenv("GOOGLE_API_KEY")
API_ENDPOINT = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/qa")

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="🛫 Changi & Jewel Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Navigation Sidebar ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "ℹ️ About", "⚙️ How it Works", "📬 Contact"])

# --- Reusable Styling ---
def separator():
    st.markdown("---")

def show_sources(sources):
    if sources:
        st.markdown("### 📎 Sources")
        for url in sources:
            st.markdown(f"- [{url}]({url})")
    else:
        st.info("ℹ️ No sources provided.")

# --- Home Page: Main Chat UI ---
if page == "🏠 Home":
    st.title("🛫 Changi & Jewel Airport RAG Chatbot")
    st.markdown("Ask anything about **Changi Airport** or **Jewel Changi** websites using a RAG-powered assistant.")
    separator()

    col1, col2 = st.columns([3, 2])
    with col1:
        user_query = st.text_input("💬 Enter your question", placeholder="E.g. What are the opening hours of Jewel?")
        ask_button = st.button("Ask", use_container_width=True)

    with col2:
        st.markdown("#### 🔑 Google API Key")
        user_api_key = st.text_input("Paste your API key here", value=DEFAULT_API_KEY or "", type="password")

    if ask_button:
        if not user_query.strip():
            st.warning("❗ Please enter a question.")
        elif not user_api_key.strip():
            st.warning("❗ Please provide a valid API key.")
        else:
            with st.spinner("🤖 Generating answer..."):
                try:
                    res = requests.post(
                        API_ENDPOINT,
                        json={"user_query": user_query, "api_key": user_api_key},
                        timeout=45
                    )

                    if res.status_code == 200:
                        result = res.json()
                        st.success("✅ Answer:")
                        st.write(result.get("answer", "No answer returned."))
                        show_sources(result.get("sources", []))

                    elif res.status_code in [403, 429, 500]:
                        st.error("🚫 API quota may have been exceeded.")
                        st.info(
                            "🔁 Please wait a few minutes and try again.\n\n"
                            "If you have another API key, paste it above and retry."
                        )
                    else:
                        st.error(f"❌ {res.status_code} - {res.text}")

                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Try again later.")
                except Exception as e:
                    st.error(f"🚨 Unexpected error: {str(e)}")

# --- About Page ---
elif page == "ℹ️ About":
    st.title("ℹ️ About this App")
    st.markdown("""
This chatbot helps you find information from the official websites of:

- **Changi Airport** 🛫  
- **Jewel Changi Airport** 🛍️

It uses a powerful **RAG (Retrieval-Augmented Generation)** backend to:
- Search the website content
- Summarize relevant sections
- Provide source links

Built with:
- LangChain + Google Gemini LLM
- FastAPI backend
- Streamlit frontend
""")
    st.markdown("""
> ⚠️ **Note:** API quota may sometimes be exceeded due to limits on free-tier Google API keys.  
> In such cases, wait a few minutes and try again. You can also use another API key.
""")

# --- How it Works Page ---
elif page == "⚙️ How it Works":
    st.title("⚙️ How it Works")
    st.markdown("""
Here's how the chatbot functions behind the scenes:

1. **User submits a query**  
   👉 You ask a question using the chat UI

2. **Hybrid Retrieval System**  
   🔍 The backend searches documents using:
   - Dense embeddings (semantic search)
   - Sparse TF-IDF retrieval
   - Reranking + deduplication

3. **Context assembly**  
   🧠 Top relevant snippets are gathered as context

4. **Gemini LLM Response**  
   💬 The context is passed into the Google Gemini LLM to generate a final answer

5. **Sources Returned**  
   📎 Source URLs are displayed for transparency
""")

# --- Contact Page ---
elif page == "📬 Contact":
    st.title("📬 Contact")
    st.markdown("""
For support, suggestions, or questions:

- 📧 Email: arnav9637@gmail.com 
- 🧠 GitHub: https://github.com/Arnav-Kumar1/Changi_chatbot
""")
