import yfinance as yf
import matplotlib
import datetime
import pandas as pd

pd.set_option('display.max_rows', None)  # Show all rows

data = yf.download("^GSPC", period="10y", interval="1d")

data.to_csv("stock_data.csv")