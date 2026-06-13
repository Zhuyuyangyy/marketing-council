"""
MarketingCouncil - Pytest Configuration & Shared Fixtures
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


@pytest.fixture
def mock_config():
    """Provide a mock config dict matching config.yaml structure."""
    return {
        "llm": {
            "provider": "spark",
            "model": "generalv3.5",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dify": {
                "enabled": False,
                "api_url": "http://localhost/v1",
                "api_key": "",
                "workflow_id": "",
            },
        },
        "decision": {
            "opportunity_threshold": 60,
            "risk_tolerance": 60,
            "debate_rounds": 3,
            "confidence_threshold": 50,
        },
        "agents": {
            "opportunity_analyst": {
                "role": "Market Opportunity Analyst",
                "goal": "Identify market opportunities",
                "backstory": "Expert in PEST/SWOT/STP analysis.",
                "frameworks": ["PEST", "SWOT", "STP"],
                "output_schema": "opportunity_score, opportunity_points[]",
            },
            "risk_controller": {
                "role": "Risk Controller",
                "goal": "Evaluate risks",
                "backstory": "Risk management expert.",
                "risk_categories": ["Policy", "Financial", "Operational"],
                "output_schema": "risk_level, risk_score, risk_items[]",
            },
            "proscons_analyst": {
                "role": "Pros/Cons Analyst",
                "goal": "Quantify pros and cons",
                "backstory": "Balanced scorecard expert.",
                "output_schema": "pros[], cons[], net_score",
            },
            "devil_advocate": {
                "role": "Devil's Advocate",
                "goal": "Challenge assumptions",
                "backstory": "Philosophical thinker.",
                "questioning_angles": [
                    "Assumption validity",
                    "Causal logic",
                    "Representative bias",
                ],
                "output_schema": "challenges[], weakest_assumption, blind_spots[]",
            },
            "competitive_analyst": {
                "role": "Competitive Analyst",
                "goal": "Analyze competition",
                "backstory": "Competitive intelligence expert.",
                "frameworks": ["Porter Five Forces"],
                "output_schema": "competitive_intensity, competitive_threats[]",
            },
            "strategy_synthesizer": {
                "role": "Strategy Synthesizer",
                "goal": "Final decision",
                "backstory": "Strategic executive.",
                "decision_labels": [
                    "STRONG-GO",
                    "CONDITIONAL-GO",
                    "HOLD",
                    "STOP",
                ],
                "output_schema": "decision, confidence, summary",
            },
        },
        "anti_hallucination": {
            "confidence_threshold": 0.6,
            "require_source": True,
            "disclaimer": "This analysis is AI-generated for reference only.",
        },
    }


@pytest.fixture
def sample_topic():
    """Provide a sample marketing topic for tests."""
    return "Launch a new cold-brew coffee brand targeting young professionals in tier-1 cities, budget 2M CNY, 3-month campaign"


@pytest.fixture
def sample_round1_results():
    """Provide mock Round 1 analysis results."""
    return {
        "opportunity_analyst": {
            "opportunity_score": 78,
            "opportunity_points": [
                "Coffee market growing 15% YoY",
                "Young professionals underserved",
            ],
            "window_period": "6-12 months",
            "target_segment": "25-35 urban professionals",
            "market_size": "50B CNY",
            "growth_potential": "High",
            "agent": "Market Opportunity Analyst",
        },
        "risk_controller": {
            "risk_level": "Medium",
            "risk_score": 52,
            "risk_items": [
                {
                    "category": "Financial",
                    "severity": "Medium",
                    "probability": "Medium",
                    "impact": "CAC may exceed budget",
                }
            ],
            "agent": "Risk Controller",
        },
        "proscons_analyst": {
            "pros": [{"title": "Growing market", "weight": 8}],
            "cons": [{"title": "High competition", "severity": 7}],
            "net_score": 12,
            "net_verdict": "Advantages outweigh disadvantages",
            "agent": "Pros/Cons Analyst",
        },
        "competitive_analyst": {
            "competitive_intensity": "High",
            "timing_assessment": {
                "is_good_timing": True,
                "window_status": "Window open",
            },
            "competitive_threats": [],
            "agent": "Competitive Analyst",
        },
        "devil_advocate": {
            "challenges": [
                {
                    "question": "Is the growth assumption realistic?",
                    "difficulty": "High",
                    "implication": "Budget overrun",
                }
            ],
            "weakest_assumption": "Market growth rate assumption",
            "blind_spots": ["Supply chain risk"],
            "agent": "Devil's Advocate",
        },
    }


@pytest.fixture
def sample_round2_results():
    """Provide mock Round 2 cross-examination results."""
    return {
        "devil_advocate": {
            "challenges": [
                {
                    "question": "What if a major competitor responds within 2 weeks?",
                    "difficulty": "High",
                    "implication": "Market share erosion",
                }
            ],
            "weakest_assumption": "Competitive response time assumption",
            "probable_failure_reason": "CAC exceeds LTV in first 3 months",
            "blind_spots": ["Regulatory changes"],
            "agent": "Devil's Advocate",
        }
    }


@pytest.fixture
def mock_llm():
    """Provide a mock LLM instance."""
    from app.core.llm_factory import _create_mock_llm

    return _create_mock_llm()
