"""
Tests for LLM Factory - provider selection and fallback logic.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.llm_factory import get_crewai_llm, _create_mock_llm, _load_config


class TestLLMFactory:
    """Test suite for LLM factory functions."""

    def test_load_config_returns_dict(self):
        """_load_config should return a dict with 'llm' and 'agents' keys."""
        config = _load_config()
        assert isinstance(config, dict)
        assert "llm" in config
        assert "agents" in config

    def test_create_mock_llm_returns_instance(self):
        """_create_mock_llm should return a callable LLM instance."""
        llm = _create_mock_llm()
        assert llm is not None
        # Should be callable
        result = llm("test message")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_llm_call_returns_string(self):
        """Mock LLM should return a string response."""
        llm = _create_mock_llm()
        result = llm([{"role": "user", "content": "hello"}])
        assert isinstance(result, str)

    @patch.dict(os.environ, {"SPARK_API_KEY": "", "SPARK_API_SECRET": ""})
    @patch("app.core.llm_factory._get_dify_llm_if_configured", return_value=None)
    def test_get_crewai_llm_returns_mock_without_keys(self, mock_dify):
        """Should return MockLLM when no API keys are configured."""
        llm = get_crewai_llm()
        assert llm is not None
        result = llm("test")
        assert isinstance(result, str)

    @patch.dict(
        os.environ,
        {"SPARK_API_KEY": "test_key", "SPARK_API_SECRET": "test_secret"},
    )
    @patch("app.core.llm_factory._load_config")
    @patch("app.core.llm_factory._create_spark_llm")
    def test_get_crewai_llm_uses_spark_with_keys(
        self, mock_spark, mock_config
    ):
        """Should use Spark LLM when API keys are present."""
        mock_config.return_value = {"llm": {"provider": "spark"}}
        mock_spark.return_value = MagicMock()
        llm = get_crewai_llm()
        mock_spark.assert_called_once()

    @patch.dict(
        os.environ,
        {"SPARK_API_KEY": "test_key", "SPARK_API_SECRET": "test_secret"},
    )
    @patch("app.core.llm_factory._load_config")
    @patch("app.core.llm_factory._get_dify_llm_if_configured")
    def test_get_crewai_llm_prefers_dify_when_configured(
        self, mock_dify, mock_config
    ):
        """Should prefer Dify when provider is set to 'dify'."""
        mock_config.return_value = {"llm": {"provider": "dify"}}
        mock_dify_llm = MagicMock()
        mock_dify.return_value = mock_dify_llm
        llm = get_crewai_llm()
        assert llm == mock_dify_llm

    def test_mock_llm_has_model_field(self):
        """Mock LLM should have a model field."""
        llm = _create_mock_llm(model_name="test-model", temperature=0.5)
        assert llm.model == "test-model"
        assert llm.temperature == 0.5


class TestMockLLMImpl:
    """Test the inner MockLLM implementation details."""

    def test_generate_returns_chat_result(self):
        """_generate should return a ChatResult."""
        from langchain_core.outputs import ChatResult

        llm = _create_mock_llm()
        result = llm._generate([])
        assert isinstance(result, ChatResult)

    def test_agenerate_returns_chat_result(self):
        """_agenerate should return a ChatResult."""
        from langchain_core.outputs import ChatResult

        llm = _create_mock_llm()
        result = llm._agenerate([])
        assert isinstance(result, ChatResult)

    def test_stream_yields_chunks(self):
        """_stream should yield ChatGeneration chunks."""
        llm = _create_mock_llm()
        chunks = list(llm._stream([]))
        assert len(chunks) > 0
        assert hasattr(chunks[0], "message")

    def test_invoke_returns_string(self):
        """invoke should return a string."""
        llm = _create_mock_llm()
        result = llm.invoke("test")
        assert isinstance(result, str)
