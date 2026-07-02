import pytest
from src.sentiment import SentimentAnalyzer, SentimentLevel

class TestSentimentAnalyzer:
    """Test sentiment analysis"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_get_fear_and_greed_index(self, analyzer):
        """Test Fear & Greed Index fetching"""
        result = analyzer.get_fear_and_greed_index()
        assert 'value' in result
        assert 'classification' in result
        assert 0 <= result['value'] <= 100
    
    def test_classify_fng(self, analyzer):
        """Test FNG classification"""
        assert analyzer._classify_fng(20) == 'Extreme Fear'
        assert analyzer._classify_fng(40) == 'Fear'
        assert analyzer._classify_fng(50) == 'Neutral'
        assert analyzer._classify_fng(70) == 'Greed'
        assert analyzer._classify_fng(80) == 'Extreme Greed'
    
    def test_analyze_social_sentiment(self, analyzer):
        """Test social sentiment analysis"""
        result = analyzer.analyze_social_sentiment('bitcoin')
        assert 'twitter_sentiment' in result
        assert 'reddit_sentiment' in result
        assert 'overall' in result
    
    def test_generate_sentiment_report(self, analyzer):
        """Test sentiment report generation"""
        result = analyzer.generate_sentiment_report('bitcoin')
        assert 'symbol' in result
        assert 'fear_and_greed' in result
        assert 'overall_sentiment' in result
        assert 'recommendation' in result
    
    def test_get_recommendation(self, analyzer):
        """Test trading recommendation"""
        assert analyzer._get_recommendation(SentimentLevel.VERY_BEARISH) == 'Strong Sell'
        assert analyzer._get_recommendation(SentimentLevel.BULLISH) == 'Buy'
        assert analyzer._get_recommendation(SentimentLevel.NEUTRAL) == 'Hold'
