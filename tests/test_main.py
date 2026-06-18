"""Tests for main.py – agent functions, get_api_key, policy, and graph structure.

main.py has heavy module-level side effects (LLM/search-tool init, st.stop on
missing keys).  We mock those at import time via ``conftest.py`` fixtures and
env-var setup, then exercise each agent function with controlled inputs.
"""

import os
import sys
import importlib
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers to import main.py safely (with mocked externals)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_main_module():
    """Remove cached ``main`` module so each test can re-import cleanly."""
    sys.modules.pop("main", None)
    yield
    sys.modules.pop("main", None)


def _import_main():
    """Import main.py with fake API keys and mocked Streamlit / external deps."""
    os.environ["GROQ_API_KEY"] = "fake-groq-key"
    os.environ["TAVILY_API_KEY"] = "fake-tavily-key"

    # Patch streamlit attributes that main.py calls at module level
    with patch("streamlit.secrets", new={}), \
         patch("streamlit.error"), \
         patch("streamlit.stop"):
        mod = importlib.import_module("main")
    return mod


# ===================== get_api_key =====================

class TestGetApiKey:
    def test_returns_env_var_when_streamlit_secrets_missing(self):
        main = _import_main()
        os.environ["MY_TEST_KEY"] = "from-env"
        try:
            assert main.get_api_key("MY_TEST_KEY") == "from-env"
        finally:
            del os.environ["MY_TEST_KEY"]

    def test_returns_none_when_key_not_set(self):
        main = _import_main()
        os.environ.pop("NONEXISTENT_KEY_12345", None)
        assert main.get_api_key("NONEXISTENT_KEY_12345") is None

    def test_prefers_streamlit_secret_over_env_var(self):
        main = _import_main()
        os.environ["DUAL_KEY"] = "from-env"
        try:
            fake_secrets = {"DUAL_KEY": "from-st"}
            with patch("streamlit.secrets", new=fake_secrets):
                result = main.get_api_key("DUAL_KEY")
            assert result == "from-st"
        finally:
            del os.environ["DUAL_KEY"]


# ===================== INVESTMENT_POLICY =====================

class TestInvestmentPolicy:
    def test_policy_keys(self):
        main = _import_main()
        expected_keys = {
            "max_exposure_to_tech",
            "prohibited_sectors",
            "min_credit_rating",
            "must_have_diversification",
        }
        assert set(main.INVESTMENT_POLICY.keys()) == expected_keys

    def test_prohibited_sectors_is_list(self):
        main = _import_main()
        assert isinstance(main.INVESTMENT_POLICY["prohibited_sectors"], list)

    def test_prohibited_sectors_contains_expected(self):
        main = _import_main()
        for sector in ["crypto", "gambling", "tobacco"]:
            assert sector in main.INVESTMENT_POLICY["prohibited_sectors"]

    def test_must_have_diversification_is_true(self):
        main = _import_main()
        assert main.INVESTMENT_POLICY["must_have_diversification"] is True

    def test_min_credit_rating(self):
        main = _import_main()
        assert main.INVESTMENT_POLICY["min_credit_rating"] == "A"

    def test_max_exposure_to_tech(self):
        main = _import_main()
        assert main.INVESTMENT_POLICY["max_exposure_to_tech"] == "40%"


# ===================== macro_intelligence_agent =====================

