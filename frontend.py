import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DEFAULT_API_KEY = os.getenv("GOOGLE_API_KEY")
API_ENDPOINT = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/qa")

st.set_page_config(page_title="🛫 Changi & Jewel Chatbot", layout="wide")
st.title("🛫 Changi & Jewel Airport RAG Chatbot")
st.markdown("Ask anything about Changi Airport or Jewel Changi. Powered by a RAG system and Gemini LLM.")

user_query = st.text_input("💬 Ask your question:", placeholder="E.g. What are the dining options?")
user_api_key = st.text_input("🔑 Optional: Paste your Gemini API key", value="", type="password")
ask_button = st.button("Ask")

final_api_key = user_api_key.strip() or DEFAULT_API_KEY

if ask_button:
    if not user_query.strip():
        st.warning("❗ Please enter a valid question.")
    elif not final_api_key:
        st.warning("❗ No API key found. Please paste your Gemini key.")
    else:
        with st.spinner("🤖 Thinking..."):
            try:
                res = requests.post(
                    API_ENDPOINT,
                    json={"user_query": user_query, "api_key": final_api_key},
                    timeout=30
                )

                if res.status_code == 200:
                    result = res.json()
                    st.success("✅ Answer:")
                    st.write(result.get("answer", "No answer returned."))
                    sources = result.get("sources", [])
                    if sources:
                        st.markdown("### 📌 Sources:")
                        for src in sources:
                            st.markdown(f"- [{src}]({src})")
                else:
                    detail = res.json().get("detail", "Unknown error.")
                    if "quota" in detail.lower():
                        st.error("🚫 Gemini quota exceeded. Please try again later or use your own API key.")
                    else:
                        st.error(f"❌ {res.status_code} - {detail}")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request failed: {e}")
            except Exception as e:
                st.error(f"🚨 Unexpected error: {str(e)}")
