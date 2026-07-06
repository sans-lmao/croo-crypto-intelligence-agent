"""
Real CROO CAP provider.

This replaces src/cap_integration.py's fake /cap endpoint. Instead of
simulating payments locally, this connects to CROO's actual network,
listens for real negotiations from real requester agents, and delivers
real results after real on-chain payment.

PREREQUISITES (do these on https://agent.croo.network before running this):
  1. Register your agent -> you get an Agent DID + an AA wallet address.
  2. Register a Service on that agent -> define its price + the JSON
     schema you expect requesters to send as `requirements` (e.g.
     {"action": "analyze_market", "symbol": "bitcoin"}).
  3. Generate an SDK Key (format: croo_sk_...) from the dashboard.
  4. Put CROO_API_URL / CROO_WS_URL / CROO_SDK_KEY in your local .env
     (never commit the real file — .env is git-ignored).

Run:
    pip install croo-sdk
    python croo_provider.py

Note on event object fields: the SDK's public README documents the event
TYPES (NEGOTIATION_CREATED, ORDER_PAID, etc.) but not every attribute on
every event object. The first time you run this, add a
`print(vars(e))` inside a handler to confirm exact field names before
relying on them — this is normal practice with a young SDK, not a bug
in this script.
"""

import asyncio
import json
import os

from dotenv import load_dotenv
from croo import (
    AgentClient,
    Config,
    EventType,
    DeliverableType,
    DeliverOrderRequest,
)

from src.analysis import MarketAnalysisEngine

load_dotenv()

REQUIRED_ENV = ["CROO_API_URL", "CROO_WS_URL", "CROO_SDK_KEY"]
missing = [v for v in REQUIRED_ENV if not os.environ.get(v)]
if missing:
    raise RuntimeError(
        f"Missing required env vars: {missing}. "
        "Register your agent + service at https://agent.croo.network first, "
        "generate an SDK key, then add it to your local .env."
    )

client = AgentClient(
    Config(
        base_url=os.environ["CROO_API_URL"],
        ws_url=os.environ["CROO_WS_URL"],
    ),
    os.environ["CROO_SDK_KEY"],
)

engine = MarketAnalysisEngine()


def fulfill(requirements_raw: str) -> dict:
    """
    Turn a requester's order requirements into a REAL analysis result,
    reusing your existing (legitimate) analysis engine.

    Expected requirements JSON (agreed with your Service's schema on the
    dashboard), e.g.:
        {"action": "analyze_market", "symbol": "bitcoin"}
        {"action": "get_sentiment", "symbol": "ethereum"}
        {"action": "find_opportunities", "min_market_cap": 1e9, "max_market_cap": 1e10}
        {"action": "get_overview"}
    """
    try:
        req = json.loads(requirements_raw) if requirements_raw else {}
    except json.JSONDecodeError:
        req = {}

    action = req.get("action", "analyze_market")
    symbol = req.get("symbol", "bitcoin")

    if action == "analyze_market":
        return engine.analyze_cryptocurrency(symbol)
    if action == "get_sentiment":
        return engine.sentiment.generate_sentiment_report(symbol)
    if action == "find_opportunities":
        min_cap = req.get("min_market_cap", 1_000_000_000)
        max_cap = req.get("max_market_cap", 10_000_000_000)
        return {"opportunities": engine.find_trading_opportunities(min_cap, max_cap)}
    if action == "get_overview":
        return engine.get_market_overview()
    return {"error": f"unsupported action: {action}"}


async def main():
    stream = await client.connect_websocket()

    def on_negotiation(e):
        async def _handle():
            print(f"[negotiation] incoming: {e.negotiation_id}")
            result = await client.accept_negotiation(e.negotiation_id)
            print(f"[negotiation] accepted -> order {result.order.order_id}")

        asyncio.create_task(_handle())

    def on_paid(e):
        async def _handle():
            print(f"[order] paid: {e.order_id} — running real analysis")
            order = await client.get_order(e.order_id)
            requirements = getattr(order, "requirements", "") or ""
            result = fulfill(requirements)

            await client.deliver_order(
                e.order_id,
                DeliverOrderRequest(
                    deliverable_type=DeliverableType.TEXT,
                    deliverable_text=json.dumps(result),
                ),
            )
            print(f"[order] delivered: {e.order_id}")

        asyncio.create_task(_handle())

    stream.on(EventType.NEGOTIATION_CREATED, on_negotiation)
    stream.on(EventType.ORDER_PAID, on_paid)

    print("CROO provider is live. Waiting for real orders... (Ctrl+C to stop)")
    stop_forever = asyncio.Event()
    await stop_forever.wait()


if __name__ == "__main__":
    asyncio.run(main())
