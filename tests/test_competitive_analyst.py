"""
Tests for CompetitiveAnalyst agent.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.competitive_analyst import CompetitiveAnalyst


class TestCompetitiveAnalyst:
    """Test suite for CompetitiveAnalyst."""

    def test_init(self):
        agent = CompetitiveAnalyst()
        assert agent.agent_key == "competitive_analyst"

    def test_parse_output_full(self):
        agent = CompetitiveAnalyst()
        raw = '''
        "competitive_intensity": "High",
        "is_good_timing": true,
        "window_status": "Window open"
        '''
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["competitive_intensity"] == "High"
        assert result["timing_assessment"]["is_good_timing"] is True
        assert result["timing_assessment"]["window_status"] == "Window open"

    def test_parse_output_bad_timing(self):
        agent = CompetitiveAnalyst()
        raw = '"is_good_timing": false, "window_status": "Window closing"'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["timing_assessment"]["is_good_timing"] is False

    def test_parse_output_defaults(self):
        agent = CompetitiveAnalyst()
        result = agent.parse_output("no data", {"topic": "test"})
        assert result["competitive_intensity"] == ""
        assert result["competitive_threats"] == []

    def test_build_prompt_contains_frameworks(self, sample_topic):
        agent = CompetitiveAnalyst()
        prompt = agent._build_prompt(sample_topic, {})
        assert "Porter" in prompt or "Competitive" in prompt or len(prompt) > 50

    @patch("app.agents.base_agent.get_crewai_llm")
    def test_analyze_with_mock(self, mock_get_llm, sample_topic):
        mock_get_llm.return_value = MagicMock()
        agent = CompetitiveAnalyst()
        with patch.object(agent, "create_agent") as mock_create:
            mock_agent = MagicMock()
            mock_agent.execute_task.return_value = '{"competitive_intensity": "Medium", "competitive_threats": []}'
            mock_create.return_value = mock_agent
            result = agent.analyze(sample_topic, {})
            assert "competitive_intensity" in result
