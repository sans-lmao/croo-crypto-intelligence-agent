# Crypto Market Intelligence Agent

Real-time cryptocurrency market intelligence agent built on the [CROO Agent Protocol (CAP)](https://cap.croo.network). Analyzes price action, volatility, and Fear & Greed sentiment for major cryptocurrencies and surfaces trading opportunities — callable by any other agent on the CROO network, with real on-chain settlement in USDC on Base.

Built for the [CROO Agent Hackathon](https://campaigns.croo.network/hackathon.html) (Data & Analytics / Research & Report tracks).

## What it does

- **Market analysis** — live price, 24h change, market cap, volume, and short-term volatility for any major cryptocurrency
- **Sentiment analysis** — Fear & Greed Index plus aggregated social sentiment, with a bullish/bearish/neutral read
- **Opportunity screening** — scans a market-cap range you specify and surfaces notable movers
- **Market overview** — a snapshot across the broader market

## Architecture

- `src/market_data.py`, `src/sentiment.py`, `src/analysis.py` — the analysis engine (`MarketAnalysisEngine`)
- `croo_provider.py` — the real CAP integration. Connects to CROO's live network via the official [`croo-sdk`](https://github.com/CROO-Network/python-sdk), listens for negotiations from real requester agents, accepts them, and delivers results after real on-chain payment settles.
- `run_agent.py` / `src/agent.py` — an optional local FastAPI demo (Swagger UI at `/docs`) for exercising the analysis engine directly, outside of CAP

## CAP integration — SDK methods actually used

From `croo-sdk`:
- `AgentClient(Config(base_url, ws_url), sdk_key)` — authenticated client
- `client.connect_websocket()` — opens the live event stream
- `stream.on(EventType.NEGOTIATION_CREATED, handler)` / `stream.on(EventType.ORDER_PAID, handler)` — event subscriptions
- `client.accept_negotiation(negotiation_id)` — accepts an incoming service request
- `client.get_order(order_id)` — retrieves order requirements
- `client.deliver_order(order_id, DeliverOrderRequest(deliverable_type=DeliverableType.TEXT, deliverable_text=...))` — delivers the result and triggers on-chain settlement

**Order lifecycle:** negotiate → accept → buyer pays (USDC escrowed) → deliver → settlement releases funds to this agent's wallet.

## Setup

```bash
git clone https://github.com/sans-lmao/croo-crypto-intelligence-agent.git
cd croo-crypto-intelligence-agent
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env — add your real CROO_SDK_KEY from https://agent.croo.network
```

## Running the agent

```bash
python croo_provider.py
```
Expected output: `CROO provider is live. Waiting for real orders...`. Agent status shows **Online** on [agent.croo.network](https://agent.croo.network).

Optional local demo API (separate from CAP):
```bash
python run_agent.py
# Swagger UI: http://localhost:8000/docs
```

## Requesting this service (for other agents)

Send JSON matching:
```json
{"action": "analyze_market", "symbol": "bitcoin"}
{"action": "get_sentiment", "symbol": "ethereum"}
{"action": "find_opportunities", "min_market_cap": 1000000000, "max_market_cap": 10000000000}
{"action": "get_overview"}
```

## Testing

```bash
pytest tests/
```

## License

MIT — see [LICENSE](LICENSE)
