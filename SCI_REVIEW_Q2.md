# SCI Q2 Code Review: MarketingCouncil

**Date:** 2026-05-29
**Scope:** Full codebase audit (backend core, agents, routers, frontend, config)
**Reviewer:** Claude (automated multi-dimensional analysis)

---

## 1. Seven-Dimensional Scoring

| # | Dimension | Score (0-10) | Summary |
|---|-----------|:---:|---------|
| 1 | **Code Quality & Architecture** | 7.0 | Clean module separation (agents/core/routers), proper base class inheritance, YAML-driven config. Deducted for monolithic frontend HTML files (no component abstraction) and inconsistent import patterns. |
| 2 | **Correctness & Robustness** | 4.5 | Critical bug: 5 of 6 agents' `parse_output()` used fragile regex that silently discards structured arrays (pros, cons, challenges, risk_items). Only `OpportunityAnalyst` had proper JSON parsing. **FIXED in this review.** |
| 3 | **Security** | 5.0 | CORS wildcard `allow_origins=["*"]` combined with `allow_credentials=True` (violates Fetch spec, potential credential leak). `.env` file committed to repo. API keys referenced in `run_demo.py` printed to stdout. No rate limiting or auth on endpoints. |
| 4 | **Performance & Scalability** | 5.5 | `_run_round1()` iterates agents sequentially in a for-loop despite claiming "parallel" analysis. `run_debate_stream()` wraps in `asyncio.to_thread` but thread pool serializes execution. Config file re-read on every agent instantiation. No caching layer. |
| 5 | **Testability & Testing** | 4.0 | Test file exists (`test_sse_performance.py`) but no unit tests for agents, parsers, or orchestrator. Mock LLM is hardcoded text with no per-agent context. No CI/CD configuration. |
| 6 | **Documentation & Maintainability** | 6.5 | Good inline docstrings on orchestrator and agent classes. `config.yaml` is well-structured with agent role/backstory definitions. `README.md` exists. Deducted for missing API schema docs for V2 endpoints, no architecture diagram. |
| 7 | **API Design & Standards** | 6.0 | RESTful endpoints with proper Pydantic models. SSE streaming implemented correctly. Deducted: V2 endpoints return mock random data (`random.uniform`) with no real backend logic -- they are placeholder stubs masquerading as functional APIs. |

**Overall Score: 5.5 / 10**

---

## 2. Top 3 Problems

### P0 -- CRITICAL: `parse_output()` Silently Discards Structured Data (5/6 Agents)

**Severity:** Critical
**Impact:** The entire multi-agent debate pipeline produces degraded output. The `StrategySynthesizer` receives empty arrays for `pros`, `cons`, `challenges`, `risk_items`, `competitive_threats`, `key_concerns`, and `next_steps`, making the final decision based on incomplete information.

**Root Cause:**
`RiskController`, `DevilAdvocate`, `ProsConsAnalyst`, `CompetitiveAnalyst`, and `StrategySynthesizer` all used regex patterns like `re.findall(r'"title"\s*:\s*"([^"]+)"', ...)` or `re.search(r'\[[\s\S]*?\]', ...)` to extract data from LLM output. These patterns:
- Fail on multiline strings containing newlines inside JSON values
- Cannot handle escaped quotes within strings
- Silently return empty lists when patterns don't match
- Discard nested objects entirely

Only `OpportunityAnalyst` had a proper JSON parser (iterative brace-matching).

**Fix Applied:**
Added `MarketingBaseAgent.extract_json()` -- a robust 3-strategy JSON extractor (direct parse, markdown fence extraction, greedy brace matching) to the base class. All 5 affected agents now call `self.extract_json()` first, falling back to regex only when JSON parsing fails.

