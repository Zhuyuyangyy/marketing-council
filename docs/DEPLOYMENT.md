# MarketingCouncil Deployment Guide

## Quick Start (Local Development)

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
# Copy and edit environment variables
cp .env.example .env
# Edit .env with your API credentials

# Or configure via config.yaml for Dify integration
```

### Run

```bash
# Option 1: Direct
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009

# Option 2: Shell script
bash start.sh        # Linux/macOS
start.bat            # Windows

# Option 3: Demo mode (no API key)
python run_demo.py --mock
```

Access:
- API: http://localhost:8009
- Docs: http://localhost:8009/docs
- Frontend: Open `frontend/index.html`

---

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t marketing-council .

# Run container
docker run -p 8009:8009 --env-file .env marketing-council

# Or use docker-compose
docker-compose up -d
```

### Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| `marketing-council` | 8009 | FastAPI backend + API |
| `nginx` | 80 | Reverse proxy (optional) |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPARK_APP_ID` | No | - | iFlytek Spark App ID |
| `SPARK_API_KEY` | No | - | iFlytek Spark API Key |
| `SPARK_API_SECRET` | No | - | iFlytek Spark API Secret |
| `SPARK_API_VERSION` | No | `generalv3.5` | Spark model version |
| `DIFY_API_URL` | No | - | Dify workflow API URL |
| `DIFY_API_KEY` | No | - | Dify API key |

---

## Production Considerations

### Security

- Set `allow_origins` to specific domains (not `["*"]`)
- Use environment variables for all secrets (never commit `.env`)
- Add rate limiting for public deployments
- Enable HTTPS via reverse proxy

### Performance

- Default timeout: 60s per LLM call
- SSE streaming reduces perceived latency
- Consider connection pooling for high-traffic deployments

### Monitoring

- Health endpoint: `GET /health`
- Structured logging via Loguru
- Session IDs for request tracing
