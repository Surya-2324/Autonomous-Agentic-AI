import logging

import streamlit as st
from main import app

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Agentic Compliance Auditor", layout="centered")

st.title("🏦 Real-Time Agentic Auditor")
st.write("Enter a topic below to perform live research and compliance auditing.")

# Initialize session state for LangGraph config
if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "user_session_1"}}

# 1. Capture user input for real-time analysis
user_topic = st.text_input("What would you like to analyze?", "Impact of US interest rates on tech stocks")

# Run the Agent
if st.button("Run Analysis"):
    if user_topic:
        with st.spinner(f"Searching live news for: {user_topic}..."):
            dynamic_state = {
                "search_topic": user_topic,
                "macro_data": "",
                "proposed_strategy": "",
                "audit_result": "",
                "decision_log": []
            }

            try:
                app.invoke(dynamic_state, config=st.session_state.config)
            except Exception as exc:
                logger.error("Agent graph failed during analysis: %s", exc)
                st.error(f"Analysis failed: {exc}")
                st.stop()

            snapshot = app.get_state(st.session_state.config)
            strategy = snapshot.values.get("proposed_strategy")
            if not strategy or not strategy.strip():
                st.warning("Analysis completed but no strategy was generated. Please try a different topic.")
            else:
                st.session_state.strategy = strategy
                st.success("Analysis Complete!")
    else:
        st.error("Please enter a topic to analyze.")

# Show results and approval
if "strategy" in st.session_state:
    st.subheader("Proposed Investment Strategy")
    st.info(st.session_state.strategy)
    
    col1, col2 = st.columns(2)
    if col1.button("Approve Strategy"):
        with st.spinner("Auditing and calculating confidence score..."):
            audit_found = False
            try:
                for event in app.stream(None, config=st.session_state.config):
                    if "auditor_agent" in event:
                        audit_result = event["auditor_agent"].get("audit_result", "")
                        if audit_result:
                            st.subheader("Audit & Confidence Report")
                            st.write(audit_result)
                            audit_found = True
            except Exception as exc:
                logger.error("Agent graph failed during audit: %s", exc)
                st.error(f"Audit failed: {exc}")
                st.stop()

            if not audit_found:
                st.warning("Audit completed but no report was generated.")

    if col2.button("Reject Strategy"):
        st.warning("Strategy Rejected.")