import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

INVESTMENT_POLICY = {
    "max_exposure_to_tech": "40%",
    "prohibited_sectors": ["crypto", "gambling", "tobacco"],
    "min_credit_rating": "A",
    "must_have_diversification": True,
}


def get_api_key(key_name: str) -> str | None:
    """Load an API key from Streamlit Secrets (cloud) or env vars (local)."""
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name)


def validate_api_keys(**keys: str | None) -> None:
    """Halt the Streamlit app when any required key is missing."""
    missing = [name for name, value in keys.items() if not value]
    if missing:
        st.error(f"API keys missing: {', '.join(missing)}. Please check Streamlit Secrets.")
        st.stop()


def init_services() -> tuple[ChatGroq, TavilySearch]:
    """Create and return the LLM and search tool, validating keys first."""
    groq_key = get_api_key("GROQ_API_KEY")
    tavily_key = get_api_key("TAVILY_API_KEY")
    validate_api_keys(GROQ_API_KEY=groq_key, TAVILY_API_KEY=tavily_key)

    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)
    search_tool = TavilySearch(max_results=3, tavily_api_key=tavily_key)
    return llm, search_tool
