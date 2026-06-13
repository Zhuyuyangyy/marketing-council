"""
Tests for OpportunityAnalyst agent.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.opportunity_analyst import OpportunityAnalyst


class TestOpportunityAnalyst:
    """Test suite for OpportunityAnalyst."""

    def test_init(self):
        """Should initialize with correct agent key."""
        agent = OpportunityAnalyst()
        assert agent.agent_key == "opportunity_analyst"

    def test_role(self):
        """Should have a meaningful role."""
        agent = OpportunityAnalyst()
        assert agent.role
        assert len(agent.role) > 0

    def test_parse_output_valid_json(self):
        """Should parse valid JSON output correctly."""
        agent = OpportunityAnalyst()
        raw = '{"opportunity_score": 82, "opportunity_points": ["point1", "point2"], "window_period": "6 months", "target_segment": "young adults", "market_size": "10B", "growth_potential": "High"}'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["opportunity_score"] == 82
        assert len(result["opportunity_points"]) == 2
        assert result["window_period"] == "6 months"

    def test_parse_output_with_extra_text(self):
        """Should extract JSON even when surrounded by extra text."""
        agent = OpportunityAnalyst()
        raw = 'Here is the analysis:\n{"opportunity_score": 65, "opportunity_points": ["p1"], "window_period": "3m", "target_segment": "all", "market_size": "5B", "growth_potential": "Medium"}\nEnd of analysis.'
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["opportunity_score"] == 65

    def test_parse_output_invalid_json(self):
        """Should return default values for invalid JSON."""
        agent = OpportunityAnalyst()
        result = agent.parse_output("not json at all", {"topic": "test"})
        assert result["opportunity_score"] == 50
        assert result["opportunity_points"] == []
        assert "raw" in result

    def test_parse_output_partial_json(self):
        """Should handle partial/malformed JSON gracefully."""
        agent = OpportunityAnalyst()
        raw = '{"opportunity_score": 70, broken'
        result = agent.parse_output(raw, {"topic": "test"})
        assert "opportunity_score" in result or result["opportunity_score"] == 50

    def test_build_prompt_contains_topic(self, sample_topic):
        """Prompt should contain the topic text."""
        agent = OpportunityAnalyst()
        prompt = agent._build_prompt(sample_topic, {})
        assert sample_topic in prompt

    def test_build_prompt_contains_frameworks(self, sample_topic):
        """Prompt should reference analysis frameworks."""
        agent = OpportunityAnalyst()
        prompt = agent._build_prompt(sample_topic, {})
        assert "PEST" in prompt or "SWOT" in prompt or "STP" in prompt

    @patch("app.agents.base_agent.get_crewai_llm")
    def test_analyze_with_mock_llm(self, mock_get_llm, sample_topic):
        """analyze should work with mock LLM."""
        mock_llm = MagicMock()
        mock_llm.call.return_value = '{"opportunity_score": 75, "opportunity_points": ["p1"], "window_period": "6m", "target_segment": "all", "market_size": "10B", "growth_potential": "High"}'
        mock_get_llm.return_value = mock_llm

        agent = OpportunityAnalyst()
        # Mock the create_agent to avoid CrewAI task execution
        with patch.object(agent, "create_agent") as mock_create:
            mock_agent = MagicMock()
            mock_agent.execute_task.return_value = '{"opportunity_score": 75, "opportunity_points": ["p1"], "window_period": "6m", "target_segment": "all", "market_size": "10B", "growth_potential": "High"}'
            mock_create.return_value = mock_agent
            result = agent.analyze(sample_topic, {})
            assert "opportunity_score" in result
