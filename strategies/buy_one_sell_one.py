from .base import Strategy

class BuyOneSellOne(Strategy, name="buy_one_sell_one"):
    def execute(self, df, owned_stocks, price, capital):
        return (0.1, [], []) if owned_stocks == 0 else (-0.1, [], [])