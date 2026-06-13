"""
Tests for ProsConsAnalyst agent.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.proscons_analyst import ProsConsAnalyst


class TestProsConsAnalyst:
    """Test suite for ProsConsAnalyst."""

    def test_init(self):
        agent = ProsConsAnalyst()
        assert agent.agent_key == "proscons_analyst"

    def test_parse_output_positive_net_score(self):
        agent = ProsConsAnalyst()
        raw = '"net_score": 18, "net_verdict": "Advantages clearly outweigh disadvantages"'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["net_score"] == 18
        assert "Advantages" in result["net_verdict"]

    def test_parse_output_negative_net_score(self):
        agent = ProsConsAnalyst()
        raw = '"net_score": -12, "net_verdict": "Disadvantages outweigh advantages"'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["net_score"] == -12

    def test_parse_output_defaults(self):
        agent = ProsConsAnalyst()
        result = agent.parse_output("no data", {"topic": "test"})
        assert result["net_score"] == 0

    def test_build_prompt_contains_topic(self, sample_topic):
        agent = ProsConsAnalyst()
        prompt = agent._build_prompt(sample_topic, {})
        assert sample_topic in prompt

    @patch("app.agents.base_agent.get_crewai_llm")
    def test_analyze_with_mock(self, mock_get_llm, sample_topic):
        mock_get_llm.return_value = MagicMock()
        agent = ProsConsAnalyst()
        with patch.object(agent, "create_agent") as mock_create:
            mock_agent = MagicMock()
            mock_agent.execute_task.return_value = '{"pros": [], "cons": [], "net_score": 5, "net_verdict": "Slightly positive"}'
            mock_create.return_value = mock_agent
            result = agent.analyze(sample_topic, {})
            assert "net_score" in result
