from typing import TypedDict, List

class AgentState(TypedDict):
    search_topic: str       # Add this: to hold your live input
    macro_data: str
    proposed_strategy: str
    audit_result: str
    decision_log: List[str]