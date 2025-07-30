import os
import requests
import streamlit as st
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
DEFAULT_API_KEY = os.getenv("GOOGLE_API_KEY")
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
API_ENDPOINT = BACKEND_URL  # Already points to full /api/qa
HEALTHCHECK_ENDPOINT = BACKEND_URL.replace("/qa", "/healthcheck")

GOOGLE_API_LINK = "https://aistudio.google.com/app/apikey"

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="🛫 Changi & Jewel Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session state init ---
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "checking"
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = None

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

# --- Health check function ---
def call_healthcheck(key=None):
    try:
        res = requests.post(
            HEALTHCHECK_ENDPOINT,
            json={"api_key": key},
            timeout=15
        )
        return res.json()["status"]
    except requests.exceptions.Timeout:
        return "timeout"
    except requests.exceptions.RequestException:
        return "backend_unavailable"
    except Exception:
        return "error"

# --- Home Page ---
if page == "🏠 Home":
    st.title("🛫 Changi & Jewel Airport RAG Chatbot")
    st.markdown("Ask anything about **Changi Airport** or **Jewel Changi** websites using a RAG-powered assistant.")
    separator()

    # --- Run backend health check on first load ---
    if st.session_state.backend_status == "checking":
        with st.spinner("🔌 Connecting to backend and validating Gemini API access..."):
            st.session_state.backend_status = call_healthcheck()

    # --- Handle health check outcomes ---
    if st.session_state.backend_status in ["backend_unavailable", "timeout"]:
        st.error("❌ Backend is unavailable or asleep.")
        st.info("⏳ Please wait 30–60 seconds and click Retry.")
        if st.button("🔁 Retry"):
            st.session_state.backend_status = "checking"
            st.experimental_rerun()
        st.stop()

    elif st.session_state.backend_status in ["quota_exceeded", "invalid_key"]:
        st.warning("🚫 Default Gemini API key quota exceeded or is invalid.")
        st.markdown(f"👉 [Click here to get your own API key]({GOOGLE_API_LINK})")
        st.session_state.gemini_key = st.text_input("🔑 Paste your Gemini API key below", type="password")
        if st.button("✅ Validate Key"):
            with st.spinner("🔍 Validating your API key..."):
                result = call_healthcheck(st.session_state.gemini_key)
                if result == "ok":
                    st.success("✅ Your key is valid! You may now proceed.")
                    st.session_state.backend_status = "ok"
                    st.experimental_rerun()
                else:
                    st.session_state.backend_status = result
                    st.error("❌ That key didn’t work. Please try again.")
        st.stop()

    # --- Main Chat UI (if backend_status == "ok") ---
    col1, col2 = st.columns([3, 2])
    with col1:
        user_query = st.text_input("💬 Enter your question", placeholder="E.g. How to get to the Jewel airport?")
        ask_button = st.button("Ask", use_container_width=True)

    with col2:
        st.markdown("#### 🔑 Gemini API Key")
        st.markdown("Using your key if provided.")

    user_api_key = st.session_state.get("gemini_key") or DEFAULT_API_KEY

    if ask_button:
        if not user_query.strip():
            st.warning("❗ Please enter a question.")
        elif not user_api_key:
            st.warning("❗ No API key available. Please paste a valid key.")
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
                        st.error("🚫 Your API key may be invalid or has exceeded usage limits.")
                        st.info(f"🔗 [Get your key here]({GOOGLE_API_LINK})")
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

- 📧 Email: [arnav@example.com](mailto:arnav@example.com)  
- 🧠 GitHub: [github.com/arnav-ai](https://github.com/arnav-ai)  
- 📝 Report a bug: [GitHub Issues](https://github.com/arnav-ai/changi-chatbot/issues)
""")
