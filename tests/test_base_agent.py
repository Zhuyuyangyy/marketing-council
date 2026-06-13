"""
Tests for MarketingBaseAgent base class.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.base_agent import MarketingBaseAgent


class TestMarketingBaseAgent:
    """Test suite for the base agent class."""

    def test_init_loads_config(self):
        """Agent should load config.yaml on initialization."""
        agent = MarketingBaseAgent("opportunity_analyst")
        assert agent.agent_key == "opportunity_analyst"
        assert agent.config is not None
        assert "agents" in agent.config

    def test_role_property(self):
        """Role property should return agent role from config."""
        agent = MarketingBaseAgent("opportunity_analyst")
        assert agent.role  # Should not be empty
        assert isinstance(agent.role, str)

    def test_goal_property(self):
        """Goal property should return agent goal from config."""
        agent = MarketingBaseAgent("risk_controller")
        assert agent.goal
        assert isinstance(agent.goal, str)

    def test_backstory_property(self):
        """Backstory property should return agent backstory from config."""
        agent = MarketingBaseAgent("devil_advocate")
        assert agent.backstory
        assert isinstance(agent.backstory, str)

    def test_unknown_agent_defaults(self):
        """Unknown agent key should return sensible defaults."""
        agent = MarketingBaseAgent("nonexistent_agent")
        assert agent.role == "nonexistent_agent"
        assert agent.goal == ""
        assert agent.backstory == ""

    def test_build_prompt_raises_not_implemented(self):
        """build_prompt should raise NotImplementedError."""
        agent = MarketingBaseAgent("opportunity_analyst")
        with pytest.raises(NotImplementedError):
            agent.build_prompt({})

    def test_parse_output_default(self):
        """Default parse_output should return raw and agent fields."""
        agent = MarketingBaseAgent("opportunity_analyst")
        result = agent.parse_output("some raw output", {"topic": "test"})
        assert "raw" in result
        assert result["raw"] == "some raw output"
        assert "agent" in result

    def test_create_agent_returns_crewai_agent(self):
        """create_agent should return a CrewAI Agent instance."""
        agent = MarketingBaseAgent("opportunity_analyst")
        crew_agent = agent.create_agent()
        assert crew_agent is not None
        assert hasattr(crew_agent, "role")

    def test_create_agent_with_tools(self):
        """create_agent should accept custom tools list."""
        agent = MarketingBaseAgent("risk_controller")
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        crew_agent = agent.create_agent(tools=[mock_tool])
        assert crew_agent is not None
