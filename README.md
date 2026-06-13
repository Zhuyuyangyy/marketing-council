# MarketingCouncil

**Multi-Agent Strategic Debate System for Marketing Decision-Making**

A multi-agent AI system that simulates a structured strategic council for evaluating marketing proposals. Six specialized AI agents engage in a 3-round debate protocol -- independent analysis, cross-examination, and strategic synthesis -- to produce quantified risk-opportunity assessments with actionable go/no-go decisions.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Benchmarks](#benchmarks)
- [Research](#research)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

---

## Overview

Marketing decisions -- new product launches, campaign strategies, market entries -- are typically made by individuals or small teams with limited perspective. Cognitive biases, incomplete information, and time pressure lead to suboptimal outcomes. MarketingCouncil addresses this by deploying a team of AI agents that each bring a distinct analytical lens, then stress-test each other's conclusions through structured debate.

The system implements a 3-round debate protocol:

1. **Round 1: Parallel Independent Analysis** -- Five specialist agents simultaneously analyze the marketing proposal from their unique perspective (opportunity, risk, pros/cons, competition, market timing).
2. **Round 2: Cross-Examination** -- A Devil's Advocate agent challenges the assumptions, logic, and blind spots identified in Round 1.
3. **Round 3: Strategic Synthesis** -- A Strategy Synthesizer agent integrates all perspectives into a final decision: STRONG-GO, CONDITIONAL-GO, HOLD, or STOP, with confidence scores and next-step recommendations.

The system supports real-time SSE streaming, allowing users to watch each agent's reasoning process as it unfolds.

---

## Key Features

### Six Specialized AI Agents

| Agent | Role | Focus |
|-------|------|-------|
| Opportunity Analyst | Market opportunity assessment | Market size, growth potential, timing windows |
| Risk Controller | Risk evaluation | Policy, financial, operational, reputational, technical risks |
| Pros/Cons Analyst | Quantitative trade-off analysis | Weighted scoring of positive and negative factors |
| Devil's Advocate | Adversarial challenge | Assumption testing, blind spot detection, weak logic |
| Competitive Analyst | Competitive landscape | Competitor reactions, entry barriers, market timing |
| Strategy Synthesizer | Final decision maker | Integrates all views into actionable recommendation |

### 3-Round Debate Protocol

- **Round 1**: 5 agents run in parallel for fast, independent analysis
- **Round 2**: Devil's Advocate cross-examines Round 1 outputs, identifying the weakest assumptions
- **Round 3**: Strategy Synthesizer produces a final verdict with confidence score, conditions, and next steps

### Decision Labels

| Decision | Condition | Meaning |
|----------|-----------|---------|
| STRONG-GO | Opportunity >70 AND Risk <40 | Proceed with full confidence |
| CONDITIONAL-GO | Meets threshold with caveats | Proceed if specific conditions are met |
| HOLD | Insufficient information | Gather more data before deciding |
| STOP | Risk too high or opportunity too low | Do not proceed |

### Real-Time Streaming

- Server-Sent Events (SSE) for live debate visualization
- Per-agent status cards with real-time updates
- Demo mode for offline preview without API keys

### Framework-Agnostic LLM Backend

- iFlytek Spark (default)
- Dify workflow integration
- OpenAI-compatible endpoints
- Mock mode for development and demonstration

---

## Architecture

```
+----------------------------------------------------------+
|                    Frontend (Vue3 SPA)                     |
|   Agent Cards  |  Debate Timeline  |  Decision Panel      |
|   SSE Streaming  |  Demo Mode  |  Dark Professional Theme |
+----------------------------+-----------------------------+
                             | HTTP + SSE
                             v
+----------------------------------------------------------+
|              FastAPI Backend (Port 8009)                   |
|                                                           |
|  +------------------------------------------------------+|
|  |              DebateOrchestrator                       ||
|  |                                                      ||
|  |  Round 1 (Parallel):                                 ||
|  |  +----------------+  +----------------+              ||
|  |  | Opportunity    |  | Risk Controller|              ||
|  |  | Analyst        |  |                |              ||
|  |  +----------------+  +----------------+              ||
|  |  +----------------+  +----------------+              ||
|  |  | Pros/Cons      |  | Competitive    |              ||
|  |  | Analyst        |  | Analyst        |              ||
|  |  +----------------+  +----------------+              ||
|  |                                                      ||
|  |  Round 2 (Cross-Examination):                        ||
|  |  +------------------+                                ||
|  |  | Devil's Advocate |  <- challenges all Round 1     ||
|  |  +------------------+                                ||
|  |                                                      ||
|  |  Round 3 (Synthesis):                                ||
|  |  +------------------------+                          ||
|  |  | Strategy Synthesizer   |  -> FINAL DECISION       ||
|  |  +------------------------+                          ||
|  +------------------------------------------------------+|
|                                                           |
|  +------------------+  +------------------+               |
|  | LLM Factory      |  | Config (YAML)   |               |
|  | Spark/Dify/Mock  |  | Agent profiles  |               |
|  +------------------+  | Decision params |               |
|                        +------------------+               |
+----------------------------------------------------------+
```

**Debate Flow:**

```
User submits marketing proposal
        |
        v
+---------------------------+
|  Round 1: Parallel        |
|  5 agents analyze         |
|  independently            |
+---------------------------+
        |
        v
+---------------------------+
|  Round 2: Cross-Exam      |
|  Devil's Advocate         |
|  challenges assumptions   |
+---------------------------+
        |
        v
+---------------------------+
|  Round 3: Synthesis       |
|  Strategy Synthesizer     |
|  produces final verdict   |
+---------------------------+
        |
        v
  STRONG-GO / CONDITIONAL-GO / HOLD / STOP
  + Confidence Score
  + Conditions
  + Next Steps
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | FastAPI + Uvicorn | Async REST + SSE server |
| Multi-Agent | CrewAI + LangChain | Agent orchestration framework |
| LLM (Default) | iFlytek Spark (generalv3.5) | Chinese-language LLM |
| LLM (Alt) | Dify Workflow | Visual workflow-based LLM |
| LLM (Alt) | OpenAI-compatible | Any OpenAI API-compatible provider |
| Frontend | Vue 3 + Axios (single HTML) | Zero-build interactive UI |
| Config | YAML | Agent definitions, decision parameters |
| Logging | Loguru | Structured logging with color |
| Protocol | REST + SSE | Sync API + real-time streaming |
| Container | Docker + Docker Compose | Production deployment |
| CI/CD | GitHub Actions | Lint, test, build pipeline |
| Testing | Pytest + Coverage | Unit & integration tests |

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
cd marketing-council
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API credentials:
# SPARK_APP_ID=your_app_id
# SPARK_API_KEY=your_api_key
# SPARK_API_SECRET=your_api_secret
```

Or configure via `config.yaml` for Dify workflow integration:

```yaml
llm:
  provider: "dify"  # spark | dify
  dify:
    api_url: "http://localhost/v1"
    api_key: "your-dify-api-key"
```

### Run

```bash
# Start backend (port 8009)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009

# Open frontend
# Navigate to frontend/index.html in your browser
```

### Demo Mode (No API Key Required)

```bash
# Run interactive demo
python run_demo.py --mock

# List all agents
python run_demo.py --list-agents

# Test API connection
python run_demo.py --test-api
```

### Docker Deployment

```bash
# Build and run
docker build -t marketing-council .
docker run -p 8009:8009 --env-file .env marketing-council

# Or use docker-compose
docker-compose up -d
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=backend --cov-report=term-missing

# Run specific test file
pytest tests/test_debate_orchestrator.py -v
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/api/v1/debate` | Start debate (sync, full result) |
| POST | `/api/v1/debate/stream` | Start debate (SSE streaming) |
| GET | `/api/v1/debate/demo` | Demo mode (no real LLM) |
| GET | `/api/v1/debate/agents` | Agent role descriptions |
| POST | `/api/v2/debate/scenario` | Create debate scenario |
| POST | `/api/v2/sentiment/analyze` | Aspect-level sentiment analysis |
| POST | `/api/v2/competitor/intelligence` | Competitive SWOT analysis |
| POST | `/api/v2/campaign/optimize` | Campaign budget optimization |
| POST | `/api/v2/brand/positioning` | Brand differentiation analysis |

---

## Project Structure

```
marketing-council/
├── backend/
│   └── app/
│       ├── main.py                       # FastAPI entry point (port 8009)
│       ├── agents/
│       │   ├── base_agent.py             # Base agent class
│       │   ├── opportunity_analyst.py    # Market opportunity analysis
│       │   ├── risk_controller.py        # Risk assessment
│       │   ├── proscons_analyst.py       # Pros/cons quantification
│       │   ├── devil_advocate.py         # Adversarial challenge
│       │   ├── competitive_analyst.py    # Competitive landscape
│       │   └── strategy_synthesizer.py   # Final decision synthesis
│       ├── core/
│       │   ├── debate_orchestrator.py    # 3-round debate orchestrator
│       │   ├── llm_factory.py            # LLM provider factory (Spark/Dify)
│       │   ├── llm_spark.py              # iFlytek Spark wrapper
│       │   ├── llm_spark_mock.py         # Mock LLM for development
│       │   └── llm_spark_crewai.py       # CrewAI adapter for Spark
│       └── routers/
│           ├── debate.py                 # Debate API routes
│           └── marketing_v2.py           # Extended marketing routes
├── tests/                                # Comprehensive test suite
│   ├── conftest.py                       # Shared fixtures
│   ├── test_base_agent.py                # Base agent tests
│   ├── test_opportunity_analyst.py       # Opportunity analyst tests
│   ├── test_risk_controller.py           # Risk controller tests
│   ├── test_proscons_analyst.py          # Pros/cons tests
│   ├── test_devil_advocate.py            # Devil's advocate tests
│   ├── test_competitive_analyst.py       # Competitive analyst tests
│   ├── test_strategy_synthesizer.py      # Strategy synthesizer tests
│   ├── test_debate_orchestrator.py       # Orchestrator tests
│   ├── test_llm_factory.py              # LLM factory tests
│   ├── test_llm_spark.py                # Spark LLM tests
│   ├── test_llm_spark_crewai.py         # CrewAI adapter tests
│   ├── test_debate_api.py               # API endpoint tests
│   ├── test_config.py                   # Configuration tests
│   └── test_decision_logic.py           # Decision logic tests
├── docs/
│   ├── ARCHITECTURE.md                   # System architecture
│   ├── API_REFERENCE.md                  # API documentation
│   ├── DEPLOYMENT.md                     # Deployment guide
│   └── DEMO_GUIDE.md                     # Demo instructions
├── frontend/
│   ├── index.html                        # Main Vue3 SPA
│   └── demo_sse.html                     # SSE streaming demo
├── config.yaml                           # Agent definitions & LLM config
├── Dockerfile                            # Production container
├── docker-compose.yml                    # Multi-service deployment
├── nginx.conf                            # Reverse proxy config
├── TODO.md                               # Innovation backlog
├── INNOVATION_ROADMAP.md                 # Patent & innovation roadmap
├── run_demo.py                           # Interactive demo script
├── requirements.txt
├── start.bat                             # Windows startup
├── start.sh                              # Linux startup
└── README.md
```

---

## Benchmarks

| Metric | Value |
|--------|-------|
| Number of Agents | 6 specialized agents |
| Debate Rounds | 3 (parallel -> cross-exam -> synthesis) |
| Decision Categories | 4 (STRONG-GO, CONDITIONAL-GO, HOLD, STOP) |
| Confidence Scoring | 0-100 scale with threshold-based filtering |
| Risk Categories | 5 (Policy, Financial, Operational, Reputational, Technical) |
| Analysis Frameworks | PEST, SWOT, STP, Porter's Five Forces, Balanced Scorecard |
| Streaming Protocol | SSE (Server-Sent Events) |
| LLM Providers | 3 (iFlytek Spark, Dify, OpenAI-compatible) |
| Demo Mode | Fully functional without API keys |

---

## Research

### Multi-Agent Debate for Decision-Making

MarketingCouncil draws on research in multi-agent debate systems and structured argumentation:

**Agent Design Philosophy:**
Each agent is designed with a distinct "cognitive role" inspired by organizational decision-making theory:
- **Opportunity Analyst**: Applies PEST/SWOT/STP frameworks for systematic market assessment
- **Risk Controller**: Multi-dimensional risk taxonomy (policy, financial, operational, reputational, technical)
- **Devil's Advocate**: Implements "red team" methodology, challenging assumptions through structured questioning angles (assumption validity, causal logic, representative bias, sunk cost, path dependency)
- **Strategy Synthesizer**: Synthesizes conflicting viewpoints using a weighted decision matrix

**Anti-Hallucination Safeguards:**
- Confidence threshold filtering (configurable, default 0.6)
- Source requirement flag for factual claims
- Built-in disclaimer for AI-generated analysis

**Decision Calibration:**
- Opportunity score threshold: 60 (configurable)
- Risk tolerance ceiling: 60 (configurable)
- Confidence threshold: 50 (configurable)
- Decisions below threshold are flagged as "insufficient confidence"

### References

- Irving, G., et al. (2018). AI Safety via Debate. *arXiv:1805.00899*.
- Du, Y., et al. (2023). Improving Factuality and Reasoning in Language Models through Multiagent Debate. *arXiv:2305.14325*.
- Liang, T., et al. (2023). Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate. *arXiv:2305.19118*.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

---

## Roadmap

See [TODO.md](TODO.md) for the full backlog and [INNOVATION_ROADMAP.md](INNOVATION_ROADMAP.md) for patent-ready innovations.

### Near-Term (Q3 2026)

- [ ] Persistent debate session storage and replay
- [ ] Smart marketing strategy auto-generation
- [ ] User persona-driven analysis
- [ ] ROI prediction model

### Mid-Term (Q4 2026)

- [ ] Multi-language debate support (English, Japanese)
- [ ] A/B test automation from debate outcomes
- [ ] Real-time market data API integration
- [ ] Collaborative multi-user debate sessions

### Long-Term (Q1 2027)

- [ ] SaaS multi-tenant platform
- [ ] Agent fine-tuning on domain-specific data
- [ ] No-code agent builder UI
- [ ] Decision outcome tracking system

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

- Issues: [GitHub Issues](https://github.com/yourusername/marketing-council/issues)
- Discussions: Open an issue with the `discussion` tag

---

*Six perspectives. One decision. Zero blind spots.*
