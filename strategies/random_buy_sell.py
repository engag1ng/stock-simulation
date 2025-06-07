from .base import Strategy
from random import random, randint

class RandomBuySell(Strategy, name="random_buy_sell"):
    def execute(self, df, owned_stocks, price, capital):
        return randint(-1, 1) * random(), [price * 0.97, -0.1], [price * 1.07, -0.1]
