import pandas as pd

def feature_pct_return(df):
    return df['Close'].pct_change().fillna(0)

def feature_lag(df, n=1):
    return df['Close'].shift(n).fillna(0)

def feature_sma(df, n=10):
    return df['Close'].rolling(window=n).mean().fillna(0)

def feature_standard_deviation(df, n=20):
    return df['Close'].rolling(window=n).std().fillna(0)

def feature_variance(df, n=20):
    return df['Close'].rolling(window=n).var().fillna(0)

def feature_ema(df, span=None, halflife=None):
    return df['Close'].ewm(span=span, halflife=halflife).mean().fillna(0)

def feature_log_return(df):
    return np.log(df['Close'] / df['Close'].shift(1)).fillna(0)

def feature_zscore(df, n=20):
    rolling_mean = df['Close'].rolling(window=n).mean()
    rolling_std = df['Close'].rolling(window=n).std()
    zscore = (df['Close'] - rolling_mean) / rolling_std
    return zscore.fillna(0)

def feature_rate_of_change(df, n=10):
    prev = df['Close'].shift(n)
    roc = (df['Close'] - prev) / prev * 100
    return roc.fillna(0)

def feature_rolling_max(df, n=20):
    return df['Close'].rolling(window=n).max().fillna(0)

def feature_rolling_min(df, n=20):
    return df['Close'].rolling(window=n).min().fillna(0)

def feature_donchian_channels(df, n=20):
    upper = feature_rolling_max(df, n)
    lower = feature_rolling_min(df, n)
    middle = (upper + lower) / 2
    return pd.DataFrame({
        'donchian_upper': upper,
        'donchian_middle': middle,
        'donchian_lower': lower
    })