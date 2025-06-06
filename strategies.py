from random import random, randint
from indicators import *

# return buy_number, [stop_loss_price, stop_loss_number], [stop_win_price, stop_win_number]
def buy_one_sell_one(owned_stocks, price, capital):
    if owned_stocks == 0:
        return 0.1, [], []
    else:
        return -0.1, [], []

def random_buy_sell(df, owned_stocks, price, capital):
    return randint(-1, 1) * random(), [price*0.97, -0.1], [price*1.07, -0.1]

def strategy_three_ema_crossover(df, owned_stocks, price, capital):
    crossover_now = df['indicator_three_ema_crossover'][-1:].item()
    if crossover_now > 1:
        max_buy = capital // price
        buy_number = max_buy/10*crossover_now
        return buy_number, [price*0.93, buy_number], [price*1.05, buy_number]

    if crossover_now < -1:
        sell_number = owned_stocks/5*crossover_now
        return sell_number, False, False

    else:
        return 0, False, False
    