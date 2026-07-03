"""
Payment tracking and on-chain settlement for A2A calls
Tracks which agents called your agent and logs it for on-chain settlement
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import uuid

class PaymentRecord(BaseModel):
    """Record of a single agent-to-agent call for payment settlement"""
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    caller_agent_id: str
    service_used: str  # The action/endpoint called
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    gas_cost: float = 0.0  # On-chain gas cost
    service_fee: float = 0.0  # Your agent's fee
    total_cost: float = 0.0
    status: str = "completed"  # completed, pending, failed
    blockchain_tx_hash: str = ""  # Once settled on-chain
    
    def calculate_fee(self) -> float:
        """Calculate service fee based on action"""
        fees = {
            'analyze_market': 0.01,  # 0.01 CROO
            'get_sentiment': 0.005,
            'find_opportunities': 0.02,
            'get_overview': 0.003,
            'price_alert': 0.005,
        }
        return fees.get(self.service_used, 0.0)

class PaymentTracker:
    """Tracks all A2A payments for settlement"""
    
    def __init__(self):
        self.payment_history: List[PaymentRecord] = []
        self.settlement_batch: List[PaymentRecord] = []
        self.total_revenue = 0.0
    
    def record_cap_call(
        self,
        caller_agent_id: str,
        service_used: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        success: bool = True
    ) -> PaymentRecord:
        """Record an incoming CAP call for payment"""
        
        payment = PaymentRecord(
            caller_agent_id=caller_agent_id,
            service_used=service_used,
            request_data=request_data,
            response_data=response_data,
            status="completed" if success else "failed"
        )
        
        # Calculate fee
        payment.service_fee = payment.calculate_fee()
        payment.gas_cost = 0.001  # Estimated gas on CROO chain
        payment.total_cost = payment.service_fee + payment.gas_cost
        
        self.payment_history.append(payment)
        self.total_revenue += payment.service_fee
        
        return payment
    
    def create_settlement_batch(self) -> Dict[str, Any]:
        """Create a batch for on-chain settlement"""
        unsettled = [p for p in self.payment_history if not p.blockchain_tx_hash]
        
        if not unsettled:
            return {"status": "no_transactions", "message": "All transactions already settled"}
        
        # Group by caller agent
        by_caller = {}
        for payment in unsettled:
            if payment.caller_agent_id not in by_caller:
                by_caller[payment.caller_agent_id] = []
            by_caller[payment.caller_agent_id].append(payment)
        
        # Create settlement request
        settlement = {
            "batch_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "total_transactions": len(unsettled),
            "total_amount": sum(p.total_cost for p in unsettled),
            "by_agent": {}
        }
        
        for agent_id, payments in by_caller.items():
            settlement["by_agent"][agent_id] = {
                "count": len(payments),
                "total": sum(p.total_cost for p in payments),
                "transactions": [p.transaction_id for p in payments]
            }
        
        self.settlement_batch = unsettled
        return settlement
    
    def settle_batch_on_chain(self, tx_hash: str) -> Dict[str, Any]:
        """Mark batch as settled on-chain"""
        for payment in self.settlement_batch:
            payment.blockchain_tx_hash = tx_hash
        
        batch_size = len(self.settlement_batch)
        total_amount = sum(p.total_cost for p in self.settlement_batch)
        
        result = {
            "status": "settled",
            "tx_hash": tx_hash,
            "transactions_settled": batch_size,
            "total_amount_settled": total_amount,
            "timestamp": datetime.now().isoformat()
        }
        
        self.settlement_batch = []
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get payment statistics"""
        completed = [p for p in self.payment_history if p.status == "completed"]
        failed = [p for p in self.payment_history if p.status == "failed"]
        settled = [p for p in self.payment_history if p.blockchain_tx_hash]
        
        by_service = {}
        for payment in completed:
            service = payment.service_used
            if service not in by_service:
                by_service[service] = {"count": 0, "revenue": 0.0}
            by_service[service]["count"] += 1
            by_service[service]["revenue"] += payment.service_fee
        
        return {
            "total_calls": len(self.payment_history),
            "completed_calls": len(completed),
            "failed_calls": len(failed),
            "settled_on_chain": len(settled),
            "pending_settlement": len(completed) - len(settled),
            "total_revenue": self.total_revenue,
            "by_service": by_service,
            "unique_callers": len(set(p.caller_agent_id for p in self.payment_history))
        }
    
    def get_ledger(self) -> List[Dict[str, Any]]:
        """Export full ledger for audit"""
        return [json.loads(p.model_dump_json()) for p in self.payment_history]
