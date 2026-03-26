"""
main.py

Entry point for the Trade Opportunities API.
Wires up middleware, routes, and shared service instances.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uuid
import logging
import re
from datetime import datetime
from typing import Optional

from auth import verify_token, create_guest_token
from data_collector import DataCollector
from ai_analyzer import AIAnalyzer
from session_manager import SessionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("trade_api")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Trade Opportunities API",
    description="Analyzes market data and provides trade opportunity insights for sectors in India.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

session_manager = SessionManager()
data_collector  = DataCollector()
ai_analyzer     = AIAnalyzer()

# sector names: letters, spaces, hyphens only, between 3 and 50 chars
VALID_SECTOR_PATTERN = re.compile(r"^[a-zA-Z\s\-]{3,50}$")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "Trade Opportunities API", "version": "1.0.0"}


@app.post("/auth/guest", tags=["Auth"])
async def guest_login():
    """Hand out a short-lived guest JWT — useful for quick testing."""
    token = create_guest_token()
    return {"access_token": token, "token_type": "bearer", "expires_in": 3600}


@app.get(
    "/analyze/{sector}",
    response_class=PlainTextResponse,
    tags=["Analysis"],
    summary="Get trade opportunity report for a sector",
    responses={
        200: {"description": "Markdown trade analysis report"},
        400: {"description": "Invalid sector name"},
        401: {"description": "Unauthorized"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Upstream service error"},
    },
)
@limiter.limit("5/minute;20/hour")
async def analyze_sector(
    request: Request,
    sector: str,
    authorization: Optional[str] = Header(None),
):
    """
    Main endpoint. Accepts a sector name, pulls live market data,
    runs it through the AI analyzer, and returns a Markdown report.

    Try: pharmaceuticals · technology · agriculture · textiles · renewable-energy
    """
    token_payload = verify_token(authorization)
    session_id    = token_payload.get("sub", str(uuid.uuid4()))

    sector = sector.strip().lower()
    if not VALID_SECTOR_PATTERN.match(sector):
        raise HTTPException(
            status_code=400,
            detail="Invalid sector name. Use only letters, spaces, or hyphens (3–50 chars).",
        )

    logger.info("Analyze request | session=%s | sector=%s", session_id, sector)
    session_manager.record_request(session_id, sector)

    try:
        market_data = await data_collector.fetch(sector)
    except Exception as exc:
        logger.error("Data collection failed: %s", exc)
        market_data = {"news": [], "summary": f"Live data temporarily unavailable for '{sector}'."}

    try:
        report_md = await ai_analyzer.generate_report(sector, market_data)
    except Exception as exc:
        logger.error("AI analysis failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"Analysis service error: {exc}")

    return PlainTextResponse(content=report_md, media_type="text/markdown")


@app.get("/session/{session_id}", tags=["Session"], summary="Get session usage stats")
async def get_session(session_id: str, authorization: Optional[str] = Header(None)):
    verify_token(authorization)
    data = session_manager.get_session(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found.")
    return data


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": session_manager.count(),
    }
