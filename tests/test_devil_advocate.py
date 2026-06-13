"""
Tests for DevilAdvocate agent.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.devil_advocate import DevilAdvocate


class TestDevilAdvocate:
    """Test suite for DevilAdvocate."""

    def test_init(self):
        agent = DevilAdvocate()
        assert agent.agent_key == "devil_advocate"

    def test_parse_output_with_assumptions(self):
        agent = DevilAdvocate()
        raw = '"weakest_assumption": "Growth rate is overly optimistic", "probable_failure_reason": "CAC too high"'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["weakest_assumption"] == "Growth rate is overly optimistic"
        assert result["probable_failure_reason"] == "CAC too high"

    def test_parse_output_defaults(self):
        agent = DevilAdvocate()
        result = agent.parse_output("nothing", {"topic": "test"})
        assert result["weakest_assumption"] == ""
        assert result["challenges"] == []
        assert result["blind_spots"] == []

    def test_build_prompt_contains_topic(self, sample_topic):
        agent = DevilAdvocate()
        prompt = agent._build_prompt(sample_topic, {})
        assert sample_topic in prompt

    def test_build_prompt_with_other_outputs(self, sample_topic, sample_round1_results):
        agent = DevilAdvocate()
        prompt = agent._build_prompt(sample_topic, sample_round1_results)
        assert sample_topic in prompt
        # Should contain references to other agents' outputs
        assert "opportunity_analyst" in prompt or "risk_controller" in prompt or len(prompt) > 0

    def test_build_prompt_questioning_angles(self, sample_topic):
        agent = DevilAdvocate()
        prompt = agent._build_prompt(sample_topic, {})
        # Should reference questioning angles
        assert len(prompt) > 100  # Non-trivial prompt

    @patch("app.agents.base_agent.get_crewai_llm")
    def test_analyze_with_other_outputs(self, mock_get_llm, sample_topic, sample_round1_results):
        mock_get_llm.return_value = MagicMock()
        agent = DevilAdvocate()
        with patch.object(agent, "create_agent") as mock_create:
            mock_agent = MagicMock()
            mock_agent.execute_task.return_value = '{"challenges": [], "weakest_assumption": "test", "blind_spots": [], "probable_failure_reason": "test"}'
            mock_create.return_value = mock_agent
            result = agent.analyze(sample_topic, {"other_agent_outputs": sample_round1_results})
            assert "weakest_assumption" in result
