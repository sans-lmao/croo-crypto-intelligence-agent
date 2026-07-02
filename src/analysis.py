from typing import Dict, List, Optional
from datetime import datetime
from src.market_data import MarketDataProvider
from src.sentiment import SentimentAnalyzer

class MarketAnalysisEngine:
    """Core analysis engine for generating market intelligence"""
    
    def __init__(self):
        self.market_data = MarketDataProvider()
        self.sentiment = SentimentAnalyzer()
        self.alerts = []
    
    def analyze_cryptocurrency(self, symbol: str) -> Dict:
        """Perform comprehensive analysis on a cryptocurrency"""
        price_data = self.market_data.get_current_price(symbol)
        if not price_data:
            return {'error': f'Could not fetch data for {symbol}'}
        
        volatility = self.market_data.calculate_volatility(symbol, 7)
        sentiment = self.sentiment.generate_sentiment_report(symbol)
        volume_spike = self.market_data.detect_volume_spike(symbol)
        
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price_analysis': {
                'current_price': price_data.get('price'),
                'change_24h': price_data.get('change_24h'),
                'market_cap': price_data.get('market_cap'),
                'volume_24h': price_data.get('volume_24h')
            },
            'technical_analysis': {
                'volatility_7d': volatility,
                'volume_spike_detected': volume_spike.get('detected')
            },
            'sentiment_analysis': sentiment,
            'alerts': self._generate_alerts(symbol, price_data, sentiment, volatility)
        }
        
        return analysis
    
    def _generate_alerts(self, symbol: str, price_data: Dict, sentiment: Dict, volatility: Optional[float]) -> List[Dict]:
        """Generate trading alerts based on analysis"""
        alerts = []
        
        # Price change alert
        change_24h = price_data.get('change_24h', 0)
        if change_24h > 10:
            alerts.append({
                'type': 'price_surge',
                'severity': 'high',
                'message': f'{symbol} up {change_24h:.2f}% in 24h',
                'value': change_24h
            })
        elif change_24h < -10:
            alerts.append({
                'type': 'price_drop',
                'severity': 'high',
                'message': f'{symbol} down {abs(change_24h):.2f}% in 24h',
                'value': change_24h
            })
        
        # Sentiment alert
        overall_sentiment = sentiment.get('overall_sentiment')
        if overall_sentiment in ['very_bullish', 'very_bearish']:
            alerts.append({
                'type': 'extreme_sentiment',
                'severity': 'medium',
                'message': f'Extreme {overall_sentiment} sentiment detected',
                'sentiment': overall_sentiment
            })
        
        # Volatility alert
        if volatility and volatility > 0.15:
            alerts.append({
                'type': 'high_volatility',
                'severity': 'medium',
                'message': f'High volatility detected ({volatility:.2%})',
                'value': volatility
            })
        
        return alerts
    
    def find_trading_opportunities(self, min_market_cap: int = 1_000_000_000, max_market_cap: int = 10_000_000_000) -> List[Dict]:
        """Identify cryptocurrencies with potential trading opportunities"""
        rankings = self.market_data.get_market_cap_rank(limit=100)
        opportunities = []
        
        for coin in rankings:
            if not coin['market_cap']:
                continue
            
            if min_market_cap <= coin['market_cap'] <= max_market_cap:
                change = coin.get('change_24h', 0)
                
                # Look for interesting patterns
                if -5 < change < 5:  # Stable price
                    volatility = self.market_data.calculate_volatility(coin['symbol'], 7)
                    if volatility and volatility > 0.10:  # But volatile historically
                        opportunities.append({
                            'symbol': coin['symbol'],
                            'name': coin['name'],
                            'rank': coin['rank'],
                            'price': coin['price'],
                            'market_cap': coin['market_cap'],
                            'change_24h': change,
                            'volatility_7d': volatility,
                            'opportunity_score': 0.75,
                            'reasoning': 'Stable price with historical volatility - potential breakout candidate'
                        })
        
        return sorted(opportunities, key=lambda x: x.get('opportunity_score', 0), reverse=True)[:10]
    
    def get_market_overview(self) -> Dict:
        """Get overall market overview and statistics"""
        top_coins = self.market_data.get_market_cap_rank(limit=10)
        fng = self.sentiment.get_fear_and_greed_index()
        
        gainers = sorted(top_coins, key=lambda x: x.get('change_24h', 0), reverse=True)[:3]
        losers = sorted(top_coins, key=lambda x: x.get('change_24h', 0))[:3]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'fear_and_greed': fng,
            'top_gainers': gainers,
            'top_losers': losers,
            'total_coins_analyzed': len(top_coins),
            'market_sentiment': fng.get('classification')
        }
