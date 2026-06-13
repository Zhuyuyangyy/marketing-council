# MarketingCouncil Architecture

## System Overview

MarketingCouncil is a multi-agent AI system that simulates a structured strategic council for evaluating marketing proposals. Six specialized AI agents engage in a 3-round debate protocol to produce quantified risk-opportunity assessments.

## Core Components

### 1. Agent Layer (`backend/app/agents/`)

Each agent is a specialized AI persona with a defined role, analytical framework, and output schema.

```
MarketingBaseAgent (base_agent.py)
    |
    +-- OpportunityAnalyst     # Market opportunity assessment (PEST/SWOT/STP)
    +-- RiskController         # Multi-dimensional risk evaluation
    +-- ProsConsAnalyst        # Quantitative trade-off analysis
    +-- DevilAdvocate          # Adversarial challenge & assumption testing
    +-- CompetitiveAnalyst     # Competitive landscape & timing
    +-- StrategySynthesizer    # Final decision integration
```

**Agent Design Principles:**
- Each agent inherits from `MarketingBaseAgent` for consistent LLM injection and config loading
- Agents are configured via `config.yaml` (role, goal, backstory, frameworks)
- Each agent implements `analyze()` -> `parse_output()` for structured result extraction
- Output parsing uses regex-based JSON extraction with graceful fallbacks

### 2. Orchestration Layer (`backend/app/core/`)

```
DebateOrchestrator (debate_orchestrator.py)
    |
    +-- Round 1: 5 agents run in parallel (independent analysis)
    +-- Round 2: Devil's Advocate cross-examines Round 1 outputs
    +-- Round 3: Strategy Synthesizer integrates all perspectives
```

**Debate Flow:**
1. User submits a marketing proposal (topic string)
2. Round 1: Each of 5 specialist agents independently analyzes the topic
3. Round 2: Devil's Advocate receives all Round 1 outputs and challenges assumptions
4. Round 3: Strategy Synthesizer receives all outputs and produces a final verdict

**Streaming Support:**
- `run_debate()` for synchronous execution
- `run_debate_stream()` for async SSE streaming with per-agent status events

### 3. LLM Layer (`backend/app/core/`)

```
llm_factory.py (Factory Pattern)
    |
    +-- Priority: Mock (no key) > Dify > Spark
    |
    +-- SparkChatModel (llm_spark_mock.py)   # iFlytek Spark API wrapper
    +-- CrewAISparkLLM (llm_spark_crewai.py) # CrewAI BaseLLM adapter
    +-- MockLLM (inline in factory)           # Demo/development mode
```

**Provider Selection Logic:**
1. No API keys configured -> MockLLM (demo mode)
2. Dify provider configured -> DifyWorkflowLLM
3. Spark API keys present -> SparkChatModel via CrewAISparkLLM
4. Any initialization failure -> fallback to MockLLM

### 4. API Layer (`backend/app/routers/`)

```
FastAPI Application (main.py)
    |
    +-- /api/v1/debate         # Core debate endpoints
    |   +-- POST /             # Sync debate
    |   +-- POST /stream       # SSE streaming debate
    |   +-- GET /demo          # Demo mode
    |   +-- GET /agents        # Agent listing
    |
    +-- /api/v2/               # Extended marketing analysis
        +-- POST /debate/scenario
        +-- POST /sentiment/analyze
        +-- POST /competitor/intelligence
        +-- POST /campaign/optimize
        +-- POST /brand/positioning
```

### 5. Frontend (`frontend/`)

Single-page Vue 3 application with:
- Dark professional theme
- Real-time agent status cards
- SSE streaming visualization
- Decision panel with confidence bars
- Demo mode (connects to backend `/demo` endpoint)

## Data Flow

```
User Input (topic)
    |
    v
FastAPI Router
    |
    v
DebateOrchestrator
    |
    +-- Round 1 (parallel)
    |   |-- Agent.analyze(topic) -> LLM -> parse_output()
    |   |-- Agent.analyze(topic) -> LLM -> parse_output()
    |   |-- ...
    |
    +-- Round 2
    |   |-- DevilAdvocate.analyze(topic, {round1_results})
    |
    +-- Round 3
    |   |-- StrategySynthesizer.synthesize(topic, round1, round2)
    |
    v
Structured Decision Response
    {
        decision: STRONG-GO | CONDITIONAL-GO | HOLD | STOP,
        confidence: 0-100,
        conditions: [...],
        key_concerns: [...],
        next_steps: [...]
    }
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| YAML-based config | Easy agent customization without code changes |
| Regex JSON parsing | LLM outputs often include extra text around JSON |
| Mock fallback | Enables demo/development without API keys |
| SSE streaming | Real-time visualization of agent reasoning |
| CrewAI framework | Standardized agent orchestration with tool support |
| FastAPI | Async support for parallel agent execution |
