"""
Stock Trading Strategy Simulator and Evaluator

This module provides a framework to simulate and evaluate stock trading strategies
on both real and simulated market data. It includes functionality to:

- Fetch real historical stock data.
- Generate simulated stock price paths.
- Run a trading strategy over time with capital management, transaction fees,
  yearly custody fees, and stop loss/win conditions.
- Visualize the strategy performance via price, capital, and net worth plots.
- Summarize results with statistical metrics for simulated outcomes.

Key components:
- `apply_stop_conditions`: Applies stop loss or stop win triggers to positions.
- `run_strategy_loop`: Core loop running the strategy through market data and managing portfolio.
- Integration with user interface (UI) to set parameters.
- Uses strategy and indicator registries for flexible strategy selection and feature precomputation.

Requires:
- yfinance, matplotlib, numpy, pandas
- Custom modules: getData, mathSim, ui, strategies, indicators

"""
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from getData import get_real_data, get_simulated_data
from mathSim import simulate_stock_paths
from ui import spawn_ui
from strategies.base import Strategy
import strategies.three_ema_crossover
from indicators import indicator_registry
from indicators.ema_crossover import indicator_three_ema_crossover

def apply_stop_conditions(current_price, registry, condition_fn):
    """
    Check and apply stop loss or stop win conditions.

    Args:
        current_price (float): Current market price.
        registry (dict): Dictionary mapping price levels to number of shares held
                         under stop conditions.
        condition_fn (callable): Function taking (current_price, stop_price) and
                                 returning True if stop condition triggered.

    Returns:
        int: Number of shares to be bought/sold as a result of triggered stop conditions.

    Side effects:
        Removes triggered stop conditions from the registry.

    """
    actions_to_take = 0
    keys_to_remove = []

    for price, amount in registry.items():
        if condition_fn(current_price, float(price)):
            actions_to_take += amount
            keys_to_remove.append(price)

    for key in keys_to_remove:
        del registry[key]

    return actions_to_take


def run_strategy_loop(data, strategy, capital, transaction_fee, yearly_custody_fee, to_precompute):
    """
    Simulate trading strategy over provided market data.

    Args:
        data (pandas.DataFrame): Market data with at least a 'Close' column.
        strategy (Strategy): Trading strategy instance with an execute method.
        capital (float): Initial capital available for trading.
        transaction_fee (float): Proportional transaction fee per trade (e.g., 0.001 for 0.1%).
        yearly_custody_fee (float): Annual custody fee rate deducted from capital yearly.
        to_precompute (list): List of indicator functions to apply on data before simulation.

    Returns:
        dict: Dictionary containing time series lists:
            - 'price': Market prices over time.
            - 'capital': Available capital over time.
            - 'stocks_owned': Number of shares owned over time.
            - 'wealth': Total net worth (capital + stocks value) over time.

    Notes:
        - Applies precomputed features for strategy decision making.
        - Enforces stop loss and stop win logic.
        - Accounts for transaction costs and custody fees.
        - Stops simulation if net worth reaches zero or below.

    """
    # --- Precompute features and indictators ---
    for stat in to_precompute:
        data[stat.__name__] = stat(data)

    prices = data['Close'].values
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

        action, stop_loss, stop_win = strategy.execute(data[:i+1], stocks_owned, current_price, capital)

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

# --- Parameters ---
params = spawn_ui()

capital=params[0]
transaction_fee=params[1]
yearly_custody_fee=params[2]
strategy = globals().get(params[3])
ticker = params[4]
real_period = params[5]
sim_period = params[6]
precompute_strings = [name.strip() for name in params[7].split(",") if name.strip()]
precompute = [globals().get(func_name) for func_name in precompute_strings]

# --- Simulation ---
real_data = get_real_data(ticker, real_period)

real_result = run_strategy_loop(real_data, strategy, capital, transaction_fee, yearly_custody_fee, precompute)

sim_data = get_simulated_data(ticker, sim_period, 20, True)
sim_results = []
for path in sim_data:
    df_path = pd.DataFrame({'Close': path})
    result = run_strategy_loop(df_path, strategy, capital, transaction_fee, yearly_custody_fee, precompute)
    sim_results.append(result)

# --- Evaluation ---
fig, axs = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Strategy Evaluation Report", fontsize=16)

ticks = range(len(real_result["price"]))

# --- Price Plot ---
axs[0, 0].plot(real_result["price"], label="Real Price", color="black", linewidth=2)
for path in sim_results:
    axs[0, 0].plot(path["price"], color='gray', alpha=0.3)
axs[0, 0].set_title("Price Over Time")
axs[0, 0].set_ylabel("Price ($)")
axs[0, 0].grid(True)
axs[0, 0].legend()

# --- Net Worth Plot ---
real_wealth = real_result["wealth"]
sim_wealth = np.array([path["wealth"] for path in sim_results])

for path in sim_wealth:
    axs[0, 1].plot(path, color='skyblue', alpha=0.3)
axs[0, 1].plot(real_wealth, label="Real Net Worth", color="blue", linewidth=2)

axs[0, 1].set_title("Net Worth Over Time")
axs[0, 1].set_ylabel("Net Worth ($)")
axs[0, 1].grid(True)
axs[0, 1].legend()

# --- Capital Plot ---
axs[1, 0].plot(real_result["capital"], label="Real Capital", color="green", linewidth=2)
axs[1, 0].set_title("Capital Over Time")
axs[1, 0].set_ylabel("Capital ($)")
axs[1, 0].grid(True)
axs[1, 0].legend()
# --- Summary Statistics ---
end_wealth = [path["wealth"][-1] for path in sim_results]
summary_text = (
    f"Strategy Summary:\n"
    f"Initial Capital: ${real_result['capital'][0]:.2f}\n"
    f"Final Real Net Worth: ${real_result['wealth'][-1]:.2f}\n\n"
    f"Simulated Net Worths:\n"
    f"• Mean: ${np.mean(end_wealth):.2f}\n"
    f"• Std Dev: ${np.std(end_wealth):.2f}\n"
    f"• Min: ${np.min(end_wealth):.2f}\n"
    f"• Max: ${np.max(end_wealth):.2f}"
)
axs[1, 1].axis("off")
axs[1, 1].text(0, 1, summary_text, fontsize=12, va="top", ha="left", family="monospace")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()