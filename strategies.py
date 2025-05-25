from random import randint
def buy_one_sell_one(owned_stocks, price, capital):
    if owned_stocks == 0:
        return 1
    else:
        return -1

def random(owned_stocks, price, capital):
    return randint(-2, 2)