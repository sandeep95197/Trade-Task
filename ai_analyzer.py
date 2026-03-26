"""
ai_analyzer.py

Calls the Gemini API to produce a structured Markdown trade report.
If no API key is set, falls back to a hardcoded template so the service
stays usable without any external credentials.
"""

import os
import httpx
import logging
from datetime import datetime

logger = logging.getLogger("ai_analyzer")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)
TIMEOUT = 30


class AIAnalyzer:

    async def generate_report(self, sector: str, market_data: dict) -> str:
        if GEMINI_API_KEY:
            try:
                return await self._gemini_report(sector, market_data)
            except Exception as exc:
                logger.error("Gemini call failed: %s — using template instead", exc)

        return self._template_report(sector, market_data)

    async def _gemini_report(self, sector: str, market_data: dict) -> str:
        news_block = "\n".join(
            f"- [{item['title']}]({item['url']}) ({item['source']}, {item['date']})"
            for item in market_data.get("news", [])
            if item.get("title")
        ) or "No live headlines retrieved."

        prompt = f"""
You are a senior trade economist specializing in India's export-import ecosystem.
Generate a **detailed, professional Markdown trade-opportunity report** for the
**{sector.title()} sector in India** using the context below.

## Context
Background summary: {market_data.get('summary', '')}

Recent headlines:
{news_block}

## Report Requirements
Structure the report EXACTLY as follows (use these headings):

# India Trade Opportunities Report: {sector.title()} Sector
> *Generated: {datetime.utcnow().strftime('%B %d, %Y')} | Source: Trade Opportunities API*

---

## Executive Summary
[3-4 sentence overview of current state and opportunity size]

## Global Market Position
[India's current share, key trading partners, rank in world exports/imports]

## Top 5 Trade Opportunities
[Numbered list; each with: opportunity name, potential value, target markets, timeline]

## Growth Drivers
[Bullet list of 5-7 macro and micro drivers]

## Key Risks & Challenges
[Bullet list of risks with brief mitigation notes]

## Key Players & Stakeholders
[Government bodies, major companies, associations]

## Market Data Snapshot
[Small Markdown table: Metric | Value | Trend]

## Strategic Recommendations
[3-5 actionable recommendations for exporters/investors]

## Useful Resources
[3-5 links to government portals, trade bodies, reports]

---
*This report is for informational purposes. Verify data before making investment decisions.*
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            },
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                GEMINI_URL,
                params={"key": GEMINI_API_KEY},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _template_report(self, sector: str, market_data: dict) -> str:
        news_block = "\n".join(
            f"- **{item['title']}** — *{item['source']}* ({item['date']})"
            for item in market_data.get("news", [])
            if item.get("title")
        ) or "- Live news unavailable. Set GEMINI_API_KEY for enriched reports."

        return f"""# India Trade Opportunities Report: {sector.title()} Sector
> *Generated: {datetime.utcnow().strftime('%B %d, %Y')} | Source: Trade Opportunities API v1.0*

---

## Executive Summary

India's **{sector.title()}** sector presents a strong trade opportunity in the current global
landscape. Favourable government policies, growing domestic manufacturing capacity, and rising
international demand position it for accelerated export growth through 2026-2030.

---

## Global Market Position

- India ranks among the **top 10 global players** in the {sector} space
- Key trading partners: **USA, UAE, Germany, UK, Bangladesh, Netherlands**
- YoY export growth (2023-24): **~12-18%** (sector-dependent)
- Import substitution drive reducing dependency on Chinese imports

---

## Top 5 Trade Opportunities

1. **Premium Export Push** — Target high-value markets in EU & North America
   *Potential: $2-5B incremental revenue | Timeline: 12-24 months*

2. **South-East Asia Expansion** — ASEAN trade corridor via FTA routes
   *Potential: $1-3B | Timeline: 6-18 months*

3. **Digital & E-Commerce Exports** — Cross-border B2B platforms
   *Potential: $500M-2B | Timeline: 3-12 months*

4. **Technology Transfer Partnerships** — Joint ventures with EU/US firms
   *Potential: Long-term IP & capability gains | Timeline: 18-36 months*

5. **Africa Growth Markets** — Emerging middle class in Sub-Saharan Africa
   *Potential: $800M-1.5B | Timeline: 12-30 months*

---

## Growth Drivers

- **PLI Scheme** — Production-Linked Incentive boosting domestic manufacturing
- **China+1 Strategy** — Global supply chains diversifying away from China
- **FTA Momentum** — India-UAE CEPA, India-Australia ECTA, EU negotiations ongoing
- **Digital Infrastructure** — UPI, GeM, ONDC enabling cross-border digital trade
- **Skilled Labour Cost Advantage** — 30-40% lower than competing economies
- **Government Export Incentives** — RoDTEP and MEIS successor schemes
- **Growing Domestic R&D** — Rising patent filings and innovation output

---

## Key Risks & Challenges

| Risk | Impact | Mitigation |
|------|--------|------------|
| Global Recession | High | Diversify markets; focus on essentials |
| Rupee Volatility | Medium | Hedge exposure; invoice in USD/EUR |
| Logistics Bottlenecks | Medium | Use DESH scheme & logistics parks |
| Regulatory Compliance | Medium | Engage trade lawyers & DGFT consultants |
| Geopolitical Tensions | Low-Medium | Monitor Red Sea, Taiwan strait developments |

---

## Key Players & Stakeholders

**Government Bodies**
- Ministry of Commerce & Industry (DPIIT, DGFT)
- EXIM Bank of India
- APEDA / MPEDA (sector-specific)

**Industry Associations**
- FICCI, CII, ASSOCHAM
- Sector-specific export councils (e.g., PHARMEXCIL, EEPC)

---

## Market Data Snapshot

| Metric | Value | Trend |
|--------|-------|-------|
| Sector Export Value (2023-24) | Est. $8-25B | Growing |
| YoY Growth Rate | 12-18% | Positive |
| Top Destination | USA / UAE | Stable |
| Import Dependency | Declining | Improving |
| FDI Inflows | Rising | Positive |

---

## Strategic Recommendations

1. **Register on DGFT portal** and leverage RoDTEP/MEIS incentives immediately
2. **Certify for EU/US markets** — BIS, CE marking, FDA approvals as applicable
3. **Attend India International Trade Fair (IITF)** and sector-specific expos
4. **Partner with IEC-registered freight forwarders** to optimise logistics costs
5. **Leverage ECGC** (Export Credit Guarantee Corporation) to insure export receivables

---

## Recent Market Headlines

{news_block}

---

## Useful Resources

- [DGFT – Directorate General of Foreign Trade](https://dgft.gov.in)
- [Export Promotion Councils India](https://www.texprocil.org)
- [EXIM Bank India](https://www.eximbankindia.in)
- [India Trade Portal](https://www.indiantradeportal.in)
- [Ministry of Commerce & Industry](https://commerce.gov.in)

---
*This report is for informational purposes only. Always verify data with official sources before making investment or trade decisions.*
"""
