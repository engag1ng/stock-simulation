# Get data
## Get data
# Prepare data
## Denormalize data
## Add variables
# Simulate ticks
## Execute algorithm
## Execute buy and sell actions
# Evaluate
## Report results
## If results are good backtest
# Backtest
## Get real data
## Add variables
## Run Simulation on real data

from math_sim import simulate_stock_paths, plot_simulation_report, plot_denormalized_paths
from strategies import buy_one_sell_one, random
import yfinance as yf
import matplotlib.pyplot as plt

def get_data(source="math_sim", ticker="^GSPC", period="10y"):
    if source == "math_sim":
        period_table = {
            "10y": 2520,
            "5y": 1260,
            "1y": 252,
        }
        num_paths = 20
        paths, sim_returns, real_returns = simulate_stock_paths(
            ticker=ticker,
            num_paths=num_paths,
            path_length=round((2*period_table[period])/num_paths),
            period=period,
            verbose=False
        )
        plot_simulation_report(paths, sim_returns, real_returns)

        start_price = float(yf.download(ticker, period="1d", progress=False)['Close'].iloc[0])
        
        data = denormalize_data(paths, start_price)

    if source == "real":
        data = yf.download(ticker, period=period, progress=False)

    return data, source, ticker, period

def denormalize_data(paths, start_price):
    denormalized_data = []
    for path in paths:
        denormalized_values = [start_price*value for value in path[1:]]
        denormalized_data.append(denormalized_values)
    return denormalized_data

def simulation(data, source, strategy, capital=10000, transaction_fee=0.01):
    stocks_owned = 0

    arr_stocks_owned = []
    arr_price = []
    arr_capital = []
    arr_wealth = []
             
    if source == "real":
        for row in data.itertuples():
            current_price = row._1
            arr_price.append(current_price)

            action = strategy(current_price, stocks_owned, capital)
            if action < 0:  # Selling
                if abs(action) > stocks_owned:
                    action = -stocks_owned  # Clamp sell to max stocks owned

            elif action > 0:  # Buying
                max_affordable = capital // (current_price * (1 + transaction_fee))
                if action > max_affordable:
                    action = int(max_affordable)  # Clamp to how much you can afford

            stocks_owned += action
            arr_stocks_owned.append(stocks_owned)
            transaction_cost = transaction_fee * abs(action) * current_price
            capital -= current_price*action
            capital -= transaction_cost
            arr_capital.append(capital)
            wealth = stocks_owned*current_price+capital
            arr_wealth.append(wealth)
            if wealth <= 0:
                    break

    elif source == "math_sim":
        for path in data: # Possibilities  
            for i in range(len(path)): # Ticks
                current_price = path[i]
                arr_price.append(current_price)
                bought_stocks = strategy(stocks_owned, current_price, capital)
                stocks_owned += bought_stocks
                arr_stocks_owned.append(stocks_owned)
                transaction_cost = transaction_fee * abs(bought_stocks) * current_price
                capital -= current_price*bought_stocks
                capital -= transaction_cost
                arr_capital.append(capital)
                wealth = stocks_owned*current_price+capital
                arr_wealth.append(wealth)
                if wealth <= 0:
                    break
                
            print(f"Net Worth: {wealth}")
            print("\nNew Simulation")       
    else:
        raise TypeError(f"No such source: '{source}'")

    return arr_price, arr_stocks_owned, arr_capital, arr_wealth

def evaluate(arr_price, arr_stocks_owned, arr_capital, arr_wealth):
    plt.figure(figsize=(16, 10))

    # Price
    plt.subplot(2, 2, 1)
    plt.plot(arr_price, label="Price", color="blue")
    plt.title("Price Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Price")
    plt.grid(True)

    # Stocks Owned
    plt.subplot(2, 2, 2)
    plt.plot(arr_stocks_owned, label="Stocks Owned", color="orange")
    plt.title("Stocks Owned Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Number of Shares")
    plt.grid(True)

    # Capital
    plt.subplot(2, 2, 3)
    plt.plot(arr_capital, label="Capital", color="green")
    plt.title("Capital Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Capital ($)")
    plt.grid(True)

    # Net Worth
    plt.subplot(2, 2, 4)
    plt.plot(arr_wealth, label="Net Worth", color="purple")
    plt.title("Net Worth Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Net Worth ($)")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    print(f"Net gain: {arr_wealth[-1] - arr_wealth[0]}")

data, source, ticker, period = get_data("real", period="10y")

arr_price, arr_stocks_owned, arr_capital, arr_wealth = simulation(data, source, random, 10000000)

evaluate(arr_price, arr_stocks_owned, arr_capital, arr_wealth)