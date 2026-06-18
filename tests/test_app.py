"""Tests for app.py – Streamlit UI wiring.

app.py imports ``main.app`` at module level, which triggers all of main.py's
side effects.  We therefore mock the ``main`` module before importing ``app``.
"""

import sys
import importlib
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _clean_app_modules():
    """Drop cached app/main so each test starts fresh."""
    for mod_name in ("app", "main"):
        sys.modules.pop(mod_name, None)
    yield
    for mod_name in ("app", "main"):
        sys.modules.pop(mod_name, None)


def _make_mock_main():
    """Return a mock ``main`` module with a stub ``app`` attribute."""
    mock_main = MagicMock()
    mock_main.app = MagicMock()
    return mock_main


# ===================== Module-level imports =====================

class TestAppImport:
    def test_app_imports_main_app(self):
        """app.py should reference ``main.app`` (the compiled LangGraph)."""
        mock_main = _make_mock_main()
        sys.modules["main"] = mock_main

        with patch("streamlit.set_page_config"), \
             patch("streamlit.title"), \
             patch("streamlit.write"), \
             patch("streamlit.text_input", return_value="test topic"), \
             patch("streamlit.button", return_value=False), \
             patch("streamlit.session_state", new=MagicMock()):
            mod = importlib.import_module("app")

        assert mod is not None

    def test_page_config_is_set(self):
        """app.py should call st.set_page_config at import time."""
        mock_main = _make_mock_main()
        sys.modules["main"] = mock_main

        with patch("streamlit.set_page_config") as mock_cfg, \
             patch("streamlit.title"), \
             patch("streamlit.write"), \
             patch("streamlit.text_input", return_value="test topic"), \
             patch("streamlit.button", return_value=False), \
             patch("streamlit.session_state", new=MagicMock()):
            importlib.import_module("app")

        mock_cfg.assert_called_once()
        call_kwargs = mock_cfg.call_args
        assert "Agentic Compliance Auditor" in str(call_kwargs)
