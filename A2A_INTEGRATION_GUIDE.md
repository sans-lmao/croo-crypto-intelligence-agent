# A2A Integration Guide - CROO Crypto Intelligence Agent

## What is A2A Composability?

Agent-to-Agent (A2A) composability means other agents can **hire your agent** to perform services and **pay you on-chain**.

Your Crypto Intelligence Agent provides market analysis that other agents need. For example:
- A **Portfolio Manager Agent** needs market data → calls your agent
- A **Trading Bot Agent** needs sentiment analysis → calls your agent
- A **Risk Analysis Agent** needs opportunities → calls your agent

Each call = **on-chain payment to you** ✅

---

## How to Call This Agent (A2A)

### Endpoint
```
POST /cap
```

### Request Format
```json
{
  "agent_id": "croo-crypto-intelligence-agent",
  "caller_agent_id": "your-agent-id-here",
  "action": "analyze_market",
  "payload": {
    "symbol": "bitcoin"
  }
}
```

### Supported Actions

#### 1. `analyze_market` - Get full market analysis
**Cost:** 0.01 CROO
```json
{
  "agent_id": "croo-crypto-intelligence-agent",
  "caller_agent_id": "portfolio-manager-agent",
  "action": "analyze_market",
  "payload": {
    "symbol": "bitcoin"
  }
}
```
**Returns:** Price analysis, technical indicators, sentiment, alerts

#### 2. `get_sentiment` - Get sentiment analysis
**Cost:** 0.005 CROO
```json
{
  "agent_id": "croo-crypto-intelligence-agent",
  "caller_agent_id": "your-agent",
  "action": "get_sentiment",
  "payload": {
    "symbol": "ethereum"
  }
}
```
**Returns:** Fear & Greed Index, social sentiment, overall trend

#### 3. `find_opportunities` - Find trading opportunities
**Cost:** 0.02 CROO
```json
{
  "agent_id": "croo-crypto-intelligence-agent",
  "caller_agent_id": "trading-bot-agent",
  "action": "find_opportunities",
  "payload": {
    "min_market_cap": 1000000000,
    "max_market_cap": 10000000000
  }
}
```
**Returns:** List of opportunities in market cap range

#### 4. `get_overview` - Get market overview
**Cost:** 0.003 CROO
```json
{
  "agent_id": "croo-crypto-intelligence-agent",
  "caller_agent_id": "your-agent",
  "action": "get_overview",
  "payload": {}
}
```
**Returns:** Total market cap, 24h volume, top gainers/losers

#### 5. `price_alert` - Set up price alert
**Cost:** 0.005 CROO
```json
{
  "agent_id": "croo-crypto-intelligence-agent",
  "caller_agent_id": "alert-bot-agent",
  "action": "price_alert",
  "payload": {
    "symbol": "bitcoin",
    "target_price": 70000,
    "type": "above"
  }
}
```
**Returns:** Alert confirmation with ID

---

## Response Format

Every CAP response includes:
```json
{
  "agent_id": "croo-crypto-intelligence-agent",
  "status": "success",
  "result": { ... },
  "timestamp": "2026-07-03T19:35:00.000Z",
  "message_id": "12345.6789",
  "transaction_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The `transaction_id` is used to track the payment on-chain.

---

## Payment Flow

1. **Your Agent Receives Call**
   - Another agent calls `/cap` endpoint
   - Request is verified
   - Service is executed
   - `transaction_id` is generated

2. **Payment is Recorded**
   - Call is logged in payment ledger
   - Service fee is calculated
   - Gas costs are estimated
   - Total cost = service fee + gas

3. **Batch Settlement**
   - Call `/settlement` to create batch
   - Groups all unsettled payments
   - Returns batch details

4. **On-Chain Payment**
   - Batch is submitted to CROO blockchain
   - Smart contract executes payment
   - Funds go to agent wallet

5. **Settlement Confirmation**
   - Call `/settlement/confirm` with tx hash
   - Marks payments as settled

---

## Example: Portfolio Manager Calling This Agent

```python
import requests
import json

# Portfolio Manager Agent calling Crypto Intelligence Agent
caller_id = "portfolio-manager-agent"
target_agent_url = "http://localhost:8000"

# Get market analysis for Bitcoin
request_body = {
    "agent_id": "croo-crypto-intelligence-agent",
    "caller_agent_id": caller_id,
    "action": "analyze_market",
    "payload": {"symbol": "bitcoin"}
}

response = requests.post(
    f"{target_agent_url}/cap",
    json=request_body
)

if response.status_code == 200:
    result = response.json()
    analysis = result["result"]
    tx_id = result["transaction_id"]
    
    print(f"Bitcoin Price: ${analysis['price_analysis']['current_price']}")
    print(f"24h Change: {analysis['price_analysis']['change_24h']}%")
    print(f"Sentiment: {analysis['overall_sentiment']}")
    print(f"Payment TX ID: {tx_id}")
else:
    print(f"Error: {response.text}")
```

---

## Monitoring Payments

### Check Payment Statistics
```bash
curl http://localhost:8000/stats
```

Returns:
```json
{
  "total_calls": 150,
  "completed_calls": 148,
  "failed_calls": 2,
  "settled_on_chain": 145,
  "pending_settlement": 3,
  "total_revenue": 1.875,
  "by_service": {
    "analyze_market": {"count": 50, "revenue": 0.5},
    "get_sentiment": {"count": 75, "revenue": 0.375},
    "find_opportunities": {"count": 20, "revenue": 0.4},
    "get_overview": {"count": 3, "revenue": 0.009}
  },
  "unique_callers": 12
}
```

### Create Settlement Batch
```bash
curl http://localhost:8000/settlement
```

Returns batch ready for on-chain payment:
```json
{
  "batch_id": "batch-2026-07-03-001",
  "timestamp": "2026-07-03T19:35:00.000Z",
  "total_transactions": 5,
  "total_amount": 0.075,
  "by_agent": {
    "portfolio-manager-agent": {
      "count": 3,
      "total": 0.032
    },
    "trading-bot-agent": {
      "count": 2,
      "total": 0.043
    }
  }
}
```

---

## Production Deployment

1. **Get CROO Agent ID**
   - Register on CROO Agent Store
   - Set `CROO_AGENT_ID` in `.env`

2. **Set Payment Wallet**
   - Add your wallet address for receiving payments
   - Ensure sufficient gas for settlement transactions

3. **Enable Signatures**
   - Set `CROO_PRIVATE_KEY` in `.env` for production
   - Will enable request verification

4. **Deploy to CROO Store**
   - Submit to store listing
   - Make endpoint public on CROO network
   - Enable other agents to discover and call you

5. **Monitor Payments**
   - Check `/stats` regularly
   - Batch and settle payments daily
   - Track revenue on blockchain

---

## Security Notes

✅ **Signature Verification**
- All requests verified with HMAC-SHA256
- Only valid agents can call you

✅ **Rate Limiting**
- Implement rate limits to prevent abuse
- Monitor for suspicious patterns

✅ **Payment Tracking**
- Every call logged immutably
- Audit trail for all transactions
- Settlement verified on-chain

---

## Next Steps

1. ✅ Agent is ready for A2A calls
2. ⏳ Deploy to CROO Agent Store
3. ⏳ Other agents discover and call you
4. ⏳ Receive on-chain payments
5. ⏳ Build network effects!
