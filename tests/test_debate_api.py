"""
Tests for Debate API routes (FastAPI endpoints).
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestRootEndpoints:
    """Test basic service endpoints."""

    def test_root_returns_service_info(self):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "MarketingCouncil" in data["name"]
        assert "endpoints" in data

    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestDebateEndpoints:
    """Test debate API endpoints."""

    def test_list_agents(self):
        resp = client.get("/api/v1/debate/agents")
        assert resp.status_code == 200
        data = resp.json()
        assert "agents" in data
        assert data["total"] == 6
        agent_keys = [a["key"] for a in data["agents"]]
        assert "opportunity_analyst" in agent_keys
        assert "risk_controller" in agent_keys
        assert "strategy_synthesizer" in agent_keys

    def test_demo_endpoint(self):
        resp = client.get("/api/v1/debate/demo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "demo-session-001"
        assert "round1" in data
        assert "round2" in data
        assert "final_decision" in data
        assert data["final_decision"]["decision"] == "CONDITIONAL-GO"

    def test_debate_empty_topic_rejected(self):
        resp = client.post("/api/v1/debate", json={"topic": ""})
        assert resp.status_code == 422  # Validation error (min_length=5)

    def test_debate_short_topic_rejected(self):
        resp = client.post("/api/v1/debate", json={"topic": "ab"})
        assert resp.status_code == 422

    @patch("app.routers.debate.DebateOrchestrator")
    def test_debate_sync_endpoint(self, MockOrchestrator):
        """Sync debate endpoint should return complete results."""
        mock_orch = MagicMock()
        mock_orch.run_debate.return_value = {
            "session_id": "test-123",
            "topic": "Test marketing campaign",
            "round1": {"opportunity_analyst": {"score": 70}},
            "round2": {"devil_advocate": {"challenges": []}},
            "final_decision": {"decision": "HOLD", "confidence": 50},
            "total_time_seconds": 5.0,
        }
        MockOrchestrator.return_value = mock_orch

        resp = client.post(
            "/api/v1/debate",
            json={"topic": "Test marketing campaign for new product launch"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert "final_decision" in data


class TestV2Endpoints:
    """Test V2 marketing API endpoints."""

    def test_debate_scenario(self):
        resp = client.post(
            "/api/v2/debate/scenario",
            json={"topic": "New product launch strategy"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "scenario_id" in data
        assert "rounds" in data
        assert len(data["rounds"]) == 3

    def test_debate_scenario_custom_params(self):
        resp = client.post(
            "/api/v2/debate/scenario",
            json={
                "topic": "Market entry",
                "num_agents": 4,
                "rounds": 2,
                "debate_mode": "adversarial",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["num_agents"] == 4
        assert len(data["rounds"]) == 2

    def test_sentiment_analysis(self):
        resp = client.post(
            "/api/v2/sentiment/analyze",
            json={"texts": ["Great product!", "Terrible service", "It's okay"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["document_count"] == 3
        assert "sentiment_distribution" in data

    def test_sentiment_with_aspects(self):
        resp = client.post(
            "/api/v2/sentiment/analyze",
            json={"texts": ["Good quality but expensive"], "include_aspect": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["detailed_results"]) == 1
        assert "aspects" in data["detailed_results"][0]

    def test_competitor_intelligence(self):
        resp = client.post(
            "/api/v2/competitor/intelligence",
            json={
                "industry": "Beverages",
                "product_category": "Coffee",
                "competitor_names": ["Starbucks", "Luckin"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["competitors"]) == 2
        assert "recommendation" in data

    def test_campaign_optimize(self):
        resp = client.post(
            "/api/v2/campaign/optimize",
            json={
                "campaign_type": "launch",
                "target_audience": "Young professionals",
                "budget_level": "medium",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_budget"] == 200000
        assert "channel_allocation" in data
        assert "expected_roi" in data

    def test_campaign_optimize_custom_channels(self):
        resp = client.post(
            "/api/v2/campaign/optimize",
            json={
                "campaign_type": "retention",
                "target_audience": "Existing customers",
                "budget_level": "high",
                "channel_mix": {"email": 0.5, "social": 0.3, "sms": 0.2},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_budget"] == 1000000

    def test_brand_positioning(self):
        resp = client.post(
            "/api/v2/brand/positioning",
            json={
                "brand_name": "TestBrand",
                "product_description": "Premium coffee",
                "target_segments": ["Young professionals"],
                "competitor_tags": ["premium", "urban"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["brand_name"] == "TestBrand"
        assert "differentiation_score" in data
        assert "positioning" in data
