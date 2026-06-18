import logging
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from state import AgentState
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

# Load local .env only for local development
load_dotenv()

# --- Configuration Helper ---
def get_api_key(key_name):
    # Try Streamlit Secrets first (for cloud deployment)
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except FileNotFoundError:
        # No secrets.toml file exists — expected in local development
        pass
    except Exception as exc:
        logger.warning("Unexpected error reading Streamlit secret '%s': %s", key_name, exc)
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
    topic = state.get("search_topic") or "current macroeconomic news impact on global markets"
    logger.info("Fetching live data for: %s", topic)

    try:
        search_results = search_tool.invoke({"query": topic})
    except Exception as exc:
        error_msg = f"Tavily search failed for '{topic}': {exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from exc

    if isinstance(search_results, dict) and "results" in search_results:
        results_list = search_results["results"]
        content_list = [res.get('content', '') for res in results_list if isinstance(res, dict)]
    else:
        content_list = [str(search_results)]

    macro_data = "\n\n".join(content_list)
    if not macro_data.strip():
        logger.warning("Search returned empty results for: %s", topic)

    return {
        "macro_data": macro_data,
        "decision_log": [f"Macro Agent successfully fetched market data for: {topic}"]
    }

def market_strategy_agent(state: AgentState):
    logger.info("Generating strategy")
    macro_data = state.get("macro_data", "")
    if not macro_data.strip():
        raise ValueError("Cannot generate strategy: macro data is empty")

    prompt = f"Analyze this macroeconomic data and suggest an investment strategy: {macro_data}"
    try:
        response = llm.invoke(prompt)
    except Exception as exc:
        error_msg = f"LLM call failed in strategy agent: {exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from exc

    return {"proposed_strategy": response.content, "decision_log": ["Strategy Agent analyzed macro trends and proposed a plan."]}

def confidence_agent(state: AgentState):
    logger.info("Calculating confidence score")
    strategy = state.get("proposed_strategy", "")
    if not strategy.strip():
        raise ValueError("Cannot calculate confidence: proposed strategy is empty")

    prompt = f"Assign a confidence score (0-100) and reasoning for this strategy: {strategy}. Return ONLY JSON."
    try:
        score_response = llm.invoke(prompt)
    except Exception as exc:
        error_msg = f"LLM call failed in confidence agent: {exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from exc

    return {"audit_result": f"Confidence Score Report: {score_response.content}"}

def auditor_agent(state: AgentState):
    logger.info("Running formal compliance audit")
    strategy = state.get("proposed_strategy", "")
    if not strategy.strip():
        raise ValueError("Cannot audit: proposed strategy is empty")

    audit_prompt = f"Review this strategy against policies {INVESTMENT_POLICY}: {strategy}. State APPROVED or REJECTED."
    try:
        audit_decision = llm.invoke(audit_prompt)
    except Exception as exc:
        error_msg = f"LLM call failed in auditor agent: {exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from exc

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