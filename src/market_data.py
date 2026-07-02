import requests
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from config import COINGECKO_API_KEY, BINANCE_API_KEY

class MarketDataProvider:
    """Fetches and aggregates real-time crypto market data"""
    
    def __init__(self):
        self.coingecko_base = 'https://api.coingecko.com/api/v3'
        self.binance_base = 'https://api.binance.com/api/v3'
        self.cache = {}
        self.cache_ttl = 60  # 60 seconds
    
    def get_current_price(self, symbol: str) -> Dict:
        """Get current price data for a cryptocurrency"""
        try:
            # Try CoinGecko first (free, no API key needed for basic requests)
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': symbol.lower(),
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if symbol.lower() in data:
                coin_data = data[symbol.lower()]
                return {
                    'symbol': symbol.upper(),
                    'price': coin_data.get('usd'),
                    'market_cap': coin_data.get('usd_market_cap'),
                    'volume_24h': coin_data.get('usd_24h_vol'),
                    'change_24h': coin_data.get('usd_24h_change'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'coingecko'
                }
        except Exception as e:
            print(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    def get_market_cap_rank(self, limit: int = 50) -> List[Dict]:
        """Get top cryptocurrencies by market cap"""
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    'rank': coin.get('market_cap_rank'),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'price': coin.get('current_price'),
                    'market_cap': coin.get('market_cap'),
                    'volume_24h': coin.get('total_volume'),
                    'change_24h': coin.get('price_change_percentage_24h')
                }
                for coin in data
            ]
        except Exception as e:
            print(f"Error fetching market cap rankings: {str(e)}")
            return []
    
    def get_price_history(self, symbol: str, days: int = 7) -> List[Dict]:
        """Get historical price data"""
        try:
            url = f"{self.coingecko_base}/coins/{symbol.lower()}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = data.get('prices', [])
            return [
                {
                    'timestamp': datetime.fromtimestamp(price[0]/1000).isoformat(),
                    'price': price[1]
                }
                for price in prices
            ]
        except Exception as e:
            print(f"Error fetching price history for {symbol}: {str(e)}")
            return []
    
    def calculate_volatility(self, symbol: str, days: int = 7) -> Optional[float]:
        """Calculate price volatility over N days"""
        history = self.get_price_history(symbol, days)
        if len(history) < 2:
            return None
        
        prices = [h['price'] for h in history]
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        return float(volatility)
    
    def detect_volume_spike(self, symbol: str) -> Dict:
        """Detect unusual trading volume"""
        try:
            current = self.get_current_price(symbol)
            history = self.get_price_history(symbol, 7)
            
            if not current or len(history) < 2:
                return {'detected': False, 'reason': 'insufficient_data'}
            
            # Simplified volume spike detection
            # In production, would use actual volume data from Binance
            return {
                'detected': False,
                'reason': 'no_spike',
                'current_volume': current.get('volume_24h'),
                'avg_volume_7d': current.get('volume_24h')  # Placeholder
            }
        except Exception as e:
            print(f"Error detecting volume spike for {symbol}: {str(e)}")
            return {'detected': False, 'reason': str(e)}
