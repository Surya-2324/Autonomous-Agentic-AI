"""Tests for Start.py – AgentState TypedDict with Annotated reducer."""

import operator
from typing import Annotated, List, get_type_hints

from Start import AgentState


def test_start_agent_state_has_expected_keys():
    annotations = AgentState.__annotations__
    expected = {"macro_data", "proposed_strategy", "audit_result", "decision_log"}
    assert set(annotations.keys()) == expected


def test_start_agent_state_macro_data_is_str():
    assert AgentState.__annotations__["macro_data"] is str


def test_start_agent_state_proposed_strategy_is_str():
    assert AgentState.__annotations__["proposed_strategy"] is str


def test_start_agent_state_audit_result_is_str():
    assert AgentState.__annotations__["audit_result"] is str


def test_start_agent_state_decision_log_uses_annotated_reducer():
    annotation = AgentState.__annotations__["decision_log"]
    assert annotation == Annotated[List[str], operator.add]


def test_start_agent_state_instantiation():
    state = AgentState(
        macro_data="data",
        proposed_strategy="strategy",
        audit_result="result",
        decision_log=["log1"],
    )
    assert state["macro_data"] == "data"
    assert state["proposed_strategy"] == "strategy"
    assert state["audit_result"] == "result"
    assert state["decision_log"] == ["log1"]


def test_start_agent_state_decision_log_reducer_combines():
    """operator.add concatenates two lists, matching the reducer semantics."""
    combined = operator.add(["a"], ["b", "c"])
    assert combined == ["a", "b", "c"]
