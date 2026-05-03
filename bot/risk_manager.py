import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, initial_balance, max_risk_pct=0.02, stop_loss_pct=0.015, take_profit_pct=0.03, kill_switch_pct=0.10):
        self.initial_balance = initial_balance
        self.max_risk_pct = max_risk_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.kill_switch_pct = kill_switch_pct
        self.is_kill_switch_active = False

    def check_kill_switch(self, current_balance):
        drawdown = (self.initial_balance - current_balance) / self.initial_balance
        if drawdown >= self.kill_switch_pct:
            logger.critical(f"KILL SWITCH ACTIVATED! Drawdown of {drawdown*100:.2f}% exceeds {self.kill_switch_pct*100}% limit.")
            self.is_kill_switch_active = True
            return True
        return False

    def calculate_position_size(self, current_balance, current_price):
        if self.is_kill_switch_active:
            return 0
        risk_amount = current_balance * self.max_risk_pct
        position_size = risk_amount / current_price
        return position_size

    def check_exit_conditions(self, entry_price, current_price, position_type='LONG'):
        if position_type == 'LONG':
            loss_pct = (entry_price - current_price) / entry_price
            profit_pct = (current_price - entry_price) / entry_price
            
            if loss_pct >= self.stop_loss_pct:
                logger.info(f"Stop Loss Triggered at {current_price}")
                return True
            if profit_pct >= self.take_profit_pct:
                logger.info(f"Take Profit Triggered at {current_price}")
                return True
                
        return False
