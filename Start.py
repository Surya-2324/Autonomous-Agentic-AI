from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    macro_data: str
    proposed_strategy: str
    audit_result: str
    decision_log: Annotated[List[str], operator.add]