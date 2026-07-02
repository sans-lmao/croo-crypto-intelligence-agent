from typing import Dict, List
from datetime import datetime
import requests
from enum import Enum

class SentimentLevel(str, Enum):
    VERY_BEARISH = 'very_bearish'
    BEARISH = 'bearish'
    NEUTRAL = 'neutral'
    BULLISH = 'bullish'
    VERY_BULLISH = 'very_bullish'

class SentimentAnalyzer:
    """Analyzes market sentiment from multiple sources"""
    
    def __init__(self):
        self.fear_greed_url = 'https://api.alternative.me/fng/'
        self.sentiment_cache = {}
    
    def get_fear_and_greed_index(self) -> Dict:
        """Fetch Fear & Greed Index from alternative.me"""
        try:
            response = requests.get(f"{self.fear_greed_url}?limit=1", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                fng = data['data'][0]
                value = int(fng.get('value', 50))
                return {
                    'value': value,
                    'classification': self._classify_fng(value),
                    'timestamp': fng.get('timestamp'),
                    'source': 'alternative.me'
                }
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {str(e)}")
        
        return {'value': 50, 'classification': 'neutral', 'source': 'error'}
    
    def _classify_fng(self, value: int) -> str:
        """Classify Fear & Greed value"""
        if value < 25:
            return 'Extreme Fear'
        elif value < 45:
            return 'Fear'
        elif value < 55:
            return 'Neutral'
        elif value < 75:
            return 'Greed'
        else:
            return 'Extreme Greed'
    
    def analyze_social_sentiment(self, symbol: str) -> Dict:
        """Analyze sentiment from social mentions (Twitter, Reddit, etc.)
        
        In production, this would integrate with:
        - Twitter API for tweet sentiment
        - Reddit API for discussion sentiment
        - CoinTelegraph or other news sources
        """
        # Placeholder implementation
        return {
            'symbol': symbol,
            'twitter_sentiment': 0.65,  # 0-1 scale
            'reddit_sentiment': 0.58,
            'news_sentiment': 0.70,
            'overall': 0.64,
            'trend': 'increasing',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_sentiment_level(self, symbol: str) -> SentimentLevel:
        """Determine overall sentiment level for a cryptocurrency"""
        fng = self.get_fear_and_greed_index()
        value = fng.get('value', 50)
        
        if value < 25:
            return SentimentLevel.VERY_BEARISH
        elif value < 45:
            return SentimentLevel.BEARISH
        elif value < 55:
            return SentimentLevel.NEUTRAL
        elif value < 75:
            return SentimentLevel.BULLISH
        else:
            return SentimentLevel.VERY_BULLISH
    
    def generate_sentiment_report(self, symbol: str) -> Dict:
        """Generate comprehensive sentiment report"""
        fng = self.get_fear_and_greed_index()
        social = self.analyze_social_sentiment(symbol)
        sentiment_level = self.get_sentiment_level(symbol)
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'fear_and_greed': fng,
            'social_sentiment': social,
            'overall_sentiment': sentiment_level,
            'confidence': 0.75,  # Confidence score for the analysis
            'recommendation': self._get_recommendation(sentiment_level)
        }
    
    def _get_recommendation(self, sentiment: SentimentLevel) -> str:
        """Get trading recommendation based on sentiment"""
        recommendations = {
            SentimentLevel.VERY_BEARISH: 'Strong Sell',
            SentimentLevel.BEARISH: 'Sell',
            SentimentLevel.NEUTRAL: 'Hold',
            SentimentLevel.BULLISH: 'Buy',
            SentimentLevel.VERY_BULLISH: 'Strong Buy'
        }
        return recommendations.get(sentiment, 'Hold')
