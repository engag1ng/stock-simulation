import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

from mathSim import plot_simulation_report, simulate_stock_paths

def denormalize_data(paths, start_price):
    return [[start_price * value for value in path[1:]] for path in paths]

def get_simulated_data(ticker, period, number_of_paths, plot_sim_report=False):
    period_table = {
        "10y": 2520,
        "5y": 1260,
        "1y": 252,
    }
    paths, sim_returns, real_returns = simulate_stock_paths(
        ticker=ticker,
        num_paths=number_of_paths,
        path_length=round((2 * period_table[period]) / number_of_paths), # path_length = 2*period / number_of_paths; This gets the best results
        period=period,
        verbose=False
    )
    if plot_sim_report:
        plot_simulation_report(paths, sim_returns, real_returns)
    start_price = float(yf.download(ticker, period="1d", progress=False)['Close'].iloc[0])
    data = denormalize_data(paths, start_price)

    return data

def get_real_data(ticker, period):
    return yf.download(ticker, period=period, progress=False)