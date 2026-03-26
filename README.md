# Trade Opportunities API

A FastAPI service that generates trade opportunity reports for specific sectors in India.
Point it at a sector name and it pulls live market headlines, runs them through Gemini,
and hands back a structured Markdown report.

---

## Setup

### 1. Clone / extract the project
```bash
cd trade_api
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# then open .env and fill in your keys
```

The two variables you can set:

| Variable | Default | Notes |
|----------|---------|-------|
| `GEMINI_API_KEY` | *(empty)* | Free key at [aistudio.google.com](https://aistudio.google.com). Without it the service still works — returns a rich template report. |
| `JWT_SECRET` | `trade-api-super-secret-key-change-in-prod` | Change this before deploying anywhere public. |

### 5. Start the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Usage

### Optional: get a guest token
```bash
curl -X POST http://localhost:8000/auth/guest
# {"access_token": "eyJ...", "token_type": "bearer", "expires_in": 3600}
```

### Analyze a sector
```bash
# without token (auto-guest)
curl http://localhost:8000/analyze/pharmaceuticals

# with token
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/analyze/technology
```

Sector name rules: letters, spaces, and hyphens only — between 3 and 50 characters.

Some sectors to try:
- pharmaceuticals
- technology
- agriculture
- textiles
- renewable-energy
- automobiles
- chemicals
- electronics
- gems-and-jewellery
- food-processing

### Health check
```bash
curl http://localhost:8000/health
```

---

## API Docs

With the server running, open:
- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc

---

## Security

| Feature | How it's done |
|---------|---------------|
| Auth | JWT Bearer tokens via python-jose |
| Rate limiting | 5 req/min · 20 req/hour per IP (slowapi) |
| Input validation | Regex + length check on sector name |
| CORS | FastAPI CORSMiddleware |
| Error handling | Graceful fallback if Gemini or DuckDuckGo is down |

---

## Project Structure

```
trade_api/
├── main.py             # FastAPI app, routes, middleware
├── auth.py             # JWT creation and verification
├── data_collector.py   # DuckDuckGo live data fetch
├── ai_analyzer.py      # Gemini report generation + template fallback
├── session_manager.py  # In-memory session tracking
├── requirements.txt
├── .env.example
└── README.md
```

### Request flow
```
Client
  → Auth check (JWT or auto-guest)
  → Rate limiter
  → Input validation
  → DataCollector  (DuckDuckGo headlines + summary)
  → AIAnalyzer     (Gemini API or template fallback)
  → Markdown report response
```

---

## Response format

The `/analyze/{sector}` endpoint returns a `.md` document covering:

- Executive Summary
- Global Market Position
- Top 5 Trade Opportunities (with value estimates and timelines)
- Growth Drivers
- Risks & Mitigation table
- Key Players & Stakeholders
- Market Data Snapshot table
- Strategic Recommendations
- Recent Headlines
- Useful Resources

---

## License

MIT
