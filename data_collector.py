"""
data_collector.py

Pulls live market news using the DuckDuckGo Instant Answer API
and the DuckDuckGo news endpoint. No paid API key needed.
"""

import asyncio
import httpx
import logging
from datetime import datetime
from urllib.parse import quote_plus

logger = logging.getLogger("data_collector")

DDG_URL = "https://api.duckduckgo.com/"
HEADERS = {"User-Agent": "TradeOpportunitiesBot/1.0 (research; non-commercial)"}
TIMEOUT = 10


class DataCollector:

    async def fetch(self, sector: str) -> dict:
        """
        Returns a dict with:
          - news: list of headline dicts (title, source, date, url, excerpt)
          - summary: background text from the DDG instant answer
        """
        query = f"India {sector} sector trade export import 2024 2025 market opportunities"

        results = await asyncio.gather(
            self._ddg_instant(query),
            self._ddg_news(f"India {sector} industry growth"),
            return_exceptions=True,
        )

        news_items = []
        summary    = ""

        for r in results:
            if isinstance(r, Exception):
                logger.warning("Collector task failed: %s", r)
                continue
            if isinstance(r, list):
                news_items.extend(r)
            elif isinstance(r, str):
                summary = r

        return {
            "sector":     sector,
            "fetched_at": datetime.utcnow().isoformat(),
            "news":       news_items[:10],
            "summary":    summary or f"Market intelligence collected for India's {sector} sector.",
        }

    async def _ddg_instant(self, query: str) -> str:
        params = {
            "q": query,
            "format": "json",
            "no_redirect": "1",
            "skip_disambig": "1",
        }
        async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
            r = await client.get(DDG_URL, params=params)
            r.raise_for_status()
            data     = r.json()
            abstract = data.get("AbstractText", "")
            related  = [
                t.get("Text", "")
                for t in data.get("RelatedTopics", [])[:5]
                if isinstance(t, dict)
            ]
            parts = [abstract] + related
            return " | ".join(p for p in parts if p)

    async def _ddg_news(self, query: str) -> list[dict]:
        url = f"https://duckduckgo.com/news.js?q={quote_plus(query)}&o=json&l=us-en&s=0&df=m"
        async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
            try:
                r = await client.get(url)
                r.raise_for_status()
                data  = r.json()
                items = []
                for art in data.get("results", [])[:8]:
                    items.append({
                        "title":   art.get("title", ""),
                        "source":  art.get("source", ""),
                        "date":    art.get("date", ""),
                        "url":     art.get("url", ""),
                        "excerpt": art.get("excerpt", ""),
                    })
                return items
            except Exception as exc:
                logger.warning("DDG news parse error: %s", exc)
                return []
