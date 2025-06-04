import pandas as pd
from features import *

def three_ema_crossover(df):
    df['EMA_9'] = ema(df, span=9)
    df['EMA_21'] = ema(df, span=21)
    df['EMA_55'] = ema(df, span=55)
    
    def apply_3_ema_crossover(row):
        ema9, ema21, ema55 = row['EMA_9'].item(), row['EMA_21'].item(), row['EMA_55'].item()
        
        if ema55 == 0 or pd.isna(ema55):
            return 0

        # If both EMAs are above EMA_55 (bullish)
        if ema9 > ema55 and ema21 > ema55:
            # Normalize strength based on average % distance
            strength = ((ema9 - ema55) + (ema21 - ema55)) / (2 * ema55)
            return min(strength * 100, 10)  # scale and clip to max 10

        # If both EMAs are below EMA_55 (bearish)
        elif ema9 < ema55 and ema21 < ema55:
            strength = ((ema55 - ema9) + (ema55 - ema21)) / (2 * ema55)
            return -min(strength * 100, 10)  # scale and clip to -10

        # If mixed trend
        else:
            return  0

    return df.apply(apply_3_ema_crossover, axis=1)