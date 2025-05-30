import pandas as pd
from features import *

def three_ema_crossover(df):
    df['EMA']