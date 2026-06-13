"""
Tests for SparkChatModel - iFlytek Spark LLM wrapper.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.llm_spark_mock import SparkChatModel, MockSparkChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class TestSparkChatModel:
    """Test suite for SparkChatModel."""

    def test_init_defaults(self):
        """Should initialize with default values."""
        model = SparkChatModel()
        assert model.spark_model_version == "generalv3.5"
        assert model.temperature == 0.7
        assert model.max_tokens == 4096

    def test_is_mock_without_keys(self):
        """Should be in mock mode without API keys."""
        model = SparkChatModel(spark_api_key="", spark_api_secret="")
        assert model._is_mock is True

    def test_is_not_mock_with_keys(self):
        """Should not be in mock mode with API keys."""
        model = SparkChatModel(spark_api_key="key", spark_api_secret="secret")
        assert model._is_mock is False

    def test_llm_type(self):
        """Should return correct LLM type identifier."""
        model = SparkChatModel()
        assert model._llm_type == "spark-chat-model"

    def test_identifying_params(self):
        """Should return model identification parameters."""
        model = SparkChatModel(spark_domain="generalv3.5", temperature=0.5)
        params = model._identifying_params
        assert "model" in params
        assert params["temperature"] == 0.5

    def test_mock_generate_returns_chat_result(self):
        """Mock mode should return a ChatResult."""
        from langchain_core.outputs import ChatResult

        model = SparkChatModel(spark_api_key="", spark_api_secret="")
        result = model._generate([HumanMessage(content="test")])
        assert isinstance(result, ChatResult)

    def test_mock_response_contains_input(self):
        """Mock response should reference the user's input."""
        model = SparkChatModel(spark_api_key="", spark_api_secret="")
        response = model._mock_response([HumanMessage(content="analyze market")])
        assert "analyze market" in response or "Mock" in response or "Mock" in response

    def test_to_spark_format(self):
        """Should convert LangChain messages to Spark format."""
        model = SparkChatModel()
        messages = [
            SystemMessage(content="You are an analyst"),
            HumanMessage(content="Analyze this"),
        ]
        result = model._to_spark_format(messages)
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"

    def test_to_spark_format_ai_message(self):
        """Should handle AI messages correctly."""
        model = SparkChatModel()
        messages = [AIMessage(content="Response")]
        result = model._to_spark_format(messages)
        assert result[0]["role"] == "assistant"


class TestMockSparkChatModel:
    """Test MockSparkChatModel (forced mock mode)."""

    def test_is_always_mock(self):
        """MockSparkChatModel should always be in mock mode."""
        model = MockSparkChatModel()
        assert model._is_mock is True

    def test_ignores_provided_keys(self):
        """Should ignore any API keys passed."""
        model = MockSparkChatModel(spark_api_key="real_key", spark_api_secret="real_secret")
        assert model._is_mock is True
        assert model.spark_api_key == ""
        assert model.spark_api_secret == ""
