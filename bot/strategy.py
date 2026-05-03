import pandas as pd
import numpy as np

class Strategy:
    def __init__(self, rsi_period=14, bb_period=20, bb_std_dev=2):
        self.rsi_period = rsi_period
        self.bb_period = bb_period
        self.bb_std_dev = bb_std_dev

    def calculate_indicators(self, df):
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Calculate Bollinger Bands
        df['sma'] = df['close'].rolling(window=self.bb_period).mean()
        df['std'] = df['close'].rolling(window=self.bb_period).std()
        df['upper_bb'] = df['sma'] + (self.bb_std_dev * df['std'])
        df['lower_bb'] = df['sma'] - (self.bb_std_dev * df['std'])
        
        return df

    def get_signal(self, df):
        if df.empty or len(df) < self.bb_period:
            return 'HOLD'

        latest = df.iloc[-1]
        
        # Buy Signal Verification
        if latest['close'] < latest['lower_bb'] and latest['rsi'] < 30:
            return 'BUY'
            
        # Sell Signal Verification
        elif latest['close'] > latest['upper_bb'] or latest['rsi'] > 70:
            return 'SELL'
            
        return 'HOLD'