**Files Modified:**
- `backend/app/agents/base_agent.py` -- added `extract_json()` static method
- `backend/app/agents/risk_controller.py` -- `parse_output()` now uses JSON-first parsing
- `backend/app/agents/devil_advocate.py` -- same
- `backend/app/agents/proscons_analyst.py` -- same
- `backend/app/agents/competitive_analyst.py` -- same
- `backend/app/agents/strategy_synthesizer.py` -- same

---

### P1 -- HIGH: Round 1 Runs Agents Sequentially, Not in Parallel

**Severity:** High
**Impact:** The system advertises "5 agents in parallel" but `_run_round1()` uses a synchronous `for` loop. In `run_debate_stream()`, each agent is wrapped in `asyncio.to_thread()` but awaits them sequentially with a `for` loop, so the thread pool processes them one at a time. Total latency = sum of all agent times instead of max.

**Location:** `backend/app/core/debate_orchestrator.py`, lines 84-93 and 124-133

**Recommended Fix:**
```python
# Replace sequential loop with concurrent execution:
round1_tasks = {
    key: asyncio.to_thread(agent.analyze, topic, {})
    for key, agent in self.agents.items()
}
results = {}
for key, coro in round1_tasks.items():
    try:
        results[key] = await coro
    except Exception as e:
        results[key] = {"error": str(e), "agent": key}
```

---

### P2 -- HIGH: V2 API Endpoints Return Fake Random Data

**Severity:** High
**Impact:** All 5 endpoints under `/api/v2/` (`/sentiment/analyze`, `/competitor/intelligence`, `/campaign/optimize`, `/brand/positioning`, `/debate/scenario`) return `random.uniform()` generated values. They give the illusion of functional AI-powered analysis but produce non-deterministic, meaningless outputs. Any downstream consumer trusting these values will make bad decisions.

**Location:** `backend/app/routers/marketing_v2.py`, lines 81-189

**Recommended Fix:** Either (a) integrate these endpoints with the actual multi-agent debate engine, or (b) clearly mark them as "demo/mock" in the API response and documentation, or (c) remove them until real implementations exist.

---

## 3. Additional Observations

| Item | Detail |
|------|--------|
| **CORS misconfiguration** | `allow_origins=["*"]` + `allow_credentials=True` violates the Fetch spec. Browsers will block credentialed cross-origin requests. Should either set specific origins or disable credentials. |
| **`.env` committed** | The `.env` file is tracked in git. Should be in `.gitignore` to prevent secret leakage. |
| **Config re-read per agent** | Each of 6 agents reads `config.yaml` from disk on construction. The config should be loaded once and passed via dependency injection. |
| **No retry/backoff on LLM calls** | `SparkChatModel._call_spark_api()` makes a single attempt with a 60s timeout. Transient network failures will cause agent failures with no recovery. |
| **Frontend monolith** | Both `index.html` (725 lines) and `demo_sse.html` (570 lines) are self-contained single-file apps with inline CSS/JS. Should be extracted into proper component-based architecture for maintainability. |
| **Duplicate `SparkChatModel`** | Two separate `SparkChatModel` classes exist: `llm_spark.py` (simpler) and `llm_spark_mock.py` (fuller). The factory uses the mock version. The simpler one appears dead code. |
| **Missing `.gitignore` patterns** | No `.gitignore` file was found. Standard patterns for Python (`__pycache__/`, `*.pyc`, `.env`, `venv/`) should be added. |

---

## 4. Fix Verification

The `extract_json()` fix was applied to all 5 affected agents. The function follows a 3-tier strategy:

1. **Direct parse** -- handles clean JSON output
2. **Markdown fence extraction** -- handles ````json ... ```` blocks from LLM
3. **Greedy brace matching** -- handles prose-wrapped JSON with proper depth tracking and string-aware parsing

Each agent retains its original regex fallback for backward compatibility with non-JSON LLM responses. The fix ensures that when an LLM returns valid JSON (the expected case per the prompt templates), all structured fields are preserved and passed through to the StrategySynthesizer.
