import asyncio
import os
import logging
import pandas as pd
from dotenv import load_dotenv
from bot.exchange import ExchangeHandler
from bot.strategy import Strategy
from bot.risk_manager import RiskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_bot():
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    symbol = os.getenv('SYMBOL', 'BTC/USDT')
    timeframe = os.getenv('TIMEFRAME', '1m')
    initial_balance = float(os.getenv('INITIAL_BALANCE', '1000.0'))

    exchange = ExchangeHandler(initial_balance=initial_balance, exchange_name='binance')
    strategy = Strategy()
    risk_manager = RiskManager(initial_balance=initial_balance)

    in_position = False
    entry_price = 0.0
    position_amount = 0.0

    logger.info(f"Starting Trading Bot for {symbol} on {timeframe} timeframe")
    
    try:
        while True:
            # 1. Fetch Balances & Check Kill Switch
            balance_info = await exchange.fetch_balance()
            if balance_info:
                # Mocking current balance logic using USDT equivalent for simplicity
                current_balance = balance_info.get('USDT', {}).get('free', initial_balance)
                if risk_manager.check_kill_switch(current_balance):
                    logger.critical('Bot halted due to Kill Switch.')
                    if in_position:
                        logger.critical('Liquidating remaining positions.')
                        await exchange.create_market_sell_order(symbol, position_amount)
                    break

            # 2. Fetch Data
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            if not ohlcv:
                await asyncio.sleep(10)
                continue
                
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # 3. Calculate Indicators & Get Signal
            df = strategy.calculate_indicators(df)
            signal = strategy.get_signal(df)
            current_price = df.iloc[-1]['close']
            
            logger.info(f"Price: {current_price} | RSI: {df.iloc[-1]['rsi']:.2f} | Signal: {signal}")

            # 4. Process Exits (Stop Loss / Take Profit)
            if in_position:
                exit_signal_triggered = risk_manager.check_exit_conditions(entry_price, current_price)
                if exit_signal_triggered or signal == 'SELL':
                    logger.info(f"Executing SELL at {current_price}")
                    # await exchange.create_market_sell_order(symbol, position_amount)
                    logger.info(f"Paper Trading Simulation: Sold {position_amount} amount")
                    in_position = False
                    entry_price = 0.0
                    position_amount = 0.0

            # 5. Process Entries
            elif signal == 'BUY' and not in_position:
                amount_to_buy_usdt = risk_manager.calculate_position_size(initial_balance, current_price)
                if amount_to_buy_usdt > 0:
                    logger.info(f"Executing BUY at {current_price}")
                    # order = await exchange.create_market_buy_order(symbol, amount_to_buy)
                    position_amount = amount_to_buy_usdt
                    entry_price = current_price
                    in_position = True
                    logger.info(f"Paper Trading Simulation: Bought {position_amount} amount")
            
            # Rate limiting / Loop delay
            await asyncio.sleep(60)
            
    except asyncio.CancelledError:
        logger.info("Bot execution cancelled.")
    except Exception as e:
        logger.error(f"Unhandled error in main loop: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot manually stopped via KeyboardInterrupt.")
