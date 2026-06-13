"""
Tests for CrewAISparkLLM - CrewAI adapter for Spark LLM.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.llm_spark_crewai import CrewAISparkLLM
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class TestCrewAISparkLLM:
    """Test suite for CrewAISparkLLM adapter."""

    def _make_spark_mock(self, response="test response"):
        """Helper to create a mock SparkChatModel."""
        spark = MagicMock()
        spark._generate.return_value = ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=response))]
        )
        spark._agenerate.return_value = ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=response))]
        )
        return spark

    def test_init(self):
        """Should wrap a SparkChatModel instance."""
        spark = self._make_spark_mock()
        llm = CrewAISparkLLM(spark_chat_model=spark)
        assert llm._spark is spark

    def test_call_returns_string(self):
        """call() should return a string response."""
        spark = self._make_spark_mock("hello from spark")
        llm = CrewAISparkLLM(spark_chat_model=spark)
        result = llm.call([HumanMessage(content="test")])
        assert result == "hello from spark"

    def test_dunder_call_returns_string(self):
        """__call__ should return a string response."""
        spark = self._make_spark_mock("response")
        llm = CrewAISparkLLM(spark_chat_model=spark)
        result = llm([HumanMessage(content="test")])
        assert result == "response"

    def test_invoke_returns_string(self):
        """invoke should return a string response."""
        spark = self._make_spark_mock("invoke response")
        llm = CrewAISparkLLM(spark_chat_model=spark)
        result = llm.invoke([HumanMessage(content="test")])
        assert result == "invoke response"

    def test_generate_delegates_to_spark(self):
        """_generate should delegate to the wrapped SparkChatModel."""
        spark = self._make_spark_mock("delegated")
        llm = CrewAISparkLLM(spark_chat_model=spark)
        result = llm._generate([HumanMessage(content="test")])
        spark._generate.assert_called_once()
        assert result.generations[0].message.content == "delegated"

    def test_model_field(self):
        """Should have a model field."""
        spark = self._make_spark_mock()
        llm = CrewAISparkLLM(spark_chat_model=spark)
        assert llm.model == "spark-model"
