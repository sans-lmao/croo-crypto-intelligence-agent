from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import uvicorn
from config import AGENT_HOST, AGENT_PORT, DEBUG
from src.cap_integration import CROOCAPIntegration, CAPRequest, CAPResponse
from src.analysis import MarketAnalysisEngine

app = FastAPI(
    title="CROO Crypto Intelligence Agent",
    description="Real-time cryptocurrency market analysis and sentiment tracking",
    version="1.0.0"
)

# Initialize components
cap_integration = CROOCAPIntegration()
analysis_engine = MarketAnalysisEngine()

class AnalyzeRequest(BaseModel):
    symbol: str
    
class SentimentRequest(BaseModel):
    symbol: str
    
class OpportunitiesRequest(BaseModel):
    min_market_cap: int = 1_000_000_000
    max_market_cap: int = 10_000_000_000

@app.get("/")
async def root():
    """Root endpoint - agent status"""
    return {
        "agent": "CROO Crypto Intelligence Agent",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/analyze",
            "/sentiment",
            "/opportunities",
            "/overview",
            "/cap"
        ]
    }

@app.post("/analyze")
async def analyze_market(request: AnalyzeRequest):
    """Analyze a cryptocurrency market"""
    try:
        result = analysis_engine.analyze_cryptocurrency(request.symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sentiment")
async def get_sentiment(request: SentimentRequest):
    """Get sentiment analysis for a cryptocurrency"""
    try:
        result = analysis_engine.sentiment.generate_sentiment_report(request.symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/overview")
async def get_overview():
    """Get market overview"""
    try:
        result = analysis_engine.get_market_overview()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/opportunities")
async def find_opportunities(request: OpportunitiesRequest):
    """Find trading opportunities"""
    try:
        result = analysis_engine.find_trading_opportunities(
            request.min_market_cap,
            request.max_market_cap
        )
        return {"opportunities": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cap")
async def cap_endpoint(request: CAPRequest):
    """CROO Agent Protocol (CAP) endpoint
    
    This is the primary interface for other CROO agents to call this agent.
    Supports actions:
    - analyze_market: Get detailed market analysis
    - get_sentiment: Get sentiment analysis
    - find_opportunities: Find trading opportunities
    - get_overview: Get market overview
    - price_alert: Set up price alerts
    """
    try:
        response = cap_integration.process_cap_call(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print(f"Starting CROO Crypto Intelligence Agent on {AGENT_HOST}:{AGENT_PORT}")
    print(f"Debug mode: {DEBUG}")
    print(f"\nAPI Documentation: http://{AGENT_HOST}:{AGENT_PORT}/docs")
    
    uvicorn.run(
        app,
        host=AGENT_HOST,
        port=AGENT_PORT,
        debug=DEBUG
    )
