from math_sim import simulate_stock_paths, plot_simulation_report, plot_denormalized_paths
from strategies import buy_one_sell_one, random_buy_sell
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

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

def simulation(data, source, strategy, capital=10000, transaction_fee=0.01, yearly_custody_fee=0.02):
    stocks_owned = 0
             
    results = {}
    if source == "real":
        arr_stocks_owned = []
        arr_price = []
        arr_capital = []
        arr_wealth = []
        for index, row in enumerate(data.itertuples()):
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
            if index%365 == 0:
                capital -= capital*yearly_custody_fee
            arr_capital.append(capital)
            wealth = stocks_owned*current_price+capital
            arr_wealth.append(wealth)
            if wealth <= 0:
                    break

        results['stocks_owned'] = arr_stocks_owned
        results['price'] = arr_price
        results['capital'] = arr_capital
        results['wealth'] = arr_wealth


    elif source == "math_sim":
        results = []
        for path in data: # Possibilities 
            path_dict = {} 
            arr_stocks_owned = []
            arr_price = []
            arr_capital = []
            arr_wealth = []
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
            path_dict['stocks_owned'] = arr_stocks_owned
            path_dict['price'] = arr_price
            path_dict['capital'] = arr_capital
            path_dict['wealth'] = arr_wealth
            results.append(path_dict)
            print(f"Net Worth: {wealth}\n")

           
    else:
        raise TypeError(f"No such source: '{source}'")

    return results

def evaluate(results):
    plt.figure(figsize=(16, 10))

    # Create a colormap with enough distinct colors
    num_paths = len(results) if isinstance(results, list) else 1
    colors = plt.cm.viridis(np.linspace(0, 1, num_paths))

    # Price
    plt.subplot(2, 2, 1)
    if isinstance(results, dict):  # Only one path
        plt.plot(results['price'], label="Price", color="blue")
    else:
        for idx, path in enumerate(results):
            plt.plot(path['price'], label=f"Path {idx+1}", color=colors[idx])
    plt.title("Price Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Price")
    plt.grid(True)

    # Stocks Owned
    plt.subplot(2, 2, 2)
    if isinstance(results, dict):  # Only one path
        plt.plot(results['stocks_owned'], label="Stocks Owned", color="orange")
    else:
        for idx, path in enumerate(results):
            plt.plot(path['stocks_owned'], label=f"Path {idx+1}", color=colors[idx])
    plt.title("Stocks Owned Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Number of Shares")
    plt.grid(True)

    # Capital
    plt.subplot(2, 2, 3)
    if isinstance(results, dict):  # Only one path
        plt.plot(results['capital'], label="Capital", color="green")
    else:
        for idx, path in enumerate(results):
            plt.plot(path['capital'], label=f"Path {idx+1}", color=colors[idx])
    plt.title("Capital Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Capital ($)")
    plt.grid(True)

    # Net Worth
    plt.subplot(2, 2, 4)
    if isinstance(results, dict):  # Only one path
        plt.plot(results['wealth'], label="Net Worth", color="purple")
    else:
        for idx, path in enumerate(results):
            plt.plot(path['wealth'], label=f"Path {idx+1}", color=colors[idx])
    plt.title("Net Worth Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Net Worth ($)")
    plt.grid(True)

    # Show a legend for different paths
    plt.tight_layout()
    plt.show()

    print(f"Net gain: {results[-1]['wealth'][-1] - results[0]['wealth'][0]}" if isinstance(results, list) else f"Net gain: {results['wealth'][-1] - results['wealth'][0]}")

data, source, ticker, period = get_data("math_sim", ticker="AAPL", period="10y")

results = simulation(data, source, random_buy_sell, 1000)

evaluate(results)