"""
Tests for configuration loading and validation.
"""

import os
import sys
import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


class TestConfig:
    """Test suite for config.yaml structure and values."""

    @pytest.fixture
    def config(self):
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config.yaml"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_config_has_llm_section(self, config):
        assert "llm" in config
        assert "provider" in config["llm"]

    def test_config_has_decision_section(self, config):
        assert "decision" in config
        assert "opportunity_threshold" in config["decision"]
        assert "risk_tolerance" in config["decision"]
        assert "debate_rounds" in config["decision"]

    def test_config_has_all_agents(self, config):
        assert "agents" in config
        expected_agents = [
            "opportunity_analyst",
            "risk_controller",
            "proscons_analyst",
            "devil_advocate",
            "competitive_analyst",
            "strategy_synthesizer",
        ]
        for agent in expected_agents:
            assert agent in config["agents"], f"Missing agent: {agent}"

    def test_each_agent_has_required_fields(self, config):
        for agent_key, agent_config in config["agents"].items():
            assert "role" in agent_config, f"{agent_key} missing 'role'"
            assert "goal" in agent_config, f"{agent_key} missing 'goal'"
            assert "backstory" in agent_config, f"{agent_key} missing 'backstory'"

    def test_decision_thresholds_are_numeric(self, config):
        decision = config["decision"]
        assert isinstance(decision["opportunity_threshold"], (int, float))
        assert isinstance(decision["risk_tolerance"], (int, float))
        assert isinstance(decision["confidence_threshold"], (int, float))

    def test_anti_hallucination_section(self, config):
        assert "anti_hallucination" in config
        assert "confidence_threshold" in config["anti_hallucination"]
        assert "disclaimer" in config["anti_hallucination"]

    def test_llm_provider_is_valid(self, config):
        valid_providers = ["spark", "dify"]
        assert config["llm"]["provider"] in valid_providers
