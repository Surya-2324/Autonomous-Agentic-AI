import re
import uuid
import logging

import streamlit as st
from main import app

logger = logging.getLogger(__name__)

MAX_INPUT_LENGTH = 500
INPUT_PATTERN = re.compile(r"^[\w\s.,;:!?'\"-]+$")

st.set_page_config(page_title="Agentic Compliance Auditor", layout="centered")

st.title("🏦 Real-Time Agentic Auditor")
st.write("Enter a topic below to perform live research and compliance auditing.")

if "config" not in st.session_state:
    thread_id = str(uuid.uuid4())
    st.session_state.config = {"configurable": {"thread_id": thread_id}}

user_topic = st.text_input(
    "What would you like to analyze?",
    "Impact of US interest rates on tech stocks",
    max_chars=MAX_INPUT_LENGTH,
)

if st.button("Run Analysis"):
    if not user_topic or not user_topic.strip():
        st.error("Please enter a topic to analyze.")
    elif len(user_topic) > MAX_INPUT_LENGTH:
        st.error(f"Input too long. Maximum {MAX_INPUT_LENGTH} characters allowed.")
    elif not INPUT_PATTERN.match(user_topic):
        st.error("Input contains disallowed characters. Please use only letters, numbers, and basic punctuation.")
    else:
        sanitized_topic = user_topic.strip()
        try:
            with st.spinner(f"Searching live news for: {sanitized_topic}..."):
                dynamic_state = {
                    "search_topic": sanitized_topic,
                    "macro_data": "",
                    "proposed_strategy": "",
                    "audit_result": "",
                    "decision_log": [],
                }

                app.invoke(dynamic_state, config=st.session_state.config)

                snapshot = app.get_state(st.session_state.config)
                strategy = snapshot.values.get("proposed_strategy")
                st.session_state.strategy = strategy
                st.success("Analysis Complete!")
        except Exception:
            logger.exception("Analysis pipeline failed")
            st.error("An error occurred during analysis. Please try again later.")

if "strategy" in st.session_state:
    st.subheader("Proposed Investment Strategy")
    st.info(st.session_state.strategy)

    col1, col2 = st.columns(2)
    if col1.button("Approve Strategy"):
        try:
            with st.spinner("Auditing and calculating confidence score..."):
                for event in app.stream(None, config=st.session_state.config):
                    if "auditor_agent" in event:
                        st.subheader("Audit & Confidence Report")
                        st.write(event["auditor_agent"]["audit_result"])
        except Exception:
            logger.exception("Audit pipeline failed")
            st.error("An error occurred during auditing. Please try again later.")

    if col2.button("Reject Strategy"):
        st.warning("Strategy Rejected.")
