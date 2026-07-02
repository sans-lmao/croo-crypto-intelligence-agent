import json
import hashlib
import hmac
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from config import CROO_AGENT_ID, CROO_PRIVATE_KEY
from src.analysis import MarketAnalysisEngine

class CAPRequest(BaseModel):
    """CROO Agent Protocol Request"""
    agent_id: str
    action: str
    payload: Dict[str, Any]
    nonce: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    signature: Optional[str] = None

class CAPResponse(BaseModel):
    """CROO Agent Protocol Response"""
    agent_id: str
    status: str = 'success'  # success, error, pending
    result: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    message_id: str

class CROOCAPIntegration:
    """Handles CROO Agent Protocol (CAP) integration"""
    
    def __init__(self):
        self.agent_id = CROO_AGENT_ID
        self.private_key = CROO_PRIVATE_KEY
        self.analysis_engine = MarketAnalysisEngine()
        self.supported_actions = [
            'analyze_market',
            'get_sentiment',
            'find_opportunities',
            'get_overview',
            'price_alert'
        ]
    
    def process_cap_call(self, request: CAPRequest) -> CAPResponse:
        """Process incoming CAP call"""
        # Verify signature
        if not self._verify_signature(request):
            return CAPResponse(
                agent_id=self.agent_id,
                status='error',
                result={'error': 'Invalid signature'},
                message_id=request.nonce
            )
        
        # Verify action is supported
        if request.action not in self.supported_actions:
            return CAPResponse(
                agent_id=self.agent_id,
                status='error',
                result={'error': f'Action {request.action} not supported'},
                message_id=request.nonce
            )
        
        # Execute action
        try:
            if request.action == 'analyze_market':
                result = self.handle_analyze_market(request.payload)
            elif request.action == 'get_sentiment':
                result = self.handle_get_sentiment(request.payload)
            elif request.action == 'find_opportunities':
                result = self.handle_find_opportunities(request.payload)
            elif request.action == 'get_overview':
                result = self.handle_get_overview(request.payload)
            elif request.action == 'price_alert':
                result = self.handle_price_alert(request.payload)
            else:
                result = {'error': 'Unknown action'}
            
            return CAPResponse(
                agent_id=self.agent_id,
                status='success',
                result=result,
                message_id=request.nonce
            )
        except Exception as e:
            return CAPResponse(
                agent_id=self.agent_id,
                status='error',
                result={'error': str(e)},
                message_id=request.nonce
            )
    
    def handle_analyze_market(self, payload: Dict) -> Dict:
        """Handle market analysis request"""
        symbol = payload.get('symbol', 'bitcoin')
        return self.analysis_engine.analyze_cryptocurrency(symbol)
    
    def handle_get_sentiment(self, payload: Dict) -> Dict:
        """Handle sentiment analysis request"""
        symbol = payload.get('symbol', 'bitcoin')
        return self.analysis_engine.sentiment.generate_sentiment_report(symbol)
    
    def handle_find_opportunities(self, payload: Dict) -> Dict:
        """Handle opportunity detection request"""
        min_cap = payload.get('min_market_cap', 1_000_000_000)
        max_cap = payload.get('max_market_cap', 10_000_000_000)
        opportunities = self.analysis_engine.find_trading_opportunities(min_cap, max_cap)
        return {
            'opportunities': opportunities,
            'count': len(opportunities),
            'filters': {'min_market_cap': min_cap, 'max_market_cap': max_cap}
        }
    
    def handle_get_overview(self, payload: Dict) -> Dict:
        """Handle market overview request"""
        return self.analysis_engine.get_market_overview()
    
    def handle_price_alert(self, payload: Dict) -> Dict:
        """Handle price alert setup"""
        symbol = payload.get('symbol', 'bitcoin')
        target_price = payload.get('target_price')
        alert_type = payload.get('type', 'above')  # above or below
        
        if not target_price:
            return {'error': 'target_price is required'}
        
        # In production, this would store the alert in a database
        # and check it periodically
        return {
            'symbol': symbol,
            'target_price': target_price,
            'alert_type': alert_type,
            'status': 'active',
            'message': f'Alert set for {symbol}: notify if price goes {alert_type} ${target_price}'
        }
    
    def _verify_signature(self, request: CAPRequest) -> bool:
        """Verify CAP request signature"""
        if not request.signature or not self.private_key:
            # In development, skip verification
            return True
        
        # Create signature payload
        payload_str = json.dumps({
            'agent_id': request.agent_id,
            'action': request.action,
            'payload': request.payload,
            'nonce': request.nonce
        }, sort_keys=True)
        
        # Verify HMAC-SHA256
        expected_sig = hmac.new(
            self.private_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_sig, request.signature)
    
    def generate_signature(self, data: Dict) -> str:
        """Generate signature for outgoing CAP calls"""
        if not self.private_key:
            return ''
        
        payload_str = json.dumps(data, sort_keys=True)
        return hmac.new(
            self.private_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
