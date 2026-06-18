import streamlit as st
from main import app
from state import create_initial_state

st.set_page_config(page_title="Agentic Compliance Auditor", layout="centered")

st.title("Real-Time Agentic Auditor")
st.write("Enter a topic below to perform live research and compliance auditing.")

if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "user_session_1"}}

user_topic = st.text_input("What would you like to analyze?", "Impact of US interest rates on tech stocks")

if st.button("Run Analysis"):
    if user_topic:
        with st.spinner(f"Searching live news for: {user_topic}..."):
            dynamic_state = create_initial_state(user_topic)
            app.invoke(dynamic_state, config=st.session_state.config)

            snapshot = app.get_state(st.session_state.config)
            strategy = snapshot.values.get("proposed_strategy")
            st.session_state.strategy = strategy
            st.success("Analysis Complete!")
    else:
        st.error("Please enter a topic to analyze.")

if "strategy" in st.session_state:
    st.subheader("Proposed Investment Strategy")
    st.info(st.session_state.strategy)

    col1, col2 = st.columns(2)
    if col1.button("Approve Strategy"):
        with st.spinner("Auditing and calculating confidence score..."):
            for event in app.stream(None, config=st.session_state.config):
                if "auditor_agent" in event:
                    st.subheader("Audit & Confidence Report")
                    st.write(event["auditor_agent"]["audit_result"])

    if col2.button("Reject Strategy"):
        st.warning("Strategy Rejected.")
