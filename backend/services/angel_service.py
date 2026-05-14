import logging
import pyotp
from SmartApi import SmartConnect
from config import settings

logger = logging.getLogger(__name__)

class AngelOneService:
    def __init__(self):
        self.smart_api = None
        self.jwt_token = None
        self.refresh_token = None
        self.feed_token = None

    def _login(self):
        """Authenticate with Angel One SmartAPI."""
        try:
            if not settings.ANGEL_API_KEY or not settings.ANGEL_CLIENT_ID:
                logger.warning("Angel One credentials missing. Skipping login.")
                return False

            self.smart_api = SmartConnect(api_key=settings.ANGEL_API_KEY)
            
            # Generate TOTP
            totp = pyotp.TOTP(settings.ANGEL_TOTP_KEY).now()
            
            data = self.smart_api.generateSession(
                settings.ANGEL_CLIENT_ID, 
                settings.ANGEL_PASSWORD, 
                totp
            )

            if data['status']:
                self.jwt_token = data['data']['jwtToken']
                self.refresh_token = data['data']['refreshToken']
                self.feed_token = self.smart_api.getfeedToken()
                logger.info("✓ Angel One session initialized")
                return True
            else:
                logger.error(f"✗ Angel One login failed: {data['message']}")
                return False
        except Exception as e:
            logger.error(f"✗ Angel One exception during login: {e}")
            return False

    def ensure_session(self):
        """Ensure we have a valid session."""
        if not self.smart_api or not self.jwt_token:
            return self._login()
        return True

    def get_index_quote(self, symbol: str, token: str):
        """Fetch quote for an index."""
        if not self.ensure_session():
            return None
        
        try:
            # exchange: NSE for indices usually
            # symbol: Nifty 50, Bank Nifty etc.
            # token: 99926037 (Nifty), 99926036 (Bank Nifty)
            response = self.smart_api.getLTP("NSE", symbol, token)
            if response['status']:
                return response['data']
            return None
        except Exception as e:
            logger.error(f"Angel One fetch quote error: {e}")
            return None

    def get_option_chain(self, symbol: str):
        """Fetch option chain for a symbol."""
        # Note: Angel One API for option chain might require specific parameters
        # For now, we'll keep it as a placeholder or use a generic fetch
        if not self.ensure_session():
            return None
        return None # Implementation depends on specific SmartAPI endpoints

    def get_indices(self):
        """Fetch LTP for major indices."""
        if not self.ensure_session():
            return None
        
        indices = [
            {"exchange": "NSE", "symbol": "Nifty 50", "token": "99926037"},
            {"exchange": "NSE", "symbol": "Nifty Bank", "token": "99926036"},
            {"exchange": "NSE", "symbol": "Nifty Fin Service", "token": "99926045"},
        ]
        
        results = {}
        for idx in indices:
            try:
                resp = self.smart_api.getLTP(idx["exchange"], idx["symbol"], idx["token"])
                if resp['status']:
                    results[idx["symbol"]] = resp['data']
            except Exception as e:
                logger.error(f"Error fetching {idx['symbol']} from Angel: {e}")
        
        return results

# Singleton
angel = AngelOneService()
