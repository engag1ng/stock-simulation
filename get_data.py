import yfinance as yf
import sys
from dateutil import parser  # Robust ISO 8601 parser

# Ensure correct usage
if len(sys.argv) != 4:
    print("Usage: python fetch_data.py <start_date> <end_date> <interval_days>")
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
data = yf.download("^GSPC", start=start_date, end=end_date, interval=interval)
data.to_csv("stock_data.csv")
print(f"Saved data from {start_date} to {end_date} with interval '{interval}'")