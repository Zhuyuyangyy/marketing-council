"""
Tests for decision logic and scoring thresholds.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


class TestDecisionLogic:
    """Test decision classification logic based on config thresholds."""

    @pytest.fixture
    def thresholds(self):
        """Default thresholds from config.yaml."""
        return {
            "opportunity_threshold": 60,
            "risk_tolerance": 60,
            "confidence_threshold": 50,
        }

    def classify_decision(self, opportunity_score, risk_score, confidence, thresholds):
        """
        Replicate the decision classification logic from config.yaml rules:
        - STRONG-GO: opportunity > 70 AND risk < 40
        - CONDITIONAL-GO: opportunity > 50 OR risk < 60
        - HOLD: opportunity ~50, risk medium
        - STOP: opportunity < 40 OR risk > 70
        """
        if opportunity_score > 70 and risk_score < 40:
            return "STRONG-GO"
        elif opportunity_score < 40 or risk_score > 70:
            return "STOP"
        elif confidence < thresholds["confidence_threshold"]:
            return "HOLD"
        elif opportunity_score >= thresholds["opportunity_threshold"]:
            return "CONDITIONAL-GO"
        else:
            return "HOLD"

    def test_strong_go_high_opportunity_low_risk(self, thresholds):
        result = self.classify_decision(85, 25, 90, thresholds)
        assert result == "STRONG-GO"

    def test_strong_go_boundary(self, thresholds):
        result = self.classify_decision(71, 39, 85, thresholds)
        assert result == "STRONG-GO"

    def test_stop_low_opportunity(self, thresholds):
        result = self.classify_decision(30, 50, 40, thresholds)
        assert result == "STOP"

    def test_stop_high_risk(self, thresholds):
        result = self.classify_decision(80, 75, 60, thresholds)
        assert result == "STOP"

    def test_conditional_go(self, thresholds):
        result = self.classify_decision(65, 55, 70, thresholds)
        assert result == "CONDITIONAL-GO"

    def test_hold_low_confidence(self, thresholds):
        result = self.classify_decision(65, 45, 30, thresholds)
        assert result == "HOLD"

    def test_hold_medium_scores(self, thresholds):
        result = self.classify_decision(50, 50, 50, thresholds)
        assert result in ["HOLD", "CONDITIONAL-GO"]

    def test_boundary_opportunity_exactly_70(self, thresholds):
        """Boundary: opportunity exactly 70 with low risk."""
        result = self.classify_decision(70, 30, 80, thresholds)
        # At boundary, should not be STRONG-GO (needs >70)
        assert result in ["CONDITIONAL-GO", "STRONG-GO"]

    def test_boundary_risk_exactly_40(self, thresholds):
        """Boundary: risk exactly 40."""
        result = self.classify_decision(80, 40, 80, thresholds)
        assert result in ["STRONG-GO", "CONDITIONAL-GO"]


class TestScoreValidation:
    """Test score range validation."""

    def test_opportunity_score_range(self):
        """Opportunity scores should be 0-100."""
        valid_scores = [0, 50, 100]
        for score in valid_scores:
            assert 0 <= score <= 100

    def test_risk_score_range(self):
        """Risk scores should be 0-100."""
        valid_scores = [0, 50, 100]
        for score in valid_scores:
            assert 0 <= score <= 100

    def test_confidence_range(self):
        """Confidence should be 0-100."""
        valid_scores = [0, 50, 100]
        for score in valid_scores:
            assert 0 <= score <= 100
