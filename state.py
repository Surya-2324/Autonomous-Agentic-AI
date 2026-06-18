import operator
from typing import Annotated, List, TypedDict


class AgentState(TypedDict):
    search_topic: str
    macro_data: str
    proposed_strategy: str
    audit_result: str
    decision_log: Annotated[List[str], operator.add]


def create_initial_state(topic: str) -> AgentState:
    """Build the default starting state for a new analysis run."""
    return AgentState(
        search_topic=topic,
        macro_data="",
        proposed_strategy="",
        audit_result="",
        decision_log=[],
    )
