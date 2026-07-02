import pytest
from src.market_data import MarketDataProvider

class TestMarketDataProvider:
    """Test market data fetching"""
    
    @pytest.fixture
    def provider(self):
        return MarketDataProvider()
    
    def test_get_current_price(self, provider):
        """Test fetching current price"""
        result = provider.get_current_price('bitcoin')
        assert result is not None
        assert 'price' in result
        assert 'symbol' in result
        assert result['symbol'] == 'BITCOIN'
    
    def test_get_market_cap_rank(self, provider):
        """Test fetching market cap rankings"""
        result = provider.get_market_cap_rank(limit=10)
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'rank' in result[0]
        assert 'symbol' in result[0]
    
    def test_get_price_history(self, provider):
        """Test fetching price history"""
        result = provider.get_price_history('bitcoin', days=7)
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'timestamp' in result[0]
        assert 'price' in result[0]
    
    def test_calculate_volatility(self, provider):
        """Test volatility calculation"""
        result = provider.calculate_volatility('bitcoin', days=7)
        assert result is not None
        assert isinstance(result, float)
        assert result >= 0
