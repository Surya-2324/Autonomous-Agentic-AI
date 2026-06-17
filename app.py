import streamlit as st
from main import app # We don't import initial_state anymore; we create it dynamically

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
            # 2. Create the initial state DYNAMICALLY with the user's topic
            dynamic_state = {
                "search_topic": user_topic, 
                "macro_data": "", 
                "proposed_strategy": "", 
                "audit_result": "", 
                "decision_log": []
            }
            
            # Invoke the graph with the dynamic state
            app.invoke(dynamic_state, config=st.session_state.config)
            
            # Get the strategy from the state
            snapshot = app.get_state(st.session_state.config)
            strategy = snapshot.values.get("proposed_strategy")
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
            # Resume the graph
            for event in app.stream(None, config=st.session_state.config):
                # The final audit and confidence result will be in the events
                if "auditor_agent" in event:
                    st.subheader("Audit & Confidence Report")
                    st.write(event["auditor_agent"]["audit_result"])
    
    if col2.button("Reject Strategy"):
        st.warning("Strategy Rejected.")