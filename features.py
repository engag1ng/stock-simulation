import pandas as pd

def pct_return(df):
    return df['Close'].pct_change().fillna(0, inplace=True)

def lag(df, n=1):
    return df['Close'].shift(n).fillna(0, inplace=True)

def sma(df, n=10):
    return df['Close'].rolling(window=n).mean().fillna(0, inplace=True)

def standard_deviation(df, n=20):
    return df['Close'].rolling(window=n).std().fillna(0, inplace=True)

def variance(df, n=20):
    return df['Close'].rolling(window=n).var().fillna(0, inplace=True)

def ema(df, span=None, halflife=None):
    return df['Close'].ewm(span=span, halflife=halflife).mean().fillna(0)