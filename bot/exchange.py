import ccxt.async_support as ccxt
import logging
import asyncio

logger = logging.getLogger(__name__)

class ExchangeHandler:
    def __init__(self, initial_balance=1000.0, exchange_name='binance', *args, **kwargs):
        exchange_class = getattr(ccxt, exchange_name)
        # Initialize exchange without API keys for public data
        self.exchange = exchange_class({
            'enableRateLimit': True,
        })
        # Manage virtual balance locally
        self.virtual_balance = {'USDT': {'free': initial_balance}}
        logger.info(f"Initialized Paper Trading mode on {exchange_name} with balance {initial_balance} USDT")
        
    async def fetch_ohlcv(self, symbol, timeframe, limit=100):
        try:
            return await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return None

    async def fetch_balance(self):
        # Return the local virtual balance
        return self.virtual_balance

    def _update_balance(self, amount, price, side):
        # Simple virtual balance updating mechanism for demonstration
        usdt_free = self.virtual_balance.get('USDT', {}).get('free', 0)
        
        if side == 'buy':
            # In a real scenario we'd track base currency balance too, 
            # here we deduct the fiat (USDT) equivalent simply for kill-switch tracking
            self.virtual_balance['USDT']['free'] = usdt_free - amount
        elif side == 'sell':
            self.virtual_balance['USDT']['free'] = usdt_free + amount


    async def create_market_buy_order(self, symbol, amount):
        try:
            order = {'info': {}, 'symbol': symbol, 'type': 'market', 'side': 'buy', 'amount': amount, 'status': 'closed'}
            logger.info(f"[PAPER TRADING] Buy Order Filled: {order}")
            # Mock update balance if we knew price, but main.py tracks it too.
            return order
        except Exception as e:
            logger.error(f"Error creating mock buy order: {e}")
            return None

    async def create_market_sell_order(self, symbol, amount):
        try:
            order = {'info': {}, 'symbol': symbol, 'type': 'market', 'side': 'sell', 'amount': amount, 'status': 'closed'}
            logger.info(f"[PAPER TRADING] Sell Order Filled: {order}")
            return order
        except Exception as e:
            logger.error(f"Error creating mock sell order: {e}")
            return None

    async def close(self):
        await self.exchange.close()
