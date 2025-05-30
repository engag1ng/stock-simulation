from random import random, randint
# return buy_number, [stop_loss_price, stop_loss_number], [stop_win_price, stop_win_number]
def buy_one_sell_one(owned_stocks, price, capital):
    if owned_stocks == 0:
        return 0.1, [], []
    else:
        return -0.1, [], []

def random_buy_sell(owned_stocks, price, capital):
    return randint(-1, 1) * random(), [price*0.97, -0.1], [price*1.07, -0.1]