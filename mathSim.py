import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
from scipy.stats import wasserstein_distance
from collections import Counter

def simulate_stock_paths(ticker, num_paths, path_length, period, verbose):
    """
    Simulate stochastic volatility paths for a stock using best-fit parameters from grid search.
    
    Returns:
        simulated_paths, simulated_log_returns, real_log_returns
    """
    # --- Fetch historical data ---
    data = yf.download(ticker, period=period, progress=False)
    if len(data) < 2 * path_length:
        raise ValueError(f"Not enough data ({len(data)} rows) for {path_length}-day simulation. Try a longer period.")
    data['Log_Return'] = np.log(data['Close'] / data['Close'].shift(1))
    data = data.dropna()
    real_log_returns = data['Log_Return']

    # --- Model constants derived from real data ---
    mu = real_log_returns.mean() * 252
    v0 = real_log_returns.var() * 252
    theta = v0
    S0 = 1
    dt = 1 / 252
    N = path_length
    num_simulations = 5  # for parameter tuning

    # --- Parameter grid ---
    kappa_vals = [1, 1.5, 2, 2.5, 3, 5]
    xi_vals = [0.05, 0.1, 0.2, 0.35, 0.4]
    rho_vals = [-0.9, -0.8, -0.7, -0.6, -0.5, 0]

    def simulate_sv(kappa, xi, rho):
        all_log_returns = []
        for _ in range(num_simulations):
            S = np.zeros(N)
            v = np.zeros(N)
            S[0] = S0
            v[0] = v0
            for t in range(1, N):
                z1 = np.random.normal()
                z2 = rho * z1 + np.sqrt(1 - rho**2) * np.random.normal()
                v[t] = np.abs(v[t-1] + kappa * (theta - v[t-1]) * dt + xi * np.sqrt(v[t-1]) * np.sqrt(dt) * z2)
                S[t] = S[t-1] * np.exp((mu - 0.5 * v[t-1]) * dt + np.sqrt(v[t-1]) * np.sqrt(dt) * z1)
            log_ret = np.diff(np.log(S))
            all_log_returns.extend(log_ret)
        return np.array(all_log_returns)

    # --- Run parameter search ---
    num_search_runs = 5  # Number of times to repeat the parameter search
    best_params_list = []

    for _ in range(num_search_runs):
        results = []
        for kappa in kappa_vals:
            for xi in xi_vals:
                for rho in rho_vals:
                    sim_returns = simulate_sv(kappa, xi, rho)
                    dist = wasserstein_distance(real_log_returns[:len(sim_returns)], sim_returns)
                    results.append(((kappa, xi, rho), dist))
        results.sort(key=lambda x: x[1])
        best_params_list.extend([params for params, _ in results[:5]])

    # Find the most frequent best parameter set across all runs
    param_counter = Counter(best_params_list)
    best_params, freq = param_counter.most_common(1)[0]

    if verbose:
        print(f"Most consistent parameter set over {num_search_runs} runs:")
        print(f"Params: {best_params}, Frequency: {freq} times")

        print("\nTop 5 most frequent parameter sets:")
        for params, count in param_counter.most_common(5):
            print(f"Params: {params}, Count: {count}")

    # --- Run final simulation with best parameters ---
    kappa, xi, rho = best_params
    simulated_paths = []
    simulated_log_returns = []

    for _ in range(num_paths):
        S = np.zeros(N)
        v = np.zeros(N)
        S[0] = S0
        v[0] = v0
        for t in range(1, N):
            z1 = np.random.normal()
            z2 = rho * z1 + np.sqrt(1 - rho**2) * np.random.normal()
            v[t] = np.abs(v[t-1] + kappa * (theta - v[t-1]) * dt + xi * np.sqrt(v[t-1]) * np.sqrt(dt) * z2)
            S[t] = S[t-1] * np.exp((mu - 0.5 * v[t-1]) * dt + np.sqrt(v[t-1]) * np.sqrt(dt) * z1)
        simulated_paths.append(S)
        simulated_log_returns.extend(np.diff(np.log(S)))

    return simulated_paths, simulated_log_returns, real_log_returns


def plot_simulation_report(simulated_paths, simulated_log_returns, real_log_returns=None):
    """
    Plot simulated paths and a histogram comparing simulated and real log returns.

    Args:
        simulated_paths (list of np.array): List of simulated price paths.
        simulated_log_returns (list of float): Flattened log returns from simulations.
        real_log_returns (pd.Series, optional): Real log returns for comparison.
    """
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2])

    # Top Left: Simulated Paths
    ax1 = fig.add_subplot(gs[0, :])
    for path in simulated_paths:
        ax1.plot(path, alpha=0.6)
    ax1.set_title('Simulated Stochastic Volatility Paths')
    ax1.set_xlabel('Time (Days)')
    ax1.set_ylabel('Normalized Price')
    ax1.grid(True)

    # Bottom: Histogram of Log Returns
    ax2 = fig.add_subplot(gs[1, :])
    if real_log_returns is not None:
        ax2.hist(real_log_returns, bins=50, alpha=0.6, label='Real Log Returns')
    ax2.hist(simulated_log_returns, bins=50, alpha=0.6, label='Simulated Log Returns')
    ax2.set_title('Histogram of Log Returns')
    ax2.set_xlabel('Log Return')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

def plot_denormalized_paths(denormalized_paths):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    for path in denormalized_paths:
        plt.plot(path, alpha=0.6)
    plt.title("Simulated Price Paths (Denormalized)")
    plt.xlabel("Time (Days)")
    plt.ylabel("Price")
    plt.grid(True)
    plt.show()