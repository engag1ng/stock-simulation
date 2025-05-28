from random import random, randint
def buy_one_sell_one(owned_stocks, price, capital):
    if owned_stocks == 0:
        return 1
    else:
        return -1

def random_buy_sell(owned_stocks, price, capital):
    return randint(-1, 1) * random()