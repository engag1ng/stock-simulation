import yfinance as yf
import sys
from dateutil import parser  # Robust ISO 8601 parser
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 50)

# Ensure correct usage
if len(sys.argv) != 4:
    print("Usage: python get_data.py <start_date> <end_date> <interval_days>")
    sys.exit(1)

try:
    # Parse ISO 8601 UTC datetimes and strip timezone
    start_date_iso = parser.isoparse(sys.argv[1]).replace(tzinfo=None)
    end_date_iso = parser.isoparse(sys.argv[2]).replace(tzinfo=None)
    
    # Truncate time part
    start_date = start_date_iso.strftime("%Y-%m-%d")
    end_date = end_date_iso.strftime("%Y-%m-%d")
    
    interval = sys.argv[3]
except Exception as e:
    print("Error parsing inputs:", e)
    sys.exit(1)


# Validate interval
valid_intervals = {
    "1m", "2m", "5m", "15m", "30m", "60m", "90m",
    "1h", "2h", "4h", "12h",
    "1d", "5d", "1wk", "1mo", "3mo"
}
if interval not in valid_intervals:
    print(f"Error: Unsupported interval '{interval}'")
    sys.exit(1)

# Fetch and save data
df = yf.download("^GSPC", start=start_date, end=end_date, interval=interval)

df['Return'] = df['Close'].pct_change()
df['Lag_1'] = df['Close'].shift(1)
df['Ret_1'] = df['Return'].shift(1)
df['SMA_20'] = df['Close'].rolling(window=20).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['StandardDeviation'] = df['Close'].rolling(window=20).std()
df['Variance'] = df['Close'].rolling(window=20).var()
df['EMA'] = df['Close'].ewm(span=3).mean()
df['MACD'] = df['SMA_20']-df['SMA_50']
df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

df.fillna(0, inplace=True)

print(df)
print(f"Saved data from {start_date} to {end_date} with interval '{interval}'")