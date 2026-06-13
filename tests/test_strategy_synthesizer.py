"""
Tests for StrategySynthesizer agent.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.strategy_synthesizer import StrategySynthesizer


class TestStrategySynthesizer:
    """Test suite for StrategySynthesizer."""

    def test_init(self):
        agent = StrategySynthesizer()
        assert agent.agent_key == "strategy_synthesizer"

    def test_parse_output_strong_go(self):
        agent = StrategySynthesizer()
        raw = '"decision": "STRONG-GO", "confidence": 85'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["decision"] == "STRONG-GO"
        assert result["confidence"] == 85

    def test_parse_output_conditional_go(self):
        agent = StrategySynthesizer()
        raw = '"decision": "CONDITIONAL-GO", "confidence": 68'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["decision"] == "CONDITIONAL-GO"

    def test_parse_output_hold(self):
        agent = StrategySynthesizer()
        raw = '"decision": "HOLD", "confidence": 45'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["decision"] == "HOLD"

    def test_parse_output_stop(self):
        agent = StrategySynthesizer()
        raw = '"decision": "STOP", "confidence": 20'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["decision"] == "STOP"

    def test_parse_output_defaults(self):
        agent = StrategySynthesizer()
        result = agent.parse_output("no data", {"topic": "test"})
        assert result["decision"] == "HOLD"
        assert result["confidence"] == 50

    def test_parse_output_conditions(self):
        agent = StrategySynthesizer()
        raw = '"decision": "CONDITIONAL-GO", "confidence": 70, "conditions": ["Pass compliance review", "Reduce budget by 30%"]'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["decision"] == "CONDITIONAL-GO"
        assert len(result["conditions"]) >= 1

    def test_synthesize_prompt_contains_round_data(
        self, sample_topic, sample_round1_results, sample_round2_results
    ):
        agent = StrategySynthesizer()
        prompt = agent._build_synthesis_prompt(
            sample_topic, sample_round1_results, sample_round2_results
        )
        assert sample_topic in prompt
        assert "STRONG-GO" in prompt
        assert "CONDITIONAL-GO" in prompt
        assert "HOLD" in prompt
        assert "STOP" in prompt

    @patch("app.agents.base_agent.get_crewai_llm")
    def test_synthesize_with_mock(
        self, mock_get_llm, sample_topic, sample_round1_results, sample_round2_results
    ):
        mock_get_llm.return_value = MagicMock()
        agent = StrategySynthesizer()
        with patch.object(agent, "create_agent") as mock_create:
            mock_agent = MagicMock()
            mock_agent.execute_task.return_value = '{"decision": "CONDITIONAL-GO", "confidence": 72, "conditions": [], "key_concerns": [], "next_steps": [], "summary": "Test summary"}'
            mock_create.return_value = mock_agent
            result = agent.synthesize(
                sample_topic, sample_round1_results, sample_round2_results
            )
            assert "decision" in result
            assert result["decision"] in [
                "STRONG-GO",
                "CONDITIONAL-GO",
                "HOLD",
                "STOP",
            ]
