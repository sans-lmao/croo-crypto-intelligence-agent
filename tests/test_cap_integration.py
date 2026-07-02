import pytest
from src.cap_integration import CROOCAPIntegration, CAPRequest

class TestCROOCAPIntegration:
    """Test CROO CAP protocol integration"""
    
    @pytest.fixture
    def integration(self):
        return CROOCAPIntegration()
    
    def test_process_analyze_market_call(self, integration):
        """Test processing analyze_market CAP call"""
        request = CAPRequest(
            agent_id='test-agent',
            action='analyze_market',
            payload={'symbol': 'bitcoin'}
        )
        response = integration.process_cap_call(request)
        assert response.status == 'success'
        assert 'price_analysis' in response.result
    
    def test_process_get_sentiment_call(self, integration):
        """Test processing get_sentiment CAP call"""
        request = CAPRequest(
            agent_id='test-agent',
            action='get_sentiment',
            payload={'symbol': 'bitcoin'}
        )
        response = integration.process_cap_call(request)
        assert response.status == 'success'
    
    def test_process_invalid_action(self, integration):
        """Test processing invalid action"""
        request = CAPRequest(
            agent_id='test-agent',
            action='invalid_action',
            payload={}
        )
        response = integration.process_cap_call(request)
        assert response.status == 'error'
    
    def test_supported_actions(self, integration):
        """Test supported actions list"""
        assert 'analyze_market' in integration.supported_actions
        assert 'get_sentiment' in integration.supported_actions
        assert 'find_opportunities' in integration.supported_actions
