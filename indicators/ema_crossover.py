from . import register_indicator
from features.basic_features import feature_ema
import pandas as pd

@register_indicator("three_ema_crossover")
def indicator_three_ema_crossover(df):
    df['EMA_9'] = feature_ema(df, span=9)
    df['EMA_21'] = feature_ema(df, span=21)
    df['EMA_55'] = feature_ema(df, span=55)

    def apply_3_ema_crossover(row):
        ema9, ema21, ema55 = row['EMA_9'].item(), row['EMA_21'].item(), row['EMA_55'].item()
        if pd.isna(ema55) or ema55 == 0:
            return 0
        if ema9 > ema55 and ema21 > ema55:
            return min(((ema9 - ema55 + ema21 - ema55) / (2 * ema55)) * 100, 10)
        elif ema9 < ema55 and ema21 < ema55:
            return -min(((ema55 - ema9 + ema55 - ema21) / (2 * ema55)) * 100, 10)
        return 0

    return df.apply(apply_3_ema_crossover, axis=1)