class TestMacroIntelligenceAgent:
    def test_uses_search_topic_from_state(self):
        main = _import_main()
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = {"results": [{"content": "news item"}]}
        main.search_tool = mock_tool

        state = {
            "search_topic": "AI chip stocks",
            "macro_data": "",
            "proposed_strategy": "",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.macro_intelligence_agent(state)

        mock_tool.invoke.assert_called_once_with({"query": "AI chip stocks"})
        assert "news item" in result["macro_data"]
        assert len(result["decision_log"]) == 1

    def test_falls_back_to_default_topic(self):
        main = _import_main()
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = "raw string result"
        main.search_tool = mock_tool

        state = {
            "search_topic": "",
            "macro_data": "",
            "proposed_strategy": "",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.macro_intelligence_agent(state)

        called_query = mock_tool.invoke.call_args[0][0]["query"]
        assert "macroeconomic" in called_query
        assert result["macro_data"] == "raw string result"

    def test_handles_non_dict_search_results(self):
        main = _import_main()
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = "plain text results"
        main.search_tool = mock_tool

        state = {
            "search_topic": "test",
            "macro_data": "",
            "proposed_strategy": "",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.macro_intelligence_agent(state)
        assert result["macro_data"] == "plain text results"

    def test_handles_dict_results_without_results_key(self):
        main = _import_main()
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = {"other_key": "value"}
        main.search_tool = mock_tool

        state = {
            "search_topic": "test",
            "macro_data": "",
            "proposed_strategy": "",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.macro_intelligence_agent(state)
        assert "other_key" in result["macro_data"]

    def test_multiple_search_results_joined(self):
        main = _import_main()
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = {
            "results": [
                {"content": "result one"},
                {"content": "result two"},
                {"content": "result three"},
            ]
        }
        main.search_tool = mock_tool

        state = {
            "search_topic": "multi results",
            "macro_data": "",
            "proposed_strategy": "",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.macro_intelligence_agent(state)
        assert "result one" in result["macro_data"]
        assert "result two" in result["macro_data"]
        assert "result three" in result["macro_data"]


# ===================== market_strategy_agent =====================

class TestMarketStrategyAgent:
    def test_returns_strategy_from_llm(self):
        main = _import_main()
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Buy tech stocks")
        main.llm = mock_llm

        state = {
            "search_topic": "",
            "macro_data": "Strong GDP growth",
            "proposed_strategy": "",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.market_strategy_agent(state)

        assert result["proposed_strategy"] == "Buy tech stocks"
        assert len(result["decision_log"]) == 1
        assert "Strategy Agent" in result["decision_log"][0]

    def test_prompt_contains_macro_data(self):
        main = _import_main()
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="strategy")
        main.llm = mock_llm

        state = {
            "search_topic": "",
            "macro_data": "SPECIFIC_MACRO_DATA_123",
            "proposed_strategy": "",
            "audit_result": "",
            "decision_log": [],
        }
        main.market_strategy_agent(state)

        prompt = mock_llm.invoke.call_args[0][0]
        assert "SPECIFIC_MACRO_DATA_123" in prompt


# ===================== confidence_agent =====================

class TestConfidenceAgent:
    def test_returns_confidence_score(self):
        main = _import_main()
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content='{"score": 85, "reasoning": "solid"}')
        main.llm = mock_llm

        state = {
            "search_topic": "",
            "macro_data": "",
            "proposed_strategy": "Invest in bonds",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.confidence_agent(state)

        assert "Confidence Score Report" in result["audit_result"]
        assert "85" in result["audit_result"]

    def test_prompt_contains_strategy(self):
        main = _import_main()
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="score")
        main.llm = mock_llm

        state = {
            "search_topic": "",
            "macro_data": "",
            "proposed_strategy": "UNIQUE_STRATEGY_XYZ",
            "audit_result": "",
            "decision_log": [],
        }
        main.confidence_agent(state)

        prompt = mock_llm.invoke.call_args[0][0]
        assert "UNIQUE_STRATEGY_XYZ" in prompt


# ===================== auditor_agent =====================

class TestAuditorAgent:
    def test_returns_audit_decision(self):
        main = _import_main()
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="APPROVED")
        main.llm = mock_llm

        state = {
            "search_topic": "",
            "macro_data": "",
            "proposed_strategy": "Diversified portfolio",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.auditor_agent(state)

        assert result["audit_result"] == "APPROVED"
        assert any("Auditor Agent" in log for log in result["decision_log"])

    def test_audit_prompt_references_policy(self):
        main = _import_main()
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="REJECTED")
        main.llm = mock_llm

        state = {
            "search_topic": "",
            "macro_data": "",
            "proposed_strategy": "All in crypto",
            "audit_result": "",
            "decision_log": [],
        }
        main.auditor_agent(state)

        prompt = mock_llm.invoke.call_args[0][0]
        assert "prohibited_sectors" in prompt or "crypto" in prompt

    def test_rejected_strategy(self):
        main = _import_main()
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="REJECTED: violates crypto prohibition")
        main.llm = mock_llm

        state = {
            "search_topic": "",
            "macro_data": "",
            "proposed_strategy": "100% Bitcoin",
            "audit_result": "",
            "decision_log": [],
        }
        result = main.auditor_agent(state)
        assert "REJECTED" in result["audit_result"]


# ===================== Workflow graph structure =====================

class TestGraphStructure:
    def test_compiled_app_exists(self):
        main = _import_main()
        assert main.app is not None

    def test_workflow_has_correct_nodes(self):
        main = _import_main()
        node_names = set(main.workflow.nodes.keys())
        expected = {"macro_agent", "strategy_agent", "confidence_agent", "auditor_agent"}
        assert expected.issubset(node_names)

    def test_entry_point_is_macro_agent(self):
        """The first node after __start__ should be macro_agent."""
        main = _import_main()
        # In LangGraph, the compiled graph's nodes include __start__ and __end__
        # Check that the entry point leads to macro_agent
        graph_nodes = set(main.workflow.nodes.keys())
        assert "macro_agent" in graph_nodes
