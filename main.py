from state import AgentState
from utils.config import INVESTMENT_POLICY, init_services
from utils.llm_helpers import invoke_llm
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

llm, search_tool = init_services()


# --- Agent Functions ---
def macro_intelligence_agent(state: AgentState):
    topic = state.get("search_topic") or "current macroeconomic news impact on global markets"
    print(f"--- FETCHING LIVE DATA FOR: {topic} ---")

    search_results = search_tool.invoke({"query": topic})

    if isinstance(search_results, dict) and "results" in search_results:
        results_list = search_results["results"]
        content_list = [res.get("content", "") for res in results_list if isinstance(res, dict)]
    else:
        content_list = [str(search_results)]

    return {
        "macro_data": "\n\n".join(content_list),
        "decision_log": [f"Macro Agent successfully fetched market data for: {topic}"],
    }


def market_strategy_agent(state: AgentState):
    return invoke_llm(
        llm,
        state,
        prompt=f"Analyze this macroeconomic data and suggest an investment strategy: {state['macro_data']}",
        result_key="proposed_strategy",
        log_message="Strategy Agent analyzed macro trends and proposed a plan.",
        status_label="GENERATING STRATEGY",
    )


def confidence_agent(state: AgentState):
    return invoke_llm(
        llm,
        state,
        prompt=(
            f"Assign a confidence score (0-100) and reasoning for this strategy: "
            f"{state['proposed_strategy']}. Return ONLY JSON."
        ),
        result_key="audit_result",
        log_message="Confidence Agent calculated a confidence score.",
        status_label="CALCULATING CONFIDENCE SCORE",
    )


def auditor_agent(state: AgentState):
    return invoke_llm(
        llm,
        state,
        prompt=(
            f"Review this strategy against policies {INVESTMENT_POLICY}: "
            f"{state['proposed_strategy']}. State APPROVED or REJECTED."
        ),
        result_key="audit_result",
        log_message="Auditor Agent completed formal policy compliance check.",
        status_label="RUNNING FORMAL COMPLIANCE AUDIT",
    )


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
