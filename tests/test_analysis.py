import pytest
from src.analysis import MarketAnalysisEngine

class TestMarketAnalysisEngine:
    """Test market analysis engine"""
    
    @pytest.fixture
    def engine(self):
        return MarketAnalysisEngine()
    
    def test_analyze_cryptocurrency(self, engine):
        """Test cryptocurrency analysis"""
        result = engine.analyze_cryptocurrency('bitcoin')
        assert 'symbol' in result
        assert 'price_analysis' in result
        assert 'technical_analysis' in result
        assert 'sentiment_analysis' in result
    
    def test_find_trading_opportunities(self, engine):
        """Test finding trading opportunities"""
        result = engine.find_trading_opportunities(
            min_market_cap=1_000_000_000,
            max_market_cap=10_000_000_000
        )
        assert isinstance(result, list)
    
    def test_get_market_overview(self, engine):
        """Test market overview"""
        result = engine.get_market_overview()
        assert 'fear_and_greed' in result
        assert 'top_gainers' in result
        assert 'top_losers' in result
        assert 'market_sentiment' in result
