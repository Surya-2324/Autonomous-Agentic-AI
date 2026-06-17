import os
import streamlit as st
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from state import AgentState
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Load local .env only for local development
load_dotenv()

# --- Configuration Helper ---
def get_api_key(key_name):
    # Try Streamlit Secrets first (for cloud deployment)
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    # Fallback to environment variables
    return os.getenv(key_name)

# --- SECURE KEY LOADING ---
GROQ_API_KEY = get_api_key("GROQ_API_KEY")
TAVILY_API_KEY = get_api_key("TAVILY_API_KEY")

# --- Validation ---
if not GROQ_API_KEY or not TAVILY_API_KEY:
    st.error("API keys missing! Please check Streamlit Secrets.")
    st.stop()

INVESTMENT_POLICY = {
    "max_exposure_to_tech": "40%",
    "prohibited_sectors": ["crypto", "gambling", "tobacco"],
    "min_credit_rating": "A",
    "must_have_diversification": True
}

# Initialize LLM and Search Tool
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
search_tool = TavilySearch(max_results=3, tavily_api_key=TAVILY_API_KEY)

# --- Agent Functions ---
def macro_intelligence_agent(state: AgentState):
    # Dynamically grab the user's input
    topic = state.get("search_topic") or "current macroeconomic news impact on global markets"
    print(f"--- FETCHING LIVE DATA FOR: {topic} ---")
    
    # Corrected parsing logic
    search_results = search_tool.invoke({"query": topic})
    
    if isinstance(search_results, dict) and "results" in search_results:
        results_list = search_results["results"]
        content_list = [res.get('content', '') for res in results_list if isinstance(res, dict)]
    else:
        content_list = [str(search_results)]
    
    return {
        "macro_data": "\n\n".join(content_list), 
        "decision_log": [f"Macro Agent successfully fetched market data for: {topic}"]
    }

def market_strategy_agent(state: AgentState):
    print("--- GENERATING STRATEGY ---")
    prompt = f"Analyze this macroeconomic data and suggest an investment strategy: {state['macro_data']}"
    response = llm.invoke(prompt)
    return {"proposed_strategy": response.content, "decision_log": ["Strategy Agent analyzed macro trends and proposed a plan."]}

def confidence_agent(state: AgentState):
    print("--- CALCULATING CONFIDENCE SCORE ---")
    strategy = state["proposed_strategy"]
    prompt = f"Assign a confidence score (0-100) and reasoning for this strategy: {strategy}. Return ONLY JSON."
    score_response = llm.invoke(prompt)
    return {"audit_result": f"Confidence Score Report: {score_response.content}"}

def auditor_agent(state: AgentState):
    print("--- RUNNING FORMAL COMPLIANCE AUDIT ---")
    strategy = state["proposed_strategy"]
    audit_prompt = f"Review this strategy against policies {INVESTMENT_POLICY}: {strategy}. State APPROVED or REJECTED."
    audit_decision = llm.invoke(audit_prompt)
    return {"audit_result": audit_decision.content, "decision_log": ["Auditor Agent completed formal policy compliance check."]}

# --- Graph Setup ---
workflow = StateGraph(AgentState)
workflow.add_node("macro_agent", macro_intelligence_agent)
workflow.add_node("strategy_agent", market_strategy_agent)
workflow.add_node("confidence_agent", confidence_agent)
workflow.add_node("auditor_agent", auditor_agent)

workflow.set_entry_point("macro_agent")
workflow.add_edge("macro_agent", "strategy_agent")
workflow.add_edge("strategy_agent", "confidence_agent")
workflow.add_edge("confidence_agent", "auditor_agent")
workflow.add_edge("auditor_agent", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["auditor_agent"])