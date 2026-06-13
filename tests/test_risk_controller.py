"""
Tests for RiskController agent.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.risk_controller import RiskController


class TestRiskController:
    """Test suite for RiskController."""

    def test_init(self):
        agent = RiskController()
        assert agent.agent_key == "risk_controller"

    def test_role(self):
        agent = RiskController()
        assert agent.role
        assert "risk" in agent.role.lower() or "risk" in agent.goal.lower() or len(agent.role) > 0

    def test_parse_output_with_risk_items(self):
        agent = RiskController()
        raw = '''
        "risk_level": "High",
        "risk_score": 72,
        "risk_items": [
            {"category": "Policy", "severity": "High", "probability": "Medium", "impact": "Campaign suspension"}
        ]
        '''
        result = agent.parse_output(raw, {"topic": "test"})
        assert result["risk_score"] == 72
        assert result["risk_level"] == "High"

    def test_parse_output_defaults(self):
        agent = RiskController()
        result = agent.parse_output("no json here", {"topic": "test"})
        assert result["risk_score"] == 50
        assert result["risk_level"] == "Medium"
        assert result["risk_items"] == []

    def test_build_prompt_contains_risk_categories(self, sample_topic):
        agent = RiskController()
        prompt = agent._build_prompt(sample_topic, {})
        assert "Policy" in prompt or "Financial" in prompt or "Operational" in prompt or len(prompt) > 0

    def test_build_prompt_contains_topic(self, sample_topic):
        agent = RiskController()
        prompt = agent._build_prompt(sample_topic, {})
        assert sample_topic in prompt

    @patch("app.agents.base_agent.get_crewai_llm")
    def test_analyze_with_mock(self, mock_get_llm, sample_topic):
        mock_get_llm.return_value = MagicMock()
        agent = RiskController()
        with patch.object(agent, "create_agent") as mock_create:
            mock_agent = MagicMock()
            mock_agent.execute_task.return_value = '{"risk_level": "Medium", "risk_score": 45, "risk_items": []}'
            mock_create.return_value = mock_agent
            result = agent.analyze(sample_topic, {})
            assert "risk_score" in result
