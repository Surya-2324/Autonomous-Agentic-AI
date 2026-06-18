"""Tests for state.py – AgentState TypedDict."""

from state import AgentState


def test_agent_state_has_expected_keys():
    annotations = AgentState.__annotations__
    expected = {"search_topic", "macro_data", "proposed_strategy", "audit_result", "decision_log"}
    assert set(annotations.keys()) == expected


def test_agent_state_search_topic_is_str():
    assert AgentState.__annotations__["search_topic"] is str


def test_agent_state_macro_data_is_str():
    assert AgentState.__annotations__["macro_data"] is str


def test_agent_state_proposed_strategy_is_str():
    assert AgentState.__annotations__["proposed_strategy"] is str


def test_agent_state_audit_result_is_str():
    assert AgentState.__annotations__["audit_result"] is str


def test_agent_state_decision_log_is_list_of_str():
    from typing import List
    assert AgentState.__annotations__["decision_log"] == List[str]


def test_agent_state_instantiation():
    state = AgentState(
        search_topic="test topic",
        macro_data="macro info",
        proposed_strategy="strategy text",
        audit_result="approved",
        decision_log=["step1"],
    )
    assert state["search_topic"] == "test topic"
    assert state["macro_data"] == "macro info"
    assert state["proposed_strategy"] == "strategy text"
    assert state["audit_result"] == "approved"
    assert state["decision_log"] == ["step1"]
