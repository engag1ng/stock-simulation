import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

from getData import get_real_data, get_simulated_data
from mathSim import simulate_stock_paths
from strategies import buy_one_sell_one, random_buy_sell

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

# Simulate strategy
capital=10000
transaction_fee=0.01
yearly_custody_fee=0.02
strategy = random_buy_sell
ticker = "^GSPC"
real_period = "10y"
sim_period = "10y"


real_data = get_real_data(ticker, real_period)

real_result = run_strategy_loop(real_data['Close'].values, strategy, capital, transaction_fee, yearly_custody_fee)

sim_data = get_simulated_data(ticker, sim_period, 20, True)
sim_results = []
for path in sim_data:
    result = run_strategy_loop(path, strategy, capital, transaction_fee, yearly_custody_fee)
    sim_results.append(result)

# Evaluate
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