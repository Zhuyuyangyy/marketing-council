# MarketingCouncil - TODO & Innovation Backlog

## Priority P0 - Critical

- [ ] Unify Spark LLM call paths (merge `llm_spark.py` and `llm_spark_mock.py`)
- [ ] Add SSE connection retry logic in frontend
- [ ] Add input sanitization for topic field (XSS prevention)
- [ ] Add rate limiting middleware for public deployments

## Priority P1 - High

- [ ] Persistent debate session storage (Redis/SQLite)
- [ ] Debate transcript export (PDF/Markdown)
- [ ] Add structured logging with request tracing
- [ ] Implement proper error codes (not just 500)
- [ ] Add API key authentication middleware
- [ ] Webhook notifications for completed debates

## Priority P2 - Medium

### Smart Marketing Strategy Generation
- [ ] Auto-generate marketing briefs from debate conclusions
- [ ] Template-based strategy document generation
- [ ] Multi-format export (PPT, Word, PDF)

### User Profile-Driven Targeting
- [ ] Integrate user persona database
- [ ] Dynamic audience segmentation based on debate topics
- [ ] Persona-aware agent prompts (adjust analysis based on target demographic)

### A/B Test Automation
- [ ] Generate A/B test plans from debate outcomes
- [ ] Statistical significance calculator
- [ ] Auto-recommend winner based on early data

### Marketing ROI Prediction
- [ ] Historical campaign data integration
- [ ] ROI prediction model (regression + LLM hybrid)
- [ ] Budget optimization algorithm

## Priority P3 - Innovation

### Multi-Language Support
- [ ] English debate mode
- [ ] Japanese debate mode
- [ ] Auto-detect input language

### Collaborative Sessions
- [ ] Multi-user debate rooms
- [ ] Real-time collaboration via WebSocket
- [ ] Role assignment for human participants

### Agent Fine-Tuning
- [ ] Domain-specific agent training data
- [ ] Decision quality feedback loop
- [ ] Agent performance benchmarking

### Market Data Integration
- [ ] Real-time market data API connections
- [ ] Industry report auto-ingestion
- [ ] Competitor monitoring dashboard

### Advanced Analytics
- [ ] Debate pattern analysis across sessions
- [ ] Decision outcome tracking (did GO decisions succeed?)
- [ ] Agent bias detection and correction
