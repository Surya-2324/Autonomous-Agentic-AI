from langchain_groq import ChatGroq
from state import AgentState


def invoke_llm(
    llm: ChatGroq,
    state: AgentState,
    prompt: str,
    result_key: str,
    log_message: str,
    status_label: str,
) -> dict:
    """Shared helper that wraps the repeated invoke-and-return pattern.

    Every LLM-based agent in the pipeline:
      1. prints a status line,
      2. builds a prompt and calls ``llm.invoke``,
      3. stores the response in *result_key* and appends to *decision_log*.

    This function captures that pattern so agents stay thin.
    """
    print(f"--- {status_label} ---")
    response = llm.invoke(prompt)
    return {
        result_key: response.content,
        "decision_log": [log_message],
    }
