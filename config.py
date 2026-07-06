import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Real CROO Configuration (used by croo_provider.py)
# CROO_SDK_KEY comes from the agent.croo.network dashboard after you
# register your agent + a service on it. NEVER commit a real value.
CROO_API_URL = os.getenv('CROO_API_URL', 'https://api.croo.network')
CROO_WS_URL = os.getenv('CROO_WS_URL', 'wss://api.croo.network/ws')
CROO_SDK_KEY = os.getenv('CROO_SDK_KEY', '')

# Server Configuration
AGENT_PORT = int(os.getenv('AGENT_PORT', 8000))
AGENT_HOST = os.getenv('AGENT_HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Market Analysis Config
ANALYSIS_TIMEFRAMES = ['1h', '4h', '1d']
ALERT_THRESHOLDS = {
    'price_change': 0.05,      # 5% change
    'volume_spike': 2.0,       # 2x average volume
    'sentiment_shift': 0.3     # 30% sentiment change
}
