import streamlit as st
import requests

st.set_page_config(
    page_title="LLM Guardrails Gateway",
    page_icon="🛡️",
    layout="centered"
)

API_URL = "http://127.0.0.1:8000/chat"

st.title("🛡️ LLM Guardrails Gateway")
st.caption("A safety middleware layer that sits between users and any LLM — blocking jailbreaks, PII leaks, and policy violations before they reach the model.")

with st.sidebar:
    st.header("📋 Active Policy Rules")
    st.markdown("""
    **Blocked Topics:**
    - Medical advice
    - Legal advice
    - Competitor names
    - Financial investment advice

    **Input Protections:**
    - Jailbreak / prompt injection detection
    - PII leakage detection (email, phone, etc.)
    - Max input length: 2000 chars

    **Output Protections:**
    - Topic compliance check
    - Auto disclaimer on sensitive topics
    """)
    st.divider()
    st.caption("Built with FastAPI + Groq (Llama 3.3) + Presidio")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Checking guardrails and generating response..."):
            try:
                res = requests.post(API_URL, json={"user_input": user_input})
                data = res.json()

                if data["success"]:
                    st.markdown(data["response"])
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": data["response"]}
                    )

                    if data.get("flagged_issues"):
                        st.warning(f"⚠️ Note: {', '.join(data['flagged_issues'])}")

                else:
                    blocked_msg = f"🚫 **Request blocked.**\n\n**Reason:** {data['blocked_reason']}\n\n**Details:** {', '.join(data['flagged_issues'])}"
                    st.error(blocked_msg)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": blocked_msg}
                    )

            except Exception as e:
                error_msg = f"Could not connect to the backend server. Make sure it's running.\n\nError: {str(e)}"
                st.error(error_msg)