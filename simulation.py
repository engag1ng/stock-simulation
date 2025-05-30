from math_sim import simulate_stock_paths, plot_simulation_report, plot_denormalized_paths
from strategies import buy_one_sell_one, random_buy_sell
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np


def denormalize_data(paths, start_price):
    return [[start_price * value for value in path[1:]] for path in paths]


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
            path_length=round((2 * period_table[period]) / num_paths),
            period=period,
            verbose=False
        )
        plot_simulation_report(paths, sim_returns, real_returns)
        start_price = float(yf.download(ticker, period="1d", progress=False)['Close'].iloc[0])
        data = denormalize_data(paths, start_price)

    elif source == "real":
        data = yf.download(ticker, period=period, progress=False)

    else:
        raise ValueError(f"Invalid source: {source}")

    return data, source, ticker, period


def apply_stop_conditions(current_price, registry, condition_fn):
    actions_to_take = 0
    keys_to_remove = []

    for price, amount in registry.items():
        if condition_fn(current_price, float(price)):
            actions_to_take += amount
            keys_to_remove.append(price)

    for key in keys_to_remove:
        del registry[key]

    return actions_to_take


def run_strategy_loop(prices, strategy, capital, transaction_fee, yearly_custody_fee):
    stocks_owned = 0
    stop_losses_registry = {}
    stop_win_registry = {}

    arr_price, arr_capital, arr_stocks_owned, arr_wealth = [], [], [], []

    for i, current_price in enumerate(prices):
        # Convert current_price to float if it's a NumPy scalar or array
        if isinstance(current_price, np.ndarray):
            if current_price.size == 1:
                current_price = current_price.item()
            else:
                current_price = float(current_price[0])  # fallback
        else:
            current_price = float(current_price)

        arr_price.append(current_price)

        action, stop_loss, stop_win = strategy(stocks_owned, current_price, capital)

        if stop_loss:
            stop_losses_registry[float(stop_loss[0])] = stop_losses_registry.get(float(stop_loss[0]), 0) + stop_loss[1]

        if stop_win:
            stop_win_registry[float(stop_win[0])] = stop_win_registry.get(float(stop_win[0]), 0) + stop_win[1]

        action -= apply_stop_conditions(current_price, stop_losses_registry, lambda p, k: p < k)
        action += apply_stop_conditions(current_price, stop_win_registry, lambda p, k: p > k)

        if action < 0:
            action = max(action, -stocks_owned)
        elif action > 0:
            max_affordable = capital / (current_price * (1 + transaction_fee))
            action = min(action, max_affordable)

        stocks_owned += action
        arr_stocks_owned.append(stocks_owned)

        transaction_cost = transaction_fee * abs(action) * current_price
        capital -= action * current_price + transaction_cost

        if i % 365 == 0 and i > 0:
            capital -= capital * yearly_custody_fee

        arr_capital.append(float(capital))
        wealth = stocks_owned * current_price + capital
        arr_wealth.append(float(wealth))

        if wealth <= 0:
            break

    return {
        'price': arr_price,
        'capital': arr_capital,
        'stocks_owned': arr_stocks_owned,
        'wealth': arr_wealth
    }


def simulation(data, source, strategy, capital=10000, transaction_fee=0.01, yearly_custody_fee=0.02):
    if source == "real":
        prices = data['Close'].values
        return run_strategy_loop(prices, strategy, capital, transaction_fee, yearly_custody_fee)

    elif source == "math_sim":
        results = []
        for path in data:
            result = run_strategy_loop(path, strategy, capital, transaction_fee, yearly_custody_fee)
            print(f"Net Worth: {result['wealth'][-1]}")
            results.append(result)
        return results

    else:
        raise TypeError(f"No such source: '{source}'")


def evaluate(results):
    plt.figure(figsize=(16, 10))
    num_paths = len(results) if isinstance(results, list) else 1
    colors = plt.cm.viridis(np.linspace(0, 1, num_paths))

    def plot_subplot(index, title, ylabel, key, color_override=None):
        plt.subplot(2, 2, index)
        if isinstance(results, dict):
            plt.plot(results[key], label=key.title(), color=color_override or "blue")
        else:
            for i, r in enumerate(results):
                plt.plot(r[key], label=f"Path {i+1}", color=colors[i])
        plt.title(title)
        plt.xlabel("Tick")
        plt.ylabel(ylabel)
        plt.grid(True)

    plot_subplot(1, "Price Over Time", "Price", "price")
    plot_subplot(2, "Stocks Owned Over Time", "Number of Shares", "stocks_owned", color_override="orange")
    plot_subplot(3, "Capital Over Time", "Capital ($)", "capital", color_override="green")
    plot_subplot(4, "Net Worth Over Time", "Net Worth ($)", "wealth", color_override="purple")

    plt.tight_layout()
    plt.show()

    if isinstance(results, list):
        print(f"Net gain: {results[-1]['wealth'][-1] - results[0]['wealth'][0]}")
    else:
        print(f"Net gain: {results['wealth'][-1] - results['wealth'][0]}")


# === Execution ===
data, source, ticker, period = get_data("real", ticker="^GSPC", period="10y")
results = simulation(data, source, random_buy_sell, 1000)
evaluate(results)