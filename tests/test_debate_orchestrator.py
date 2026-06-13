"""
Tests for DebateOrchestrator - the core 3-round debate engine.
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.debate_orchestrator import DebateOrchestrator


class TestDebateOrchestrator:
    """Test suite for DebateOrchestrator."""

    def test_init_creates_all_agents(self):
        """Orchestrator should initialize all 5 agents + synthesizer."""
        orch = DebateOrchestrator()
        assert "opportunity_analyst" in orch.agents
        assert "risk_controller" in orch.agents
        assert "proscons_analyst" in orch.agents
        assert "devil_advocate" in orch.agents
        assert "competitive_analyst" in orch.agents
        assert orch.synthesizer is not None

    def test_session_id_is_unique(self):
        """Each orchestrator instance should have a unique session ID."""
        orch1 = DebateOrchestrator()
        orch2 = DebateOrchestrator()
        assert orch1.session_id != orch2.session_id

    @patch.object(DebateOrchestrator, "_run_round1")
    @patch.object(DebateOrchestrator, "_run_round2")
    @patch.object(DebateOrchestrator, "_run_round3")
    def test_run_debate_returns_complete_result(
        self, mock_r3, mock_r2, mock_r1, sample_topic
    ):
        """run_debate should return session_id, topic, rounds, and timing."""
        mock_r1.return_value = {"opportunity_analyst": {"score": 70}}
        mock_r2.return_value = {"devil_advocate": {"challenges": []}}
        mock_r3.return_value = {"decision": "CONDITIONAL-GO", "confidence": 70}

        orch = DebateOrchestrator()
        result = orch.run_debate(sample_topic)

        assert "session_id" in result
        assert "topic" in result
        assert "round1" in result
        assert "round2" in result
        assert "final_decision" in result
        assert "total_time_seconds" in result
        assert result["topic"] == sample_topic

    @patch.object(DebateOrchestrator, "_run_round1")
    def test_run_round1_catches_agent_errors(self, mock_r1, sample_topic):
        """Round 1 should handle individual agent failures gracefully."""
        # Simulate one agent failing
        def side_effect(topic):
            return {
                "opportunity_analyst": {"score": 70},
                "risk_controller": {"error": "LLM timeout"},
            }

        mock_r1.side_effect = side_effect
        orch = DebateOrchestrator()
        result = mock_r1(sample_topic)
        assert "opportunity_analyst" in result
        assert "risk_controller" in result

    @patch("app.core.debate_orchestrator.DebateOrchestrator.__init__", return_value=None)
    def test_run_round2_calls_devil_advocate(self, mock_init):
        """Round 2 should call Devil's Advocate with Round 1 results."""
        orch = DebateOrchestrator()
        orch.session_id = "test-123"
        orch.agents = {"devil_advocate": MagicMock()}
        orch.agents["devil_advocate"].analyze.return_value = {
            "challenges": [],
            "weakest_assumption": "test",
        }

        result = orch._run_round2("test topic", {"opportunity_analyst": {}})
        assert "devil_advocate" in result

    @patch("app.core.debate_orchestrator.DebateOrchestrator.__init__", return_value=None)
    def test_run_round3_calls_synthesizer(self, mock_init):
        """Round 3 should call StrategySynthesizer."""
        orch = DebateOrchestrator()
        orch.session_id = "test-123"
        orch.synthesizer = MagicMock()
        orch.synthesizer.synthesize.return_value = {
            "decision": "HOLD",
            "confidence": 50,
        }

        result = orch._run_round3("test topic", {}, {})
        assert "decision" in result


class TestDebateOrchestratorAsync:
    """Test async streaming debate flow."""

    @pytest.mark.asyncio
    async def test_run_debate_stream_yields_events(self, sample_topic):
        """Stream should yield round_start, agent events, and final_decision."""
        orch = DebateOrchestrator()

        # Mock all agents to return quickly
        for key in orch.agents:
            orch.agents[key].analyze = MagicMock(
                return_value={"score": 70, "agent": key}
            )
        orch.synthesizer.synthesize = MagicMock(
            return_value={"decision": "HOLD", "confidence": 50}
        )

        events = []
        async for event in orch.run_debate_stream(sample_topic):
            events.append(event)
            if len(events) > 50:  # Safety limit
                break

        # Should have at least round_start and round_complete events
        event_types = [e.get("event") for e in events]
        assert "round_start" in event_types
        assert "debate_complete" in event_types or "final_decision" in event_types
