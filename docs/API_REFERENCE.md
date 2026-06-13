# MarketingCouncil API Reference

## Base URL

```
http://localhost:8009
```

---

## V1 Endpoints - Core Debate

### POST `/api/v1/debate`

Start a synchronous marketing debate. Returns complete 3-round results.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | Yes | Marketing proposal description (5-500 chars) |
| `stream` | bool | No | Use streaming (default: true) |
| `include_round2` | bool | No | Include cross-examination (default: true) |

**Response:**

```json
{
    "session_id": "uuid",
    "topic": "...",
    "created_at": "ISO-8601",
    "round1": {
        "opportunity_analyst": { ... },
        "risk_controller": { ... },
        "proscons_analyst": { ... },
        "competitive_analyst": { ... },
        "devil_advocate": { ... }
    },
    "round2": {
        "devil_advocate": { ... }
    },
    "final_decision": {
        "decision": "STRONG-GO | CONDITIONAL-GO | HOLD | STOP",
        "confidence": 0-100,
        "conditions": [],
        "key_concerns": [],
        "next_steps": [],
        "summary": "..."
    },
    "total_time_seconds": 12.5,
    "disclaimer": "..."
}
```

### POST `/api/v1/debate/stream`

Start a streaming debate via Server-Sent Events.

**Events:**

| Event | Data |
|-------|------|
| `round_start` | `{round, message}` |
| `agent_start` | `{round, agent, role}` |
| `agent_complete` | `{round, agent, result}` |
| `round_complete` | `{round, results}` |
| `final_decision` | `{decision}` |
| `debate_complete` | `{total_time}` |
| `error` | `{message}` |
| `done` | `{}` |

### GET `/api/v1/debate/demo`

Returns a pre-built demo result without calling any LLM.

### GET `/api/v1/debate/agents`

Lists all 6 agents with their roles and round assignments.

---

## V2 Endpoints - Extended Analysis

### POST `/api/v2/debate/scenario`

Create a multi-agent debate scenario.

**Request:**

| Field | Type | Default |
|-------|------|---------|
| `topic` | string | Required |
| `num_agents` | int | 6 |
| `rounds` | int | 3 |
| `debate_mode` | string | "standard" |

### POST `/api/v2/sentiment/analyze`

Aspect-level sentiment analysis.

**Request:**

| Field | Type | Default |
|-------|------|---------|
| `texts` | string[] | Required |
| `include_aspect` | bool | true |

### POST `/api/v2/competitor/intelligence`

Competitive SWOT analysis.

### POST `/api/v2/campaign/optimize`

Budget allocation and channel optimization.

### POST `/api/v2/brand/positioning`

Brand differentiation analysis.

---

## Health Check

### GET `/health`

```json
{"status": "ok", "service": "MarketingCouncil"}
```
